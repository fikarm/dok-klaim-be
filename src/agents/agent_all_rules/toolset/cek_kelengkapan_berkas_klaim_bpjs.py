import json
import os
import re
import fitz
import pprint
from pymupdf import Document
from psycopg.rows import scalar_row
from langchain_core.tools import tool
from src.agents.agent_all_rules.typings import UploadedFile
from src.agents.agent_all_rules.config.db import pool_simpp
from src.agents.agent_all_rules.api.eklaim import get_claim_data
from types import FunctionType
from typing_extensions import TypedDict


class HasilCek(TypedDict):
    filename: str


@tool
def cek_kelengkapan_berkas_klaim_bpjs(kumpulan_berkas: list[UploadedFile]) -> str:
    """Cek kelengkapan berkas klaim asuransi BPJS Kesehatan"""

    try:
        if not kumpulan_berkas:
            raise ValueError("tidak ada berkas yang diunggah")

        hasil_cek = {}

        for berkas in kumpulan_berkas:
            pdfpath = berkas["filepath"]
            pdfname = os.path.basename(berkas["filepath"])
            hasil_cek[pdfname] = {}

            with fitz.open(pdfpath) as pdf:
                try:
                    page_eklaim = get_eklaim_pages_as_text(pdf)
                    # no_sep = get_eklaim_no_sep(page_eklaim)
                    diagnosa_utama = get_eklaim_diagnosa_utama(page_eklaim)
                    diagnosa_sekunder = get_eklaim_diagnosa_utama(page_eklaim)
                    list_prosedur = get_eklaim_prosedur(page_eklaim)
                    list_icd = list_prosedur + [diagnosa_utama, diagnosa_sekunder]

                    hasil_cek[pdfname]["klasifikasi"] = {
                        "Tindakan operasi": is_tindakan_operasi_by_icd_9(list_prosedur),
                        "Kemoterapi": is_kemoterapi_by_icd(list_icd),
                        # "Tindakan Ventilator",
                        # "Top Up",
                        # "Ibu melahirkan",
                        # "Kasus Jatuh bukan dalam berkendara dan bekerja",
                        # "Kasus kecelakaan tunggal",
                        # "kasus kecelakaan Ganda",
                        # "belum finger",
                    }

                    hasil_cek[pdfname]["kelengkapan"] = {}
                    for kelas in hasil_cek[pdfname]["klasifikasi"]:
                        if hasil_cek[pdfname]["klasifikasi"][kelas]:
                            hasil_cek[pdfname]["kelengkapan"][kelas] = {}
                            for persyaratan in fn_cek_kelengkapan[kelas]:
                                if not fn_cek_kelengkapan[kelas][persyaratan] is None:
                                    hasil_cek[pdfname]["kelengkapan"][kelas][
                                        persyaratan
                                    ] = fn_cek_kelengkapan[kelas][persyaratan](pdf)
                                else:
                                    hasil_cek[pdfname]["kelengkapan"][kelas][
                                        persyaratan
                                    ] = False

                    print(pdfname, hasil_cek[pdfname]["kelengkapan"])

                    # hasil_cek[pdfname]["kelengkapan_dokumen"] = {
                    #     "Tindakan operasi": is_tindakan_operasi_by_icd_9(list_prosedur),
                    #     "Kemoterapi": is_kemoterapi_by_icd(list_icd),
                    #     # "Tindakan Ventilator",
                    #     # "Top Up",
                    #     # "Ibu melahirkan",
                    #     # "Kasus Jatuh bukan dalam berkendara dan bekerja",
                    #     # "Kasus kecelakaan tunggal",
                    #     # "kasus kecelakaan Ganda",
                    #     # "belum finger",
                    # }
                except Exception as e:
                    hasil_cek[pdfname]["kendala"] = str(e)

        # print(hasil_cek)

        return rangkai(hasil_cek)
    except Exception as e:
        print("error", e)
        return str(e)


def read_md(filepath: str) -> str:
    with open(filepath, "r") as f:
        return f.read()


def get_page_eklaim(doc):
    start = None
    end = None

    for page in doc:
        if page.search_for("Berkas Klaim Individual Pasien"):
            start = page.number

        if page.search_for("Generated"):
            matches = re.search(r"Generated[\s\r\n:]+E-Klaim", page.get_text())
            if matches:
                end = page.number

    if start and end:
        return doc[start:end]


def cari_no_sep_pdf(doc):
    search_string = "1301R001"

    for page in doc:
        text_instances = page.search_for(search_string)
        if text_instances:
            pattern = re.compile(r"1301R001\w+")
            words = page.get_text("words")
            for w in words:
                matches = pattern.search(w[4])
                if matches:
                    return matches[0]

    raise ValueError("Kami tidak menemukan nomor SEP dalam dokumen tersebut.")


def is_ada_berkas_laporan_operasi(doc) -> bool:
    for page in doc:
        # mencari awal halaman eklaim berdasarkan judul
        if page.search_for("Nama dan Tanda Tangan Dokter Operator"):
            return True

    return False


def is_ada_berkas_protokol_kemoterapi(doc):
    search_string = "PROTOKOL PEMBERIAN KEMOTERAPI"

    for page in doc:
        if page.search_for(search_string):
            return True

    return False


def cari_no_pendaftaran(md: str):
    matches = re.search(r"No\.\s*Pendaftaran\s*:\n*(\w+)", md)

    if matches:
        return str(matches.group(1))

    raise ValueError("Nomor pendaftaran tidak ditemukan")


def cari_no_sep(md: str):
    matches = re.search(r"1301R001\w+", md)

    if matches:
        return str(matches.group(0))

    raise ValueError("Nomor sep tidak ditemukan")


def cari_diagnosa_utama(md: str):
    matches = re.search(r"Diagnosa Utama\n:\n([\.\w]+)\n", md)

    if matches:
        return str(matches.group(1))


def get_pendaftaran_id(no_pendaftaran: str):
    with pool_simpp.connection() as conn:
        with conn.cursor(row_factory=scalar_row) as cur:
            cur.execute(
                """
                SELECT      pendaftaran_id
                FROM        pendaftaran_t pt
                WHERE       pt.no_pendaftaran = %s
                """,
                [no_pendaftaran],
            )
            return str(cur.fetchone())


def get_list_kode_icd_9(pendaftaran_id: str):
    with pool_simpp.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT      diagnosaix_kode,
                            diagnosaix_nama
                FROM        diagnosaix_inacbg_t
                WHERE       pendaftaran_id = %s
                ORDER BY    diagnosaix_inacbg_id DESC
                """,
                [pendaftaran_id],
            )
            return cur.fetchall()


def is_tindakan_operasi(md: str) -> bool:
    keyword = "Tindakan Medis Operatif\n\n: tidak ada"
    return keyword in md


def is_kemoterapi(list_icd_9: list[tuple[str, str]]) -> bool:
    for kode, nama in list_icd_9:
        if kode == "99.25":
            return True
    return False


def is_tindakan_operasi_by_icd_9(list_icd_9: list[str]) -> bool:
    for icd9 in list_icd_9:
        code = int(icd9.split(".")[0])
        if code >= 1 and code <= 86:
            return True

    return False


def is_kemoterapi_by_icd(list_icd: list[str]) -> bool:

    for kode in list_icd:
        if kode == "99.25" or kode == "Z51.1":
            return True

    return False


def get_eklaim_pages_as_text(doc):
    """
    Mencari halaman e-klaim yang digenerate oleh aplikasi e-klaim milik Kemenkes.
    Support ekstraksi lintas halaman.
    """

    start = None
    end = None

    for page in doc:
        # mencari awal halaman eklaim berdasarkan judul
        if page.search_for("Berkas Klaim Individual Pasien"):
            start = page.number

        # mencari akhir halaman eklaim berdasarkan kata kunci generated
        if page.search_for("Generated"):
            # pastikan kata generated diikuti kata eklaim
            if re.search(
                r"Generated[\s\r\n:]+E-Klaim [\w\.\s@\-:]+\n", page.get_text()
            ):
                end = page.number

    if not start is None and not end is None:
        return "\n".join([page.get_text() for page in doc[start : end + 1]])

    raise ValueError("Tidak ditemukan berkas E-Klaim dari Kemenkes.")


def get_eklaim_no_sep(eklaim: str):
    matches = re.search(r"Nomor SEP[\s\r\n:]+(\w+)", eklaim)

    if matches:
        return str(matches.group(1))

    raise ValueError("Kami tidak menemukan nomor sep pada berkas tersebut.")


def get_eklaim_diagnosa_utama(eklaim: str):
    matches = re.search(r"Diagnosa Utama[\s\r\n:]+(\w+)", eklaim)

    if matches:
        return str(matches.group(1))

    raise ValueError("Kami tidak menemukan data diagnosa utama pada berkas tersebut.")


def get_eklaim_diagnosa_sekunder(eklaim: str):
    matches = re.search(r"Diagnosa Sekunder[\s\r\n:]+(\w+)", eklaim)

    if matches:
        return str(matches.group(1))

    raise ValueError(
        "Kami tidak menemukan data diagnosa sekunder pada berkas tersebut."
    )


def get_eklaim_prosedur(eklaim: str):
    matches = re.search(r"Prosedur([\w\W]+)ADL Sub Acute", eklaim)

    if matches:
        return re.sub(r"[^\d\.]", " ", matches.group(1)).split()

    raise ValueError(
        "Kami tidak menemukan data diagnosa sekunder pada berkas tersebut."
    )


def rangkai(hasil_cek):
    rangkai = ""

    with open(
        "/home/administrator/projects/rag-dok-klaim/docs/dokumen_yang_diperlukan_per_kasus.md",
        "r",
    ) as f:
        rangkai = f.read() + "\n"

    rangkai += (
        f"Berikut adalah berkas-berkas yang diunggah user:\n"
        + "\n".join([f"- {berkas}" for berkas in hasil_cek])
        + "\n"
    )

    rangkai += "\nBerikut adalah hasil klasifikasi kasus pasien untuk setiap berkas:\n"
    for berkas in hasil_cek:
        if "kendala" in hasil_cek[berkas]:
            continue
        else:
            rangkai += f"- {berkas}\n"
            for kelas in hasil_cek[berkas]["klasifikasi"]:
                if hasil_cek[berkas]["klasifikasi"][kelas]:
                    rangkai += f"  - {kelas}\n"

    rangkai += "\nBerikut adalah hasil cek kelengkapan untuk setiap berkas:\n"
    for berkas in hasil_cek:
        if "kendala" in hasil_cek[berkas]:
            continue
        else:
            rangkai += f"- {berkas}\n"
            for kelas in hasil_cek[berkas]["kelengkapan"]:
                rangkai += f"   - {kelas}\n"
                for syarat in hasil_cek[berkas]["kelengkapan"][kelas]:
                    status = (
                        "ada berkas"
                        if hasil_cek[berkas]["kelengkapan"][kelas][syarat]
                        else "tidak ada berkas"
                    )
                    rangkai += f"      - {syarat}: {status}\n"

    kendala = ""
    for berkas in hasil_cek:
        if "kendala" in hasil_cek[berkas]:
            kendala += f"- {berkas}, kendalanya adalah {hasil_cek[berkas]['kendala']}\n"
    if kendala:
        rangkai += f"\nBerikut adalah berkas-berkas yang tidak bisa di analisis karena mengalami kendala:\n{kendala}"

    rangkai += (
        "\nSebutkan apa saja berkas yang diunggah user. "
        "Kemudian jelaskan dokumen apa saja yang belum lengkap untuk setiap berkas yang diunggah. "
        "Jika ada berkas yang tidak bisa diproses karena ada kendala, maka sebutkan juga. "
        "Kembalikan dalam format markdown. Beri format bold untuk dokumen yang tidak ada berkas."
    )

    return rangkai


fn_cek_kelengkapan = {
    "Tindakan operasi": {
        "laporan operasi": is_ada_berkas_laporan_operasi,
    },
    "Kemoterapi": {
        "protokol pemberian kemoterapi": is_ada_berkas_protokol_kemoterapi,
        "form monitoring": None,
        "efek samping pasien kemoterapi": None,
    },
    "Tindakan Ventilator": {
        "form surat keterangan penggunaan alat bantu pernafasan": None,
    },
    "Top Up": {
        "Barcode": None,
    },
    "Ibu melahirkan": {
        "SHK baik dilakukan maupun tidak": None,
    },
    "Kasus Jatuh bukan dalam berkendara dan bekerja": {
        "surat kronologi": None,
    },
    "Kasus kecelakaan tunggal": {
        "laporan kepolisian": None,
    },
    "kasus kecelakaan Ganda": {
        "Surat Jasa Raharja": None,
    },
    "belum finger": {
        "validasi biometrik": None,
    },
}
