import fitz
from src.agents.agent_all_rules.toolset.dokumen_klaim_validator.reader import DokumenKlaim
from src.agents.agent_all_rules.toolset.dokumen_klaim_validator.rules import rules
from src.agents.agent_all_rules.toolset.dokumen_klaim_validator.evaluator import evaluate
from src.agents.agent_all_rules.toolset.dokumen_klaim_validator.types import HasilEvaluasi


def cek_kelengkapan(pdfpath):
    with fitz.open(pdfpath) as pdf:
        dokklaim = DokumenKlaim(pdf)

        invalids = []
        for i, rule in enumerate(rules[dokklaim.jenis_rawat]):
            hasil_evaluasi = evaluate(rule, dokklaim)

            if isinstance(hasil_evaluasi, HasilEvaluasi):
                print("\n# Alasan")
                print(hasil_evaluasi.alasan)
                print("\n# Status")
                print(hasil_evaluasi.status)
                print("\n# Saran")
                print(hasil_evaluasi.saran)

            if hasil_evaluasi and not hasil_evaluasi.status:
                invalids.append(
                    {
                        "rule": rule,
                        "alasan": hasil_evaluasi.alasan,
                        "saran": hasil_evaluasi.saran,
                    }
                )

        if len(invalids):
            # refrasa
            return (
                f"Dokumen klaim asuransi BPJS {dokklaim.name} belum lengkap dan konsisten. "
                "Berikut ini adalah daftar aturan yang belum terpenuhi beserta alasan dan saran.\n"
                + "\n".join(
                    [
                        f"{i + 1}. Aturan: {rule['rule']}\n"
                        f"Alasan: Belum terpenuhi karena {rule['alasan']}.\n"
                        f"Saran: {rule['saran']}\n"
                        for i, rule in enumerate(invalids)
                    ]
                )
            )

        return f"Berdasarkan aturan yang diberikan, dokumen klaim asuransi BPJS {dokklaim.name} sudah lengkap dan konsisten."
