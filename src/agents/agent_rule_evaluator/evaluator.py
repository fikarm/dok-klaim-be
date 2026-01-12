from langchain_core.messages import SystemMessage, HumanMessage
from src.agents.agent_rule_evaluator.llm import init as llm_init
from src.agents.agent_rule_evaluator.types import (
    DaftarNamaBerkasDitemukan,
    HasilEvaluasi,
)
from src.agents.agent_rule_evaluator.reader import DokumenKlaim

# from src.rag.dok_klaim.reader import DokumenKlaim
from src.rag import (
    rules as Rule,
    dok_klaim as Dok,
    jenis_dokumen as JenisDok,
)


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

    # print(berkas_ditemukan)

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
                    f"Cek kelengkapan dokumen klaim asuransi BPJS hanya berdasarkan aturan berikut.\n{rule}"
                ),
            ]
        )
    )

    if isinstance(response, HasilEvaluasi):
        return response


def evaluate_rag(rule: str, dok: Dok.reader.DokumenKlaim) -> Rule.evaluator.HasilEvaluasi | None:

    if not Dok.retrieval.nosep_exists(dok.nosep):
        dok.cleanup()
        dok.embed()
        print("dok embed done")

    print("\n\n\n\n==== Rule ====")
    Rule.evaluator.pprint(rule)

    # cari dokumen terkait dari sebuah rule
    results = JenisDok.retrieval.search(rule)
    print("\n==== Jenis Dokumen ====")
    Rule.retrieval.pprint(results)

    dokumen_terkait = [
        point.payload["text"] for point in results.points if point.payload
    ]

    # cari konteks dokumen terkait
    results = Dok.retrieval.search(dok.nosep, rule, dokumen_terkait)
    print("\n==== Konteks Dokumen ====")
    Dok.retrieval.pprint(results)

    # order urutan dokumen
    # konteks = Dok.retrieval.get_dict(results)
    # print("\n==== Konteks Dokumen ====")
    # print(konteks)

    # evaluasi rule + konteks
    hasil_evaluasi = Rule.evaluator.voting(rule, results)
    print("\n==== Evaluasi ====")
    print(hasil_evaluasi)

    if not hasil_evaluasi:
        raise ValueError(f"Gagal melakukan evaluasi rule: {rule}")

    # dok.cleanup()

    return hasil_evaluasi
