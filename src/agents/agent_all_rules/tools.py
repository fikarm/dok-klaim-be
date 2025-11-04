import pprint
from langchain_core.tools import tool
from typing import List
from typing_extensions import TypedDict
from src.agents.agent_all_rules.toolset.dokumen_klaim_validator.main import (
    cek_kelengkapan,
)

# from main_app_rule_exec import cek_kelengkapan


# from src.agents.agent_all_rules.toolset.cek_kelengkapan_berkas_klaim_bpjs_v2 import (
#     cek_kelengkapan_berkas_klaim_bpjs,
# )


class UploadedFile(TypedDict):
    filepath: str


@tool
def cek_kelengkapan_berkas_klaim_bpjs(kumpulan_berkas: List[UploadedFile]):
    """Cek kelengkapan dokumen-dokumen klaim asuransi BPJS Kesehatan"""
    print("tool:cek_kelengkapan_berkas_klaim_bpjs", kumpulan_berkas)

    try:
        if not kumpulan_berkas:
            raise ValueError("tidak ada berkas yang diunggah")

        hasil = ""
        for berkas in kumpulan_berkas:
            hasil += cek_kelengkapan(berkas["filepath"]) + "\n"

        return hasil
    except Exception as e:
        print("error", e)
        return str(e)


@tool(response_format="content_and_artifact")
def retrieve_knowledge(query: str):
    """memastikan bahwa user ingin menanyakan sesuatu dengan dokumen"""
    pass


@tool
def perkalian(a: int, b: int) -> int:
    """Perkalian dua bilangan bulat"""
    print("tool:perkalian")
    return 0


@tool
def sapa():
    """Jawab sapaan dengan sopan"""
    print("tool:sapa")
    return "Jawab sapaan dengan sopan dan tawarkan bantuan untuk cek kelengkapan berkas klaim BPJS Kesehatan"


@tool
def info_umum_dokumen():
    """Menjawab pertanyaan user terkait dokumen yang diunggah selain tentang pengecekan berkas klaim bpjs."""
    print("tool:info_umum_dokumen")
    # TODO: ekstraksi pdf ke teks
    # return "Jika tidak ada tool yang cocok, maka jawab pertanyaan user sesuai pengetahuan yang kamu punya."


@tool
def fallback():
    """Menjawab pertanyaan user sesuai pengetahuan yang kamu punya, hanya jika tidak ada tool yang sesuai."""
    print("tool:fallback")
    # return "Jika tidak ada tool yang cocok, maka jawab pertanyaan user sesuai pengetahuan yang kamu punya."


active_tools = [
    # retrieve_knowledge,
    sapa,
    perkalian,
    # info_umum_dokumen,
    cek_kelengkapan_berkas_klaim_bpjs,
    fallback,
]
