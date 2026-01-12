import pymupdf

from qdrant_client import models
from src.rag.config.db import qdrant, DB_DOK_KLAIM
from src.rag.dok_klaim.splitter import chunking


def collection_exists():
    return qdrant.collection_exists(DB_DOK_KLAIM)


def create_collection(recreate: bool = False) -> None:
    if recreate:
        qdrant.delete_collection(DB_DOK_KLAIM)
    elif qdrant.collection_exists(DB_DOK_KLAIM):
        return

    qdrant.create_collection(
        collection_name=DB_DOK_KLAIM,
        vectors_config={
            "dense": models.VectorParams(
                size=1024,
                distance=models.Distance.COSINE,
                # Leave HNSW indexing ON for dense
            ),
            "colbert": models.VectorParams(
                size=128,
                distance=models.Distance.COSINE,
                multivector_config=models.MultiVectorConfig(
                    comparator=models.MultiVectorComparator.MAX_SIM
                ),
                hnsw_config=models.HnswConfigDiff(m=0),  # Disable HNSW for reranking
            ),
        },
        sparse_vectors_config={
            "sparse": models.SparseVectorParams(modifier=models.Modifier.IDF)
        },
        # multitenancy calibrate performance
        hnsw_config=models.HnswConfigDiff(
            payload_m=16,
            m=0,
        ),
    )

    # Index frequently filtered fields
    qdrant.create_payload_index(
        collection_name=DB_DOK_KLAIM,
        field_name="nosep",
        field_schema=models.KeywordIndexParams(
            type=models.KeywordIndexType.KEYWORD,
            is_tenant=True,
        ),
    )
    qdrant.create_payload_index(
        collection_name=DB_DOK_KLAIM,
        field_name="berkas",
        field_schema=models.PayloadSchemaType.KEYWORD,
    )


def sparse_embeddings(q: str):
    return models.Document(text=q, model="Qdrant/bm25")


def dense_embeddings(q: str):
    return models.Document(text=q, model="intfloat/multilingual-e5-large")
    # return models.Document(text=q, model="BAAI/bge-small-en")


def colbert_embeddings(q: str):
    return models.Document(text=q, model="colbert-ir/colbertv2.0")


def berkas_id(berkas: str) -> int:
    return abs(hash(berkas)) % (10**8)


def embed(nosep: str, berkas: str, pages: list[pymupdf.Page]):

    create_collection()

    chunks = chunking(pages)

    dense_chunks = [dense_embeddings(chunk) for chunk in chunks]
    sparse_chunks = [sparse_embeddings(chunk) for chunk in chunks]
    colbert_chunks = [colbert_embeddings(chunk) for chunk in chunks]

    points = []
    for i, c in enumerate(chunks):
        points.append(
            models.PointStruct(
                id=berkas_id(berkas) + i,
                vector={
                    "dense": dense_chunks[i],
                    "sparse": sparse_chunks[i],
                    "colbert": colbert_chunks[i],
                },
                payload={"nosep": nosep, "text": c, "berkas": berkas, "order": i},
            )
        )

    qdrant.upsert(collection_name=DB_DOK_KLAIM, points=points)
    # qdrant.upload_points(collection_name=DB_DOK_KLAIM, points=points, batch_size=8)


def remove_nosep(nosep: str):
    qdrant.delete(
        collection_name=DB_DOK_KLAIM,
        points_selector=models.FilterSelector(
            filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="nosep", match=models.MatchValue(value=nosep)
                    )
                ]
            )
        ),
    )
