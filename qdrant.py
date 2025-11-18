from qdrant_client.models import Distance, VectorParams
from langchain_qdrant import QdrantVectorStore
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document

embeddings = OllamaEmbeddings(model="llama3:latest", url="http://localhost:11434")
url = "http://localhost:6335"
qdrant = QdrantVectorStore.from_existing_collection(
    embeddings=embeddings,
    url=url,
    prefer_grpc=True,
    collection_name="aturan_validasi_klaim",
)

rule1 = {
    "deskripsi": "Kelas perawatan pada dokumen klaim individual pasien harus sama dengan kelas rawat pada dokumen surat eligibilitas peserta",
}

qdrant.add_documents(documents=[rule1])


# operation_info = client.upsert(
#     collection_name="aturan_validasi_klaim",
#     wait=True,
#     points=[
#         PointStruct(id=1, vector=[0.05, 0.61, 0.76, 0.74], payload={"city": "Berlin"}),
#         PointStruct(id=2, vector=[0.19, 0.81, 0.75, 0.11], payload={"city": "London"}),
#         PointStruct(id=3, vector=[0.36, 0.55, 0.47, 0.94], payload={"city": "Moscow"}),
#         PointStruct(id=4, vector=[0.18, 0.01, 0.85, 0.80], payload={"city": "New York"}),
#         PointStruct(id=5, vector=[0.24, 0.18, 0.22, 0.44], payload={"city": "Beijing"}),
#         PointStruct(id=6, vector=[0.35, 0.08, 0.11, 0.44], payload={"city": "Mumbai"}),
#     ],
# )
