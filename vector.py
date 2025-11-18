import pymupdf
from uuid import uuid4
from langchain_ollama import ChatOllama
from langchain_qdrant import QdrantVectorStore, RetrievalMode, FastEmbedSparse
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama.embeddings import OllamaEmbeddings
from src.agents.agent_rule_evaluator_vector.parser.reader import DokumenKlaim
from src.agents.agent_rule_evaluator_vector.parser.schema import NamaBerkas
from src.agents.agent_rule_evaluator_vector.parser.extractor import extractors
from qdrant_client import QdrantClient, models
from qdrant_client.http.models import Distance, VectorParams


# embedding model
model = "nomic-embed-text"
# model = "llama3.1:8b"
ollama_url = "http://localhost:11434"
vector_embedding = OllamaEmbeddings(base_url=ollama_url, model=model)
sparse_embedding = FastEmbedSparse()

url = "http://localhost:6333"
# collection_name = "aturan_validasi_klaim"
# vectorstore = QdrantVectorStore.from_existing_collection(
#     url=url,
#     embedding=vector_embedding,
#     vector_name="vector",
#     sparse_embedding=sparse_embedding,
#     sparse_vector_name="sparse",
#     collection_name=collection_name,
#     retrieval_mode=RetrievalMode.HYBRID,
#     # retrieval_mode=RetrievalMode.SPARSE,
# )

# # docstore simpan di memory saja
# doc_collection = "dokumen_klaim"
# # client = QdrantClient(":memory:")
# # client.create_collection(
# #     collection_name=doc_collection,
# #     vectors_config=VectorParams(size=768, distance=Distance.COSINE),
# # )
# docstore = QdrantVectorStore.from_existing_collection(
#     # client=client,
#     embedding=vector_embedding,
#     vector_name="vector",
#     sparse_embedding=sparse_embedding,
#     sparse_vector_name="sparse",
#     collection_name=doc_collection,
#     retrieval_mode=RetrievalMode.HYBRID,
# )


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
    # eklaim
    eklaim = NamaBerkas.e_klaim

    # cari rules yang berkaitan dengan klaim
    vectorstore = QdrantVectorStore.from_existing_collection(
        url=url,
        embedding=vector_embedding,
        vector_name="vector",
        sparse_embedding=sparse_embedding,
        sparse_vector_name="sparse",
        collection_name=collection_name,
        retrieval_mode=RetrievalMode.SPARSE,
    )
    rules = vectorstore.similarity_search_with_score(NamaBerkas.e_klaim.value)
    # rawat inap

    # bagaimana cara cari konteks yang tepat berdasarkan rule yang ditemukan?

    ctx = "" "-"

    llm.invoke(
        [
            # {
            #     "role": "system",
            #     "content": "Anda adalah validator klaim BPJS. "
            #     "Anda akan diberikan instruksi bagaimana cara melakukan validasi. "
            #     "Ikuti instruksi tersebut dengan teliti. "
            #     "Gunakan konteks data ini untuk menjalankan instruksi yang diberikan.\n"
            #     f"Konteks: {ctx}\n"
            #     f"Daftar Dokumen yang ditemukan: {list_doc_str}\n",
            # },
            # {"role": "user", "content": "Instruksi:\n" + rule},
            {
                "role": "system",
                "content": ""
                "Anda adalah validator dokumen klaim asuransi BPJS. "
                "Anda akan diberikan instruksi bagaimana cara melakukan validasi. "
                "Gunakan instruksi di bawah ini untuk melakukan validasi. Ikuti satu persatu dengan teliti.\n"
                "- Tanggal masuk pada Dokumen Klaim Individual Pasien (E-Klaim Kemenkes) harus sama dengan tgl. sep pada Dokumen Surat Eligibilitas Peserta (SEP BPJS)\n"
                "- Cara pulang pada Dokumen Klaim Individual Pasien (E-Klaim Kemenkes) harus sama dengan cara pulang pada Dokumen Ringkasan Pasien Pulang Rawat Inap dan Dokumen Surat Keterangan Kematian\n"
                "- Pada Dokumen Klaim Individual Pasien (E-Klaim Kemenkes) jika terdapat kode diagnosa yang diawali dengan huruf S dan T00-T79 maka harus melampirkan Dokumen Jasa Raharja dan Dokumen Surat Pernyataan Kronologis\n\n"
                "Gunakan konteks data ini untuk menjalankan instruksi yang diberikan.\n"
                f"Konteks: {ctx}\n",
            },
            {"role": "user", "content": ""},
        ]
    )


# load_rules()
# sim()
# load_dok()
# validate()

# vectorstore = QdrantVectorStore.from_documents(
#     url=url,
#     embedding=embeddings,
#     collection_name=collection_name,
#     documents=documents,
# )


# docstore.add_documents(documents=[Document("cobi", jenis_dokumen="test")])

# r = docstore.similarity_search_with_score(
#     "Tanggal masuk pada Dokumen Klaim Individual Pasien (E-Klaim Kemenkes) harus sama dengan tgl. sep pada Dokumen Surat Eligibilitas Peserta (SEP BPJS)"
# )
# print(r)

# docstore = QdrantVectorStore.from_existing_collection(
#     # client=client,
#     embedding=vector_embedding,
#     vector_name="vector",
#     sparse_embedding=sparse_embedding,
#     sparse_vector_name="sparse",
#     collection_name=doc_collection,
#     retrieval_mode=RetrievalMode.HYBRID,
#     # retrieval_mode=RetrievalMode.SPARSE,
# )

# client = QdrantClient(url=url)


def list_nama_dokumen(list_aturan: list[str]):

    pass


# docnamestore = QdrantVectorStore.from_documents(
#     # documents=[Document(page_content=b.value) for b in extractors],
#     documents=[Document(page_content="Dokumen " + b.value) for b in extractors],
#     embedding=vector_embedding,
#     sparse_embedding=sparse_embedding,
#     retrieval_mode=RetrievalMode.HYBRID,
#     # location=":memory:",
#     url=url,
#     # collection_name="jenis_dokumen_2",
#     collection_name="jenis_dokumen_hybrid",
# )
docnamestore = QdrantVectorStore.from_existing_collection(
    url=url,
    embedding=vector_embedding,
    sparse_embedding=sparse_embedding,
    retrieval_mode=RetrievalMode.HYBRID,
    collection_name="jenis_dokumen_hybrid",
)


# docnamestore.add_documents([Document(page_content="Dokumen Surat Keterangan Kematian")])

r = docnamestore.similarity_search_with_score(
    # "- Tanggal masuk pada Dokumen Klaim Individual Pasien (E-Klaim Kemenkes) harus sama dengan tgl. sep pada Dokumen Surat Eligibilitas Peserta (SEP BPJS)\n"
    # "- Cara pulang pada Dokumen Klaim Individual Pasien harus sama dengan cara pulang pada Dokumen Ringkasan Pasien Pulang Rawat Inap\n"
    # "- Cara pulang pada Dokumen Klaim Individual Pasien (E-Klaim Kemenkes) harus sama dengan cara pulang pada Dokumen Surat Keterangan Kematian\n",
    # "- Cara pulang pada Dokumen Klaim Individual Pasien harus sama dengan cara pulang pada Dokumen Ringkasan Pasien Pulang Rawat Inap dan Dokumen Surat Keterangan Kematian\n",
    # "- Pada Dokumen Klaim Individual Pasien (E-Klaim Kemenkes) jika terdapat kode diagnosa yang diawali dengan huruf S dan T00-T79 maka harus melampirkan Dokumen Jasa Raharja dan Dokumen Surat Pernyataan Kronologi\n\n",
    # "- Pada Dokumen Klaim Individual Pasien (E-Klaim Kemenkes) jika terdapat kode diagnosa yang diawali dengan huruf S dan T00-T79 maka harus melampirkan Dokumen Surat Pernyataan Kronologi\n\n",
    "- Pada Dokumen Klaim Individual Pasien (E-Klaim Kemenkes) jika terdapat kode diagnosa yang diawali dengan huruf S dan T00-T79 maka harus melampirkan Dokumen Jasa Raharja\n\n",
    # "Dokumen Jasa Raharja",
    k=5,
    # filter=models.Filter(
    #     should=[
    #         models.FieldCondition(
    #             key="metadata.nama_berkas",
    #             match=models.MatchValue(value=NamaBerkas.e_klaim.value),
    #         )
    #     ]
    # ),
    # score_threshold=5,
)
print(r)
