import os
from pathlib import Path
from qdrant_client import models
from src.rag.dok_klaim.segmentation import JenisRawat
from src.rag.config.db import qdrant, DB_RULES


def collection_exists():
    return qdrant.collection_exists(DB_RULES)


def create_collection(recreate: bool = False) -> None:
    if recreate:
        qdrant.delete_collection(DB_RULES)
    elif collection_exists():
        return

    qdrant.create_collection(
        collection_name=DB_RULES,
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
    )

    # Index frequently filtered fields
    qdrant.create_payload_index(
        collection_name=DB_RULES,
        field_name="jenis_perawatan",
        field_schema=models.PayloadSchemaType.KEYWORD,
    )


def rulespath():
    return Path(os.getcwd(), "src", "rules")


def read_ri():
    with open(rulespath().joinpath("rules_ri.txt"), "r") as f:
        return f.readlines()


def read_rj():
    with open(rulespath().joinpath("rules_rj.txt"), "r") as f:
        return f.readlines()


def sparse_embeddings(q: str):
    return models.Document(text=q, model="Qdrant/bm25")


def dense_embeddings(q: str):
    return models.Document(text=q, model="intfloat/multilingual-e5-large")
    # return models.Document(text=q, model="BAAI/bge-small-en")


def colbert_embeddings(q: str):
    return models.Document(text=q, model="colbert-ir/colbertv2.0")


def berkas_id(berkas: str) -> int:
    return abs(hash(berkas)) % (10**8)


def embed(rules: list[str], jenis_perawatan: str):

    create_collection()

    dense_chunks = [dense_embeddings(rule.strip()) for rule in rules]
    sparse_chunks = [sparse_embeddings(rule.strip()) for rule in rules]
    colbert_chunks = [colbert_embeddings(rule.strip()) for rule in rules]

    points = []
    for i, rule in enumerate(rules):
        points.append(
            models.PointStruct(
                id=berkas_id(rule),
                vector={
                    "dense": dense_chunks[i],
                    "sparse": sparse_chunks[i],
                    "colbert": colbert_chunks[i],
                },
                payload={
                    "dokumen_terkait": [],
                    "jenis_perawatan": jenis_perawatan,
                    "text": rule,
                },
            )
        )

    qdrant.upsert(collection_name=DB_RULES, points=points)
    # qdrant.upload_points(collection_name=DB_DOK_KLAIM, points=points, batch_size=8)


def embed_all_rules():
    embed(read_ri(), JenisRawat.rawat_inap.value)
    embed(read_rj(), JenisRawat.rawat_jalan.value)
