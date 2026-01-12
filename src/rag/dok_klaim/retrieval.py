from src.rag.dok_klaim.embeddings import (
    dense_embeddings,
    sparse_embeddings,
    colbert_embeddings,
)
from qdrant_client import models
from src.rag.config.db import qdrant, DB_DOK_KLAIM
from qdrant_client.conversions.common_types import QueryResponse, ScoredPoint


def hybrid_search_rrf(nosep: str, q: str, list_berkas: list[str]) -> QueryResponse:
    filter_conditions = models.Filter(
        must=[
            models.FieldCondition(key="nosep", match=models.MatchValue(value=nosep)),
            models.FieldCondition(key="berkas", match=models.MatchAny(any=list_berkas)),
        ]
    )

    results = qdrant.query_points(
        collection_name=DB_DOK_KLAIM,
        prefetch=[
            models.Prefetch(query=sparse_embeddings(q), using="sparse"),
            models.Prefetch(query=dense_embeddings(q), using="dense"),
        ],
        query_filter=filter_conditions,
        query=models.FusionQuery(fusion=models.Fusion.RRF),
        with_payload=True,
        score_threshold=0.14,  # 0.34,  # 0.53,  # 0.66,
    )

    return results


def hybrid_search_colbert(nosep: str, q: str, list_berkas: list[str]) -> QueryResponse:
    """
    Reranking Hybrid Search Results with ColBERT.

    Referensi:
    - https://qdrant.tech/documentation/advanced-tutorials/reranking-hybrid-search/
    """

    filter_conditions = models.Filter(
        must=[
            models.FieldCondition(key="nosep", match=models.MatchValue(value=nosep)),
            models.FieldCondition(key="berkas", match=models.MatchAny(any=list_berkas)),
        ]
    )

    results = qdrant.query_points(
        collection_name=DB_DOK_KLAIM,
        prefetch=[
            models.Prefetch(query=sparse_embeddings(q), using="sparse"),
            models.Prefetch(query=dense_embeddings(q), using="dense"),
        ],
        query_filter=filter_conditions,
        query=colbert_embeddings(q),
        using="colbert",
        with_payload=True,
        score_threshold=34.5,  # 41,
    )

    return results


def nosep_exists(nosep: str) -> QueryResponse:
    filter_conditions = models.Filter(
        must=[
            models.FieldCondition(key="nosep", match=models.MatchValue(value=nosep)),
        ]
    )

    results = qdrant.query_points(
        collection_name=DB_DOK_KLAIM,
        query_filter=filter_conditions,
        with_payload=False,
        limit=1,
    )

    return results.points


def pick_n_each(response: QueryResponse, n: int) -> QueryResponse:
    """
    Mengambil sejumlah n dari hasil query similarity dokumen
    untuk tiap jenis dokumen dengan tujuan agar tidak melebihi
    max tokens yang bisa diproses oleh LLM.
    """
    groups: dict[str, int] = {}
    filtered: list[ScoredPoint] = []

    for p in response.points:
        if not p.payload:
            continue

        berkas = p.payload["berkas"]

        if not berkas in groups:
            groups[berkas] = 0

        if groups[berkas] < n:
            groups[berkas] += 1
            filtered.append(p)

    response.points = filtered

    return response


def search(nosep: str, q: str, dokumen_terkait: list[str]):
    # better untuk rules:
    # - Pada Berkas Klaim Individual Pasien (E-Klaim Kemenkes) Jika ada prosedur
    #   dengan kode digit diawali 00-86 maka harus melampirkan Berkas Laporan Operasi
    return hybrid_search_rrf(nosep, q, dokumen_terkait)

    # return hybrid_search_colbert(nosep, q, dokumen_terkait)


def get_dict(results: QueryResponse) -> dict[str, str]:
    """
    Menggabungkan point hasil query Qdrant,
    grouping by nama berkas, kemudian menggabungkan
    isi dokumen sesuai payload order
    """
    # merge by berkas
    konteks: dict[str, list[tuple[str, str]]] = {}
    for p in results.points:
        if not p.payload:
            continue

        berkas = p.payload["berkas"]

        if not berkas in konteks:
            konteks[berkas] = []

        konteks[berkas].append((p.payload["order"], p.payload["text"]))

    # urutkan konteks
    return {k: "\n".join([o[1] for o in sorted(konteks[k])]) for k in konteks}


def pprint(r: QueryResponse):
    for p in r.points:
        if p.payload:
            print(
                "%10s  %s  %s"
                % (
                    p.score,
                    # p.payload["nosep"],
                    p.payload["berkas"][:20] + " ...",
                    p.payload["text"][:75].replace("\n", " ") + " ...",
                )
            )
