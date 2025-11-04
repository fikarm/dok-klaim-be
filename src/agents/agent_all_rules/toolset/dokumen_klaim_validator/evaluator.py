from langchain_core.messages import SystemMessage, HumanMessage
from src.agents.agent_all_rules.toolset.dokumen_klaim_validator.llm import init as llm_init
from src.agents.agent_all_rules.toolset.dokumen_klaim_validator.types import (
    DaftarNamaBerkasDitemukan,
    HasilEvaluasi,
)
from src.agents.agent_all_rules.toolset.dokumen_klaim_validator.reader import DokumenKlaim


def semua_isi_berkas(
    nama_berkas_ditemukan: DaftarNamaBerkasDitemukan, dokklaim: DokumenKlaim
):
    text = ""

    for nama_berkas in nama_berkas_ditemukan.daftar:
        isi_berkas = dokklaim.get_berkas(nama_berkas.nama)
        nama_berkas = nama_berkas.nama.value

        if isi_berkas is None:
            text += f"Dokumen {dokklaim.name} tidak memiliki berkas {nama_berkas}"
        else:
            text += (
                f'## Isi Berkas "{nama_berkas}".\n\n'
                # f'Di bawah ini adalah isi dari berkas "{nama_berkas}".\n'
                f"{isi_berkas}"
                f'\nIni adalah akhir dari berkas "{nama_berkas}".\n\n'
            )

    return text


def cari_nama_berkas(rule: str):
    """
    Menentukan berkas apa saja yang diperlukan
    oleh sebuah aturan dan mengolahnya menjadi
    kalimat konteks.
    """

    structured_llm = llm_init().with_structured_output(DaftarNamaBerkasDitemukan)

    daftar_nama_berkas = structured_llm.invoke(
        [
            SystemMessage(
                "Temukan semua nama berkas yang disebutkan secara eksplisit oleh user."
                "Nama berkas biasanya diawali dengan kata 'Berkas'. "
                "\n\n"
            ),
            HumanMessage(rule),
        ]
    )

    if isinstance(daftar_nama_berkas, DaftarNamaBerkasDitemukan):
        return daftar_nama_berkas


def evaluate(rule: str, dokklaim: DokumenKlaim):
    nama_berkas_ditemukan = cari_nama_berkas(rule)

    if nama_berkas_ditemukan is None:
        raise ValueError(f"Tidak ada nama berkas dalam rule:\n{rule}")

    berkas_ditemukan = semua_isi_berkas(nama_berkas_ditemukan, dokklaim)

    response = (
        llm_init()
        .with_structured_output(HasilEvaluasi)
        .invoke(
            [
                SystemMessage(
                    "Anda adalah verifikator dokumen klaim asuransi BPJS di Rumah Sakit Umum Daerah Dr. Soeteomo (RSDS). "
                    # "Tugas anda adalah memastikan dokumen klaim tersebut lengkap dan konsisten berdasarkan aturan/rule yang disebutkan oleh user. "
                    "Satu dokumen klaim asuransi BPJS bisa terdiri dari banyak berkas."
                    # f"Terdapat sebuah dokumen klaim asuransi BPJS bernama {dokklaim.name}."
                    f"Di bawah ini adalah berkas-berkas yang ada pada dokumen klaim {dokklaim.name}."
                    # "Di bawah ini adalah semua berkas yang ditemukan dalam dokumen klaim bernama  "
                    # f"Di bawah ini adalah daftar isi dari dokumen klaim asuransi BPJS '{dokklaim.name}'.\n"
                    f"{berkas_ditemukan}\n\n"
                ),
                HumanMessage(
                    f"Cek kelengkapan dokumen klaim asuransi BPJS berdasarkan aturan berikut.\n{rule}"
                ),
            ]
        )
    )

    if isinstance(response, HasilEvaluasi):
        return response
