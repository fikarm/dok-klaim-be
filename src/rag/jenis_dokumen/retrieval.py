from src.rag import jenis_dokumen
from qdrant_client import models
from src.rag.config.db import qdrant, DB_JENIS_BERKAS
from qdrant_client.conversions.common_types import QueryResponse


def sparse_search(q: str) -> QueryResponse:
    results = qdrant.query_points(
        collection_name=DB_JENIS_BERKAS,
        query=models.Document(text=q, model="Qdrant/bm25"),
        using="sparse",
        with_payload=True,
        score_threshold=8.68,  # 9.18,  # 7.42, # 8.34,
    )

    return results


def indobert_search(q: str) -> QueryResponse:
    results = qdrant.query_points(
        collection_name=DB_JENIS_BERKAS,
        query=jenis_dokumen.embeddings.indobert_dense_embeddings([q])[0],
        using="indobert",
        with_payload=True,
        # score_threshold=0.5,
    )

    return results


def hybrid_search_rrf(q: str) -> QueryResponse:
    """
    Hybrid Search with Reciprocal Rank Fusion
    score_threshold = 0.8
    """
    results = qdrant.query_points(
        collection_name=DB_JENIS_BERKAS,
        prefetch=[
            models.Prefetch(
                query=jenis_dokumen.embeddings.sparse_embeddings(q), using="sparse"
            ),
            models.Prefetch(
                query=jenis_dokumen.embeddings.dense_embeddings(q), using="dense"
            ),
            # models.Prefetch(
            #     query=jenis_dokumen.embeddings.indobert_dense_embeddings([q])[0],
            #     using="indobert",
            # ),
        ],
        query=models.FusionQuery(fusion=models.Fusion.RRF),
        with_payload=True,
        score_threshold=0.42,  # 0.5,
    )

    return results


def hybrid_search_colbert(q: str) -> QueryResponse:
    """
    Reranking Hybrid Search Results with ColBERT.

    Referensi:
    - https://qdrant.tech/documentation/advanced-tutorials/reranking-hybrid-search/
    """
    results = qdrant.query_points(
        collection_name=DB_JENIS_BERKAS,
        prefetch=[
            models.Prefetch(
                query=jenis_dokumen.embeddings.sparse_embeddings(q), using="sparse"
            ),
            models.Prefetch(
                query=jenis_dokumen.embeddings.dense_embeddings(q), using="dense"
            ),
        ],
        query=jenis_dokumen.embeddings.colbert_embeddings(q),
        using="colbert",
        with_payload=True,
        # score_threshold=30,
    )

    return results


def search(q: str) -> QueryResponse:
    """
    Untuk eksekusi rule, lebih sesuai menggunakan sparse vector.
    Dense vector baik dengan reranking hasilnya tidak ada keyword
    berkas yang masuk kedalam top list.
    """
    # return hybrid_search_colbert(q)
    # return hybrid_search_rrf(q)
    # return indobert_search(q)
    return sparse_search(q)
