import fitz
from src.agents.agent_all_rules.toolset.dokumen_klaim_validator.reader import (
    DokumenKlaim,
)
from src.agents.agent_all_rules.toolset.dokumen_klaim_validator.rules import rules
from src.agents.agent_all_rules.toolset.dokumen_klaim_validator.evaluator import (
    evaluate,
)
from src.agents.agent_all_rules.toolset.dokumen_klaim_validator.types import (
    HasilEvaluasi,
)
from src.agents.agent_all_rules.evaluator import evaluate_rag
from src.rag import dok_klaim
import json
import datetime
from src.rag import (
    rules as Rule,
    dok_klaim as Dok,
    jenis_dokumen as JenisDok,
)


def cek_kelengkapan_old(pdfpath):
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


def kesimpulan_debug(
    jenis_rawat: str, hasil_validasi: dict[str, Rule.evaluator.HasilEvaluasi]
):
    n_rules_layak = 0
    n_rules_tidak_layak = 0
    details = []

    for rule, hasil in hasil_validasi.items():
        if hasil.status_validasi == "LAYAK":
            n_rules_layak += 1
        else:
            n_rules_tidak_layak += 1

        details.append(
            {
                "rule": rule,
                "saran": hasil.saran,
                "status_validasi": hasil.status_validasi,
            }
        )

    # kalimat kesimpulan
    kesimpulan = {
        "status": "Tidak Layak Klaim" if n_rules_tidak_layak > 0 else "Layak Klaim",
        "stats": {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "jenis_rawat": jenis_rawat,
            "rules_total": n_rules_layak + n_rules_tidak_layak,
            "rules_layak": n_rules_layak,
            "rules_tidak_layak": n_rules_tidak_layak,
        },
        "details": details,
    }

    return json.dumps(kesimpulan, indent=4)


def cek_kelengkapan(pdfpath: str):
    """
    Evaluator menggunakan RAG.
    """
    with fitz.open(pdfpath) as pdf:

        try:
            dok = dok_klaim.reader.DokumenKlaim(pdf)

            if not Dok.retrieval.nosep_exists(dok.nosep):
                dok.cleanup()
                dok.embed()
                print("dok embed done")

            rules = Rule.retrieval.get_rules(dok.jenis_rawat)

            hasil_validasi = Rule.evaluator.evaluate_ruleset(dok.nosep, rules.points)

            # kesimpulan += Rule.evaluator.summary(hasil_validasi).content
            kesimpulan = kesimpulan_debug(dok.jenis_rawat.value, hasil_validasi)

            return kesimpulan

        except ValueError as e:
            print(e)
