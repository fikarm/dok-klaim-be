from src.rag.jenis_dokumen import retrieval as jenis_dok_retrieval
from src.rag.dok_klaim.segmentation import JenisRawat
from src.rag.rules.embeddings import (
    dense_embeddings,
    sparse_embeddings,
    colbert_embeddings,
)
from qdrant_client import models
from src.rag.config.db import qdrant, DB_RULES
from qdrant_client.conversions.common_types import QueryResponse, ScoredPoint


def hybrid_search(q: str) -> QueryResponse:
    results = qdrant.query_points(
        collection_name=DB_RULES,
        prefetch=[
            models.Prefetch(
                query=sparse_embeddings(q),
                using="jenis_berkas",
                limit=5,
            ),
            models.Prefetch(query=dense_embeddings(q), using="dense", limit=5),
        ],
        query=colbert_embeddings(q),
        using="colbert",
        limit=5,
        with_payload=True,
    )

    return results


def hybrid_search_colbert(q: str, list_berkas: list[str]) -> QueryResponse:
    """
    Reranking Hybrid Search Results with ColBERT.

    Referensi:
    - https://qdrant.tech/documentation/advanced-tutorials/reranking-hybrid-search/
    """

    filter_conditions = models.Filter(
        must=[
            models.FieldCondition(key="berkas", match=models.MatchAny(any=list_berkas)),
        ]
    )

    results = qdrant.query_points(
        collection_name=DB_RULES,
        prefetch=[
            models.Prefetch(query=sparse_embeddings(q), using="sparse"),
            models.Prefetch(query=dense_embeddings(q), using="dense"),
        ],
        query_filter=filter_conditions,
        query=colbert_embeddings(q),
        using="colbert",
        with_payload=True,
        score_threshold=41,
    )

    return results


def get_rules(jenis_rawat: JenisRawat) -> QueryResponse:
    filter_conditions = models.Filter(
        must=[
            models.FieldCondition(
                key="jenis_perawatan", match=models.MatchValue(value=jenis_rawat.value)
            ),
        ]
    )

    results = qdrant.query_points(
        collection_name=DB_RULES,
        query_filter=filter_conditions,
        with_payload=True,
        limit=500,
    )

    return results


def get_dokumen_terkait(rule_point: ScoredPoint) -> list[str] | None:
    if not rule_point.payload:
        return

    if not rule_point.payload["text"]:
        return

    # gunakan hasil pencarian dokumen sebelumnya jika ada
    if rule_point.payload["dokumen_terkait"]:
        print("\n==== Jenis Dokumen ====")
        print(rule_point.payload["dokumen_terkait"])
        return rule_point.payload["dokumen_terkait"]

    results = jenis_dok_retrieval.search(rule_point.payload["text"])
    print("\n==== Jenis Dokumen ====")
    pprint(results)

    dokumen_terkait = [
        point.payload["text"] for point in results.points if point.payload
    ]
    rule_point.payload["dokumen_terkait"] = dokumen_terkait

    # update dokumen terkait di db vector
    qdrant.set_payload(
        collection_name=DB_RULES, payload=rule_point.payload, points=[rule_point.id]
    )

    return dokumen_terkait


def rule_by_text(keyword: str):
    filter_conditions = models.Filter(
        must=[
            models.FieldCondition(key="text", match=models.MatchText(text=keyword)),
        ]
    )

    results = qdrant.query_points(
        collection_name=DB_RULES,
        query_filter=filter_conditions,
        with_payload=True,
        limit=500,
    )

    return results


def pprint(r: QueryResponse):
    for p in r.points:
        if p.payload:
            print(
                "%10s  %s"
                % (
                    p.score,
                    # p.payload["nosep"],
                    p.payload["text"][:75].replace("\n", " ") + " ...",
                )
            )
