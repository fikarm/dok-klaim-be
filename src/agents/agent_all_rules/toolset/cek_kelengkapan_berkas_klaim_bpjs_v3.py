import os
import fitz
from src.agents.agent_all_rules.typings import UploadedFile
from langchain_ollama import ChatOllama
from typing_extensions import TypedDict, Literal
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage
from src.agents.agent_all_rules.pdf_extractor import (
    eklaim_pages_as_text,
    sep_bpjs_rsds_as_text,
    form_rawat_inap_rsds_as_text,
    ringkasan_pasien_pulang_rawat_inap_as_text,
)
from pydantic import BaseModel, Field


class Aturan(TypedDict):
    aturan: str
    hasil_validasi: Literal["valid", "tidak valid"]
    alasan: str


class HasilValidasiDokumen(BaseModel):
    nama_dokumen: str = Field(
        description="nama dokumen klaim asuransi BPJS yang diunggah oleh user. Contoh: 1301R0010825V044650.pdf."
    )
    daftar_isi_dokumen: list[str] = Field(
        description="daftar isi dokumen klaim asuransi BPJS yang diunggah user."
    )
    daftar_hasil_validasi_berdasarkan_aturan: list[Aturan] = Field(
        description="daftar isi dokumen klaim asuransi BPJS yang diunggah user."
    )
    kesimpulan: str


def generate_system_message(pdf):
    # nampaknya terlalu panjang kalau dimasukkan ke prompt semua
    isi_dokumen = {
        "Berkas Klaim Individual Pasien (E-Klaim Kemenkes)": {
            "isi": eklaim_pages_as_text(pdf),
            "keterangan": ""
            "Diagnosa Utama pada berkas klaim individual pasien ditulis dalam format ICD-10.\n"
            "Diagnosa Sekunder pada berkas klaim individual pasien ditulis ditulis dalam format ICD-10.\n"
            "Prosedur pada berkas klaim individual pasien ditulis dalam format ICD-9.\n"
            "LOS (length of stay) pada berkas klaim individual pasien ditulis dalam satuan hari.\n"
            "Special CMG pada berkas klaim individual pasien diikuti dengan besaran tarif/biaya dalam satuan Rupiah (Rp)",
        },
        "Surat Eligibilitas Peserta BPJS (SEP BPJS)": {
            "isi": sep_bpjs_rsds_as_text(pdf),
            "keterangan": "",
        },
        "Form Rawat Inap RSDS": {
            "isi": form_rawat_inap_rsds_as_text(pdf),
            "keterangan": "",
        },
        "Ringkasan Pasien Pulang Rawat Inap": {
            "isi": ringkasan_pasien_pulang_rawat_inap_as_text(pdf),
            "keterangan": "",
        },
    }

    # group pengecekan
    # eklaim + rule + output
    groups = [
        {
            "dokumen": {
                "Berkas Klaim Individual Pasien (E-Klaim Kemenkes)": isi_dokumen[
                    "Berkas Klaim Individual Pasien (E-Klaim Kemenkes)"
                ],
                "Surat Eligibilitas Peserta BPJS (SEP BPJS)": isi_dokumen[
                    "Surat Eligibilitas Peserta BPJS (SEP BPJS)"
                ],
            },
            "rules": [],
        }
    ]

    # sepertinya melebihi panjang konteks
    # perlu cari cara

    print(isi_dokumen)

    rules_ri = [
        "Kelas perawatan pada Berkas Klaim Individual Pasien harus sama dengan Kls. Rawat Pada berkas SEP BPJS",
        "Kelas perawatan pada Berkas Klaim Individual Pasien harus sama dengan Hak Kelas Perawatan pada berkas Sep Form Rawat Inap",
        "Tanggal masuk pada Berkas Klaim Individual Pasien harus sama dengan tgl. SEP pada berkas SEP BPJS",
        "Cara pulang pada Berkas Klaim Individual Pasien harus sama dengan cara pulang pada Ringkasan Pasien Pulang Rawat Inap.\n"  # TODO: Atas Persetujuan Dokter?
        # "Bisa dilihat pada keadaan Waktu Keluar Rumah Sakit (Keadaan KRS). Misal cara pulang kedua berkas tersebut adalah Atas Persetujuan Dokter, artinya data sudah sesuai.",
        # "Cara pulang pada Berkas Klaim Individual Pasien harus sama dengan cara pulang pada Ringkasan Surat Keterangan Kematian (jika pasien sudah meninggal)", # TODO: perlu contoh pdf
        "Pada Berkas Klaim Individual Pasien jika terdapat kode diagnosa ICD-10 yang diawali dengan huruf S dan T00-T79 maka harus ada berkas Jasa Raharja",  # TODO: contoh pdf
        "Pada Berkas Klaim Individual Pasien jika terdapat kode diagnosa ICD-10 yang diawali dengan huruf S dan T00-T79 maka harus ada berkas Surat Pernyataan Kronologis",  # TODO: contoh pdf
        "Pada Berkas Klaim Individual Pasien jika INA-CBG berbunyi Kemoterapi maka wajib melampirkan Protokol Pemberian Kemoterapi"
        "Pada Berkas Klaim Individual Pasien jika INA-CBG berbunyi Kemoterapi maka wajib melampirkan Monitoring dan Efek Samping Pasien Kemoterapi",
        'Pada Berkas Klaim Individual Pasien jika LOS (Length of Stay) hanya 3 hari maka pada Berkas Klaim Individual Pasien tidak boleh ada kata "berat" (terkecuali pasien meninggal)',
        "Pada Berkas Klaim Individual Pasien jika Diagnosa Utama terdapat kode Z51.1 dan LOS lebih dari 5 hari maka perlu dilakukan reseleksi diagnosa utama",
        "Pada Berkas Klaim Individual Pasien jika ada prosedur ICD-9 dengan kode digit diawali 00-86 maka harus melampirkan Laporan Operasi",
        "Pada Berkas Klaim Individual Pasien jika ada prosedur ICD-9: 96.71, 96.72, 93.90, dan 93.960, maka harus ada Surat Keterangan Penggunaan Alat Bantu Pernafasan",
        "Pada Berkas Klaim Individual Pasien jika Special CMG muncul tarif (tidak Rp 0.00) maka wajib ada berkas berkas resep obat/alkes",
        "Pada Berkas Klaim Individual Pasien jika Diagnosa Sekunder terdapat kode O80-O84 maka harus ada berkas berkas Surat Keterangan Telah Dilakukan Pengambilan Sampel Skrining Hipotiroid Kongenital dan Surat Keterangan Lahir (melahirkan di RSDS)",
        "Pada Berkas Klaim Individual Pasien jika Diagnosa Sekunder terdapat kode Z38.0 maka harus ada berkas Surat Keterangan Lahir (lahir di RSDS)",
        # 'Pada Berkas Klaim Individual Pasien jika LOS kurang dari 3 hari dan INA CBG ada kata "Berat", maka cek pada Ringkasan Pasien Pulang Rawat Inap', # TODO: apa yang dicek di ringkasan pasien pulan rawat inap?
        "Pada Berkas Klaim Individual Pasien jika Diagnosa Utama terdapat kode D56.1 maka harus ada berkas Protokol PEMBERIAN KELASI BESI dan E-RESEP",
        "Pada Berkas Klaim Individual Pasien jika Diagnosa Utama terdapat kode D66 dan D67 maka harus ada berkas Protokol PEMBERIAN KOSENTRAT, HASIL PEMERIKSAAN LABORATORIUM PATOLOGI KLINIK (Faal Koagulasi) dan E-RESEP",
        "Pada Berkas Klaim Individual Pasien jika terdapat kode diagnose E40-E46 maka wajib ada berkas Asesmen Gizi",
        "Pada Berkas Klaim Individual Pasien jika terdapat prosedur ICD-9: 99.25 maka wajib ada berkas PROTOKOL PEMBERIAN KEMOTERAPI (pasien rawat inap)",
    ]

    rules_rj = [
        "Pada Berkas Klaim Individual Pasien cara pulang harus sama dengan cara pulang pada Resume Medis Rawat Jalan",
        "Pada Berkas Klaim Individual Pasien jika terdapat Diagnosa Utama ICD-10 Z51.1 maka wajib ada berkas PROTOKOL PEMBERIAN KEMOTERAPI (pasien rawat jalan)",
        "Pada Berkas Klaim Individual Pasien jika terdapat Prosedur ICD-9: 99.04, 99.03, 99.05, maka wajib ada berkas INSTALASI TRANSFUSI DARAH PENYERAHAN KANTONG DARAH",
        "Pada Berkas Klaim Individual Pasien jika INA-CBG disebutkan PROSEDUR MAGNETIC RESONANCE IMAGING (MRI) maka wajib ada berkas HASIL PEMERIKSAAN RADIOLOGI MRI",
        "Pada Berkas Klaim Individual Pasien jika INA-CBG disebutkan CT SCAN LAIN-LAIN  maka wajib ada berkas HASIL PEMERIKSAAN RADIOLOGI CT SCAN",
        "Pada Berkas Klaim Individual Pasien jika INA-CBG disebutkan PROSEDUR ULTRASOUND LAIN-LAIN maka wajib ada berkas HASIL PEMERIKSAAN RADIOLOGI USG",
        "Pada Berkas Klaim Individual Pasien jika INA-CBG disebutkan PROSEDUR ELEKROENSEFALOGRAFI (EEG) maka wajib ada berkas LAPORAN HASIL ELEKTROENSEFALOGRAFI ( EEG)",
        "Pada Berkas Klaim Individual Pasien jika INA-CBG disebutkan PROSEDUR EKOKARDIOGRAFI maka wajib ada berkas HASIL PEMERIKSAAN TEE (EKOKARDIOGRAFI)",
        "Pada Berkas Klaim Individual Pasien jika INA-CBG disebutkan PROSEDUR PENGAWASAN FUNGSI KARDIOVASKULAR maka wajib ada berkas HASIL PEMERIKSAAN SETTING PPM",
        "Pada Berkas Klaim Individual Pasien jika INA-CBG disebutkan 89.41 maka wajib ada berkas HASIL ECG SEGMENT",
        "Pada Berkas Klaim Individual Pasien jika INA-CBG disebutkan PELAYANAN KEDOKTERAN NUKLIR dan Diagnosa Utama C73 maka wajib ada berkas MONITORING CARSINOMA TIROID",
        "Pada Berkas Klaim Individual Pasien jika terdapat prosedur Tindakan 92.18 maka wajib ada berkas HASIL PEMERIKSAAN RADIOLOGI (Tindakan BMD)",
        "Pada Berkas Klaim Individual Pasien jika terdapat prosedur Tindakan 41.31 maka wajib ada berkas HASIL PEMERIKSAAN LABORATORIUM PATOLOGI KLINIK atau BMA",
        "Pada Berkas Klaim Individual Pasien jika INA-CBG disebutkan PROSEDUR THERAPI FISIK DAN PROSEDUR KECIL MUSKULOSKLETAL maka wajib ada berkas KARTU TERAPI REHABILITASI MEDIK",
        "Pada Berkas Klaim Individual Pasien jika INA-CBG disebutkan PROSEDUR RADIOTERAPI maka wajib ada berkas CATATAN HARIAN RADIASI EKSTERNA",
        "Pada Berkas Klaim Individual Pasien jika INA-CBG disebutkan PROSEDUR LAIN- LAIN PADA MATA maka wajib ada berkas LAPORAN OPERASI",
    ]

    messages = []

    messages.append(
        SystemMessage(
            content=(
                "\n".join(
                    [
                        "Anda adalah verifikator berkas klaim asuransi BPJS Kesehatan di Rumah Sakit Umum Daerah Dr. Soetomo (RSDS).",
                        "Tugas Anda adalah memastikan berkas klaim asuransi BPJS yang diunggah user adalah lengkap dan konsisten.",
                        f"User mengunggah dokumen pdf klaim asuransi BPJS bernama {pdf.name}.",
                        "Setelah sistem melakukan ekstraksi pdf menjadi teks, dapat diidentifikasi bahwa dokumen pdf tersebut terdiri dari beberapa berkas, yaitu:",
                        "\n".join(
                            [f"{i+1}. {judul}" for i, judul in enumerate(isi_dokumen)]
                        ),
                        "\n\nBerikut ini adalah isi dari masing-masing berkas:",
                        "\n\n".join(
                            [
                                f"{i+1}. {judul}\n{isi_dokumen[judul]}"
                                for i, judul in enumerate(isi_dokumen)
                            ]
                        ),
                        # "Langkah pertama yang anda lakukan adalah melihat informasi Jenis Perawatan yang ada pada Berkas Klaim Individual Pasien."
                        # "Jenis Perawatan hanya bisa salah satu, Rawat Inap atau Rawat Jalan."
                        # "Apabila Jenis Perawatan adalah Rawat Inap, maka gunakan aturan di bawah ini untuk menentukan dokumen klaim lengkap dan valid."
                        # "\n".join(
                        #     [f"{i + 1}. {rule}" for i, rule in enumerate(rules_ri)]
                        # ),
                        # "",
                        # "Apabila Jenis Perawatan adalah Rawat Jalan, maka gunakan aturan di bawah ini untuk menentukan dokumen klaim lengkap dan valid."
                        # "\n".join(
                        #     [f"{i + 1}. {rule}" for i, rule in enumerate(rules_rj)]
                        # ),
                        # prompt awal
                        "\nBerkas bukti klaim tersebut dikatakan lengkap dan valid apabila semua aturan di bawah ini terpenuhi."
                        "\n".join(
                            [f"{i + 1}. {rule}" for i, rule in enumerate(rules_ri)]
                        ),
                        "",
                        "Jawablah dengan Bahasa Indonesia",
                    ]
                )
            )
        ),
    )

    return messages


@tool
def cek_kelengkapan_berkas_klaim_bpjs(kumpulan_berkas: list[UploadedFile]):
    """Cek kelengkapan dokumen-dokumen klaim asuransi BPJS Kesehatan"""
    print("tool:cek_kelengkapan_berkas_klaim_bpjs")

    try:
        if not kumpulan_berkas:
            raise ValueError("tidak ada berkas yang diunggah")

        hasil_cek = ""

        ollama_url = "http://localhost:11434"
        llm = ChatOllama(base_url=ollama_url, model="gemma3:27b")

        for berkas in kumpulan_berkas:
            pdfpath = berkas["filepath"]
            pdfname = os.path.basename(berkas["filepath"])

            print(pdfname)

            with fitz.open(pdfpath) as pdf:
                try:
                    messages = generate_system_message(pdf)
                    response = llm.invoke(messages)
                    hasil_cek += (
                        f"Di bawah ini adalah hasil cek kelengkapan dari dokumen klaim BPJS bernama {pdfname}.\n"
                        f"{str(response.content)}"
                        "\nItulah tadi hasil analisis cek kelengkapan dokumen klaim BPJS bernama {pdfname}.\n"
                        "Sampaikan kepada user hasil analisis tersebut apa adanya tanpa mengolah kata lagi.\n"
                    )
                except Exception as e:
                    hasil_cek += (
                        "Sistem mengalami kendala saat membuka file {pdfname}. Deskripsi error: ```\n"
                        + str(e)
                        + "```"
                    )

        return hasil_cek
    except Exception as e:
        print("error", e)
        return str(e)
