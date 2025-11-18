from qdrant_client import QdrantClient, models


client = QdrantClient(host="localhost")

points = client.scroll("aturan_validasi_klaim")

print(points)
