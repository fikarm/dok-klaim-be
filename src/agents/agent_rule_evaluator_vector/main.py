import os
import pickle
import faiss
import pymupdf
import numpy as np
from pathlib import Path
from src.core.settings import settings
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama.embeddings import OllamaEmbeddings
from langchain_ollama.chat_models import ChatOllama
from langchain_community.vectorstores import FAISS
from src.agents.agent_rule_evaluator.llm import init as llm_init
from langchain_community.docstore.in_memory import InMemoryDocstore
from src.agents.agent_rule_evaluator_vector.parser.reader import DokumenKlaim
from src.agents.agent_rule_evaluator_vector.parser.extractor import extractors


id_key = "doc_id"
ollama_url = "http://localhost:11434"

# embedding model
# model = "llama3.1:8b"
# model = "gemma3:12b"
# model = "embeddinggemma:300m"
# model = "gpt-oss:latest"
model = "nomic-embed-text"
# model = "qwen3-embedding:8b"
embedding = OllamaEmbeddings(base_url=ollama_url, model=model)

# menyimpan vektor chunk dokumen
index = faiss.IndexFlatL2(len(embedding.embed_query("hello world")))
vectorstore = FAISS(
    embedding_function=embedding,
    index=index,
    docstore=InMemoryDocstore(),
    index_to_docstore_id={},
)

# menyimpan nama dokumen
index2 = faiss.IndexFlatL2(len(embedding.embed_query("hello world")))
docstore = FAISS(
    embedding_function=embedding,
    index=index2,
    docstore=InMemoryDocstore(),
    index_to_docstore_id={},
)


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
            chunk.page_content = f"Ini adalah penggalan informasi dari berkas/dokumen: {d.value}\n{chunk.page_content}"

            chunk.metadata["nama_berkas"] = d.value

        vectorstore.add_documents(documents=chunks)

        print("vectorstore done")


def do_embed_dok(dok: DokumenKlaim):
    # embedding per page
    docs = [Document(page_content=d.value) for d in dok.daftar_isi if d]

    # print(docs)

    return docstore.add_documents(documents=docs)


def sort_similarity_result_by_score(result: list[tuple[Document, float]]):
    scores = [d[1] for d in result]
    sorted_scores = np.argsort(scores)
    sorted_scores = sorted_scores[::-1]  # descending
    sorted_result: list[tuple[Document, float]] = [result[i] for i in sorted_scores]
    return sorted_result


def cek_kelengkapan(pdfpath: str, rule: str):
    with pymupdf.open(pdfpath) as pdf:
        dok = DokumenKlaim(pdf)

        # segmentasi
        do_segmentasi(dok)
        print("segment: done")

        do_embedding(dok)
        print("embed: done")

        do_embed_dok(dok)
        print("embed dok: done")

        # cari nama dukumen yang relevan
        docsim = docstore.similarity_search_with_relevance_scores(rule, k=5)
        docsim = sort_similarity_result_by_score(docsim)

        # ambil daftar nama dokumen
        list_doc = set([d.page_content for [d, score] in docsim])
        list_doc_str = f"\n".join([f"{i}. {d}" for i, d in enumerate(list_doc)])
        print()
        print("---")
        print(list_doc_str)
        print("---")
        print()

        # cari chunk yang relevan
        chunksim = vectorstore.similarity_search_with_relevance_scores(
            rule, k=20, filter={"nama_berkas": {"$in": list_doc}}
        )
        chunksim = sort_similarity_result_by_score(chunksim)

        ctx = "\n\n\n".join(
            [d.metadata["nama_berkas"] for (i, (d, s)) in enumerate(chunksim)]
        )
        print("\n---")
        print(ctx)
        print("---\n")
        ctx = "\n\n\n".join([d.page_content for (i, (d, s)) in enumerate(chunksim)])

        llm = ChatOllama(base_url=ollama_url, model="gemma3:12b")
        ans = llm.invoke(
            [
                {
                    "role": "system",
                    "content": "Anda adalah validator klaim BPJS. "
                    "Anda akan diberikan instruksi bagaimana cara melakukan validasi. "
                    "Ikuti instruksi tersebut dengan teliti. "
                    "Gunakan konteks data ini untuk menjalankan instruksi yang diberikan.\n"
                    f"Konteks: {ctx}\n"
                    f"Daftar Dokumen yang ditemukan: {list_doc_str}\n",
                },
                {"role": "user", "content": "Instruksi:\n" + rule},
            ]
        )

        print()
        print("---")
        ans.pretty_print()
        return ans.content
