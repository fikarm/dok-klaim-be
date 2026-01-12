from qdrant_client import models
from src.rag.config import db, ollama
from src.rag.jenis_dokumen.models import NamaBerkas
from sentence_transformers import SentenceTransformer


def collection_exists():
    return db.qdrant.collection_exists(db.DB_JENIS_BERKAS)


def create_collection(recreate: bool = False) -> None:
    """
    Hybrid Search with Reciprocal Rank Fusion
    Sumber: https://db.qdrant.tech/course/essentials/day-3/hybrid-search-demo/
    """
    if recreate:
        db.qdrant.delete_collection(db.DB_JENIS_BERKAS)
    elif collection_exists():
        return

    db.qdrant.create_collection(
        collection_name=db.DB_JENIS_BERKAS,
        vectors_config={
            "dense": models.VectorParams(
                size=1024,
                # size=768,
                # size=384,
                distance=models.Distance.COSINE,
                # Leave HNSW indexing ON for dense
            ),
            "indobert": models.VectorParams(
                size=768,
                distance=models.Distance.COSINE,
                # Leave HNSW indexing ON for dense
            ),
            # bisa diaktifkan jika ingin rerank menggunakan colbert
            "colbert": models.VectorParams(
                size=128,  # TODO:
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
    )


def sparse_embeddings(q: str):
    return models.Document(text=q, model="Qdrant/bm25")


def indobert_dense_embeddings(q: list[str]):
    model = SentenceTransformer("indolem/indobert-base-uncased")
    return model.encode(q).tolist()


def dense_embeddings(q: str):
    return models.Document(
        text=q, model="intfloat/multilingual-e5-large"
    )  # 1024 # kurang akurat
    # return models.Document(text=q, model="BAAI/bge-small-en") # 384


def colbert_embeddings(q: str):
    return models.Document(text=q, model="colbert-ir/colbertv2.0")


def berkas_id(berkas: str) -> int:
    return abs(hash(berkas)) % (10**8)


def embed(daftar_jenis_berkas: list[str]):

    create_collection()

    points = []

    tensors = indobert_dense_embeddings(daftar_jenis_berkas)

    for i, jenis_berkas in enumerate(daftar_jenis_berkas):
        point = models.PointStruct(
            id=berkas_id(jenis_berkas),
            vector={
                "sparse": sparse_embeddings(jenis_berkas),
                "dense": dense_embeddings(jenis_berkas),
                "indobert": tensors[i],
                # bisa diaktifkan jika ingin rerank menggunakan colbert
                "colbert": colbert_embeddings(jenis_berkas),
            },
            payload={"text": jenis_berkas},
        )
        points.append(point)

    db.qdrant.upsert(collection_name=db.DB_JENIS_BERKAS, points=points)

    # db.qdrant.upload_points(collection_name=DB_JENIS_BERKAS, points=points, batch_size=8)


def embed_jenis_dokumen():
    embed([b.value for b in NamaBerkas])
