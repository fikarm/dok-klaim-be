import pymupdf
from uuid import uuid4
from langchain_ollama import ChatOllama
from langchain_qdrant import QdrantVectorStore, RetrievalMode, FastEmbedSparse
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama.embeddings import OllamaEmbeddings
from src.agents.agent_rule_evaluator_vector.parser.reader import DokumenKlaim
from src.agents.agent_rule_evaluator_vector.parser.extractor import extractors
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams


# embedding model
model = "nomic-embed-text"
ollama_url = "http://localhost:11434"
vector_embedding = OllamaEmbeddings(base_url=ollama_url, model=model)
sparse_embedding = FastEmbedSparse()

url = "http://localhost:6333"
collection_name = "aturan_validasi_klaim"
vectorstore = QdrantVectorStore.from_existing_collection(
    url=url,
    embedding=vector_embedding,
    vector_name="vector",
    sparse_embedding=sparse_embedding,
    sparse_vector_name="sparse",
    collection_name=collection_name,
    # retrieval_mode=RetrievalMode.HYBRID,
    retrieval_mode=RetrievalMode.SPARSE,
)

# docstore simpan di memory saja
doc_collection = "dokumen_klaim"
# client = QdrantClient(":memory:")
# client.create_collection(
#     collection_name=doc_collection,
#     vectors_config=VectorParams(size=768, distance=Distance.COSINE),
# )
docstore = QdrantVectorStore.from_existing_collection(
    # client=client,
    embedding=vector_embedding,
    vector_name="vector",
    sparse_embedding=sparse_embedding,
    sparse_vector_name="sparse",
    collection_name=collection_name,
    retrieval_mode=RetrievalMode.HYBRID,
)


llm = ChatOllama(model="gemma3:12b", base_url=ollama_url)


def load_rules():
    with open("/home/itki/projects/dok-klaim/dok-klaim-be/assets/rules.txt", "r") as f:
        i = 0
        for line in f:
            doc = Document(page_content=line.strip())
            vectorstore.add_documents(documents=[doc], ids=[i])
            i += 1


def sim():
    r = vectorstore.similarity_search_with_score("klaim individual pasien", k=100)
    print(r)
    return r


def do_segmentasi(dok: DokumenKlaim):
    for nama in extractors:
        dok.get_berkas(nama)


def do_chunking_token(content: str):
    splitter = RecursiveCharacterTextSplitter(
        separators=["\n", " "], chunk_size=200, chunk_overlap=100
    )

    return splitter.create_documents([content])


def do_embedding(dok: DokumenKlaim):
    for no, d in enumerate(dok.daftar_isi):
        if not d:
            continue

        pagetext = dok.pdf[no].get_text()
        if type(pagetext) is not str:
            continue

        chunks = do_chunking_token(pagetext)

        for chunk in chunks:
            # chunk.page_content = f"Ini adalah penggalan informasi dari berkas/dokumen: {d.value}\n{chunk.page_content}"
            chunk.page_content = chunk.page_content

            chunk.metadata["nama_berkas"] = d.value

        docstore.add_documents(documents=chunks)

        print("docstore done")


def do_embed_dok(dok: DokumenKlaim):
    # embedding per page
    docs = [Document(page_content=d.value) for d in dok.daftar_isi if d]

    # print(docs)

    return docstore.add_documents(documents=docs)


def load_dok():
    print("masuk")
    pdfpath = "/home/itki/projects/dok-klaim/dok-klaim-be/tmp/0a5405a6-94b7-4067-8139-d235374c4cd2/1301R0011125V012544_pdf lengkap.pdf"
    with pymupdf.open(pdfpath) as pdf:
        dok = DokumenKlaim(pdf)
        # segmentasi
        do_segmentasi(dok)
        print("segment: done")

        do_embedding(dok)
        print("embed: done")

        # do_embed_dok(dok)
        # print("embed dok: done")

        # cari nama dukumen yang relevan
        # docsim = docstore.similarity_search_with_relevance_scores(rule, k=5)
        # docsim = sort_similarity_result_by_score(docsim)
        return dok


def validate():

    llm.invoke([{"role": "system", "text": ""}, {"role": "user", "text": ""}])


# load_rules()
# sim()
load_dok()

# vectorstore = QdrantVectorStore.from_documents(
#     url=url,
#     embedding=embeddings,
#     collection_name=collection_name,
#     documents=documents,
# )


# docstore.add_documents(documents=[Document("cobi", jenis_dokumen="test")])
