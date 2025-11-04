import fitz
from src.agents.agent_rule_evaluator.reader import DokumenKlaim
from src.agents.agent_rule_evaluator.evaluator import evaluate


def cek_kelengkapan(pdfpath: str, rule: str):
    with fitz.open(pdfpath) as pdf:
        dokklaim = DokumenKlaim(pdf)

        hasil_evaluasi = evaluate(rule, dokklaim)

        # print(dokklaim.daftar_isi)

        if hasil_evaluasi:
            status = "Dokumen Valid" if hasil_evaluasi.status else "Dokumen Belum Valid"
            return (
                "##### Status\n"
                f"{status}\n"
                "##### Alasan\n"
                f"{hasil_evaluasi.alasan}\n"
                "##### Saran\n"
                f"{hasil_evaluasi.saran}\n"
            )
