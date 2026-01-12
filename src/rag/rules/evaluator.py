from pprint import pprint
from pydantic import BaseModel, Field
from src.rag.rules import retrieval as rules_retrieval
from src.rag.dok_klaim import retrieval as dok_retrieval
from src.rag.config.llm import llm_init
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from qdrant_client.conversions.common_types import QueryResponse, ScoredPoint


class HasilEvaluasi(BaseModel):
    status_validasi: str  # Literal["LAYAK", "TIDAK LAYAK"]
    saran: str = Field(description="Apa yang harus dilakukan jika tidak lengkap")


def parse(answer: str) -> HasilEvaluasi:
    # remove thinking parts untuk model seperti qwen3
    try:
        token = "</think>\n"
        answer = answer[answer.index(token) + len(token) :]
    except:
        pass

    parts = answer.split(":")
    status_validasi = parts[1].strip()
    status_validasi = status_validasi[: status_validasi.index("\n")].strip()
    saran = "".join(parts[2:]).strip()
    return HasilEvaluasi(status_validasi=status_validasi, saran=saran)


def evaluasi(rule: str, daftar_dokumen: dict[str, str]) -> HasilEvaluasi | None:
    konteks = "\n\n\n".join(
        [
            f"### Sebagian Isi Dokumen {dok}\n\n{isi.strip()}"
            for dok, isi in daftar_dokumen.items()
        ]
    )

    daftar_isi = "\n".join([f"{(i+1)}. {b}" for i, b in enumerate(daftar_dokumen)])

    sys_prompt = (
        "## PERAN\n\n"
        "Anda adalah seorang Auditor Medik Spesialis Klaim Asuransi JKN"
        " pada rumah sakit RSUD Dr. Soetomo Surabaya"
        " yang bertugas melakukan verifikasi DOKUMEN KLAIM"
        " berdasarkan ATURAN VALIDASI UTAMA. "
        " Gunakan DAFTAR DOKUMEN KLAIM TERLAMPIR dan SEBAGIAN ISI DOKUMEN KLAIM sebagai konteks"
        " tanpa perlu tahu isi keseluruhan DOKUMEN KLAIM.\n"
        "\n\n"
        "## ATURAN VALIDASI UTAMA\n\n"
        f"{rule}\n"
        "\n\n"
        f"## DAFTAR DOKUMEN KLAIM TERLAMPIR\n\n"
        f"{daftar_isi}\n"
        "\n\n"
        f"## SEBAGIAN ISI DOKUMEN KLAIM\n\n"
        f"{konteks}\n"
        "\n\n"
        "## FORMAT OUTPUT YANG DIHARAPKAN\n\n"
        "Berikan jawaban dalam format berikut:\n\n"
        "1. **Status Validasi**: [LAYAK / TIDAK LAYAK]\n"
        "2. **Saran**: [Apa yang harus dilakukan jika tidak lengkap]\n"
    )

    # print("\n==== PROMPT ====")
    # print(sys_prompt)

    r = (
        llm_init()
        # .with_structured_output(HasilEvaluasi) # dinonaktifkan karena respons kadang tidak sesuai harapan
        .invoke(
            [
                SystemMessage(sys_prompt),
                HumanMessage("Cek kelengkapan dokumen klaim"),
            ]
        )
    )

    # print("\n==== RESPONS ====")
    # print(r.pretty_print())

    return parse(str(r.content))


def voting(rule: str, daftar_dokumen: QueryResponse) -> HasilEvaluasi | None:
    """
    Running evaluasi beberapa kali
    """

    # urutkan dokumen
    konteks = dok_retrieval.get_dict(daftar_dokumen)
    # print("\n==== Konteks Dokumen ====")
    # pprint(konteks)

    # loop
    layak = []
    tidak_layak = []
    i = 0
    while abs(len(layak) - len(tidak_layak)) < 2:
        hasil = evaluasi(rule, konteks)

        if hasil and hasil.status_validasi == "LAYAK":
            layak.append(hasil)
        elif hasil and hasil.status_validasi != "TIDAK LAYAK":
            # bisa jadi case melebihi max tokens dari LLM.
            # contoh case: `1301R0011125V030170`
            # maka coba lagi dengan mengurangi hasil retrieval dokumen
            konteks = dok_retrieval.get_dict(
                dok_retrieval.pick_n_each(daftar_dokumen, 3)
            )
            print("\n\n\n>>> [ MELEBIHI MAX TOKEN ] <<<\n\n\n")
        else:
            tidak_layak.append(hasil)

        print(
            ">>> PERCOBAAN:",
            i + 1,
            "SELISIH:",
            abs(len(layak) - len(tidak_layak)),
            "<<<",
        )
        i += 1

    if len(layak) > len(tidak_layak):
        return layak[-1]
    else:
        return tidak_layak[-1]


def evaluate_ruleset(nosep: str, ruleset: list[ScoredPoint]):
    validation_results: dict[str, HasilEvaluasi] = {}

    for rule_point in ruleset:
        if not rule_point.payload:
            continue

        rule = rule_point.payload["text"]
        print("\n\n\n\n==== Rule ====")
        pprint(rule)

        # cari dokumen terkait dari sebuah rule
        dokumen_terkait = rules_retrieval.get_dokumen_terkait(rule_point)
        if not dokumen_terkait:
            continue

        # cari konteks dokumen terkait
        konteks = dok_retrieval.search(nosep, rule, dokumen_terkait)
        # print("\n==== Konteks Dokumen ====")
        # dok_retrieval.pprint(konteks)

        # evaluasi rule + konteks
        hasil_evaluasi = voting(rule, konteks)
        print("\n==== Evaluasi ====")
        pprint(hasil_evaluasi)

        if not hasil_evaluasi:
            raise ValueError(f"Gagal melakukan evaluasi rule: {rule}")

        validation_results[rule] = hasil_evaluasi

    return validation_results


def summary(hasil_eval: dict[str, HasilEvaluasi]) -> AIMessage:

    aturan_tidak_lolos = "\n".join(
        [
            "- " + hasil.saran + ". Aturan terkait: " + rule
            for rule, hasil in hasil_eval.items()
            if hasil.status_validasi != "LAYAK"
        ]
    )

    sys_prompt = (
        "## PERAN\n"
        "Anda adalah seorang Auditor Medik Spesialis Klaim Asuransi JKN"
        " yang bertugas menentukan kelengkapan berkas administrasi klaim"
        " rumah sakit RSUD Dr. Soetomo Surabaya berdasarkan HASIL VERIFIKASI di bawah ini.\n"
        "\n\n"
        "## HASIL VERIFIKASI\n\n"
        f"{aturan_tidak_lolos if aturan_tidak_lolos else 'Dokumen klaim lengkap berdasarkan aturan yang diberikan.'}"
    )

    print("\n==== SUMMARY ====")
    print(sys_prompt)

    r = llm_init().invoke(
        [
            SystemMessage(sys_prompt),
            HumanMessage("Cek kelengkapan berkas administrasi klaim"),
        ]
    )

    return r
