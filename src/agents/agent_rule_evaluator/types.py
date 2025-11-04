from enum import Enum
from fitz import Page, Document
from typing import List, TypeAlias, Callable, Dict, Set
from pydantic import BaseModel, Field


class JenisRawat(Enum):
    rawat_inap = "Rawat Inap"
    rawat_jalan = "Rawat Jalan"


class NamaBerkas(Enum):
    e_klaim = "Klaim Individual Pasien"
    sep_bpjs_rsds = "Surat Eligibilitas Peserta BPJS (SEP BPJS)"
    form_rawat_inap_rsds = "Formulir Rawat Inap RSDS"
    ringkasan_pasien_pulang_rawat_inap = "Ringkasan Pasien Pulang Rawat Inap"
    jasa_raharja = "Jasa Raharja"
    surat_pernyataan_kronologi = "Surat Pernyataan Kronologi"
    protokol_pemberian_kemoterapi = "Protokol Pemberian Kemoterapi"
    monitoring_dan_efek_samping_pasien_kemoterapi = (
        "Monitoring dan Efek Samping Pasien Kemoterapi"
    )
    laporan_operasi = "Laporan Operasi"
    laporan_operasi_rawat_inap = "Laporan Operasi Rawat Inap"
    surat_keterangan_penggunaan_alat_bantu_pernafasan = (
        "Surat Keterangan Penggunaan Alat Bantu Pernafasan"
    )
    resep_obat_atau_alat_kesehatan = "Resep Obat atau Alat Kesehatan (obat/alkes)"
    surat_keterangan_telah_dilakukan_pengambilan_sampel_skrining_hipotiroid_kongenital = "Surat Keterangan Telah Dilakukan Pengambilan Sampel Skrining Hipotiroid Kongenital"
    surat_keterangan_lahir = "Surat Keterangan Lahir"
    surat_pernyataan_approval_validasi_biometrik = (
        "Surat Pernyataan Approval Validasi Biometrik"
    )
    protokol_pemberian_kelasi_besi = "Protokol PEMBERIAN KELASI BESI"
    e_resep = "E-RESEP"
    protokol_pemberian_konsentrat = "Protokol PEMBERIAN KONSENTRAT"
    asesmen_gizi = "Asesmen Gizi"
    resume_medis_rawat_jalan = "Resume Medis Rawat Jalan"
    instalasi_transfusi_darah_penyerahan_kantong_darah = (
        "Instalasi Transfusi Darah Penyerahan Kantong Darah"
    )
    hasil_pemeriksaan_radiologi_mri = "Hasil Pemeriksaan Radiologi MRI"
    hasil_pemeriksaan_radiologi_ct_scan = "Hasil Pemeriksaan Radiologi CT Scan"
    hasil_pemeriksaan_radiologi = "Hasil Pemeriksaan Radiologi USG"
    laporan_hasil_eeg = "Laporan Hasil Elektroensefalografi (EEG)"
    hasil_pemeriksaan_tee = "Hasil Pemeriksaan Tee (Ekokardiografi)"
    hasil_pemeriksaan_setting_ppm = "Hasil Pemeriksaan Setting PPM"
    hasil_ecg_segment = "Hasil ECG Segment"
    monitoring_carsinoma_tiroid = "Monitoring Carsinoma Tiroid"
    hasil_pemeriksaan_radiologi_tindakan_bmd = (
        "Hasil Pemeriksaan Radiologi (Tindakan BMD)"
    )
    hasil_pemeriksaan_laboratorium_patologi_klinik = (
        "Hasil Pemeriksaan Laboratorium Patologi Klinik"
    )
    kartu_terapi_rehabilitasi_medik = "Kartu Terapi Rehabilitasi Medik"
    catatan_harian_radiasi_eksterna = "Catatan Harian Radiasi Eksterna"
    laporan_operasi_rawat_jalan = "Laporan Operasi Rawat Jalan"
    rincian_biaya_perawatan = "Rincian Biaya Perawatan"


HalamanCari: TypeAlias = Document | List[Page]
DaftarIsi: TypeAlias = List[NamaBerkas | None]
DaftarBerkas: TypeAlias = Dict[NamaBerkas, str]


class HalamanDitemukan(object):
    def __init__(self, lokasi: range, isi: str):
        self.lokasi = lokasi
        self.isi = isi


Ekstraktor = Callable[[HalamanCari], HalamanDitemukan | None]
SemuaEkstraktor: TypeAlias = dict[NamaBerkas, Ekstraktor]


class NamaBerkasDitemukan(BaseModel):
    nama: NamaBerkas

    def __hash__(self):
        return hash((self.nama))


class DaftarNamaBerkasDitemukan(BaseModel):
    daftar: Set[NamaBerkasDitemukan] = Field(
        description=(
            "Daftar semua nama berkas yang anda temukan. "
            "Nama berkas biasanya diawali dengan kata 'Berkas'."
        )
    )


class HasilEvaluasi(BaseModel):
    alasan: str = Field(
        description="hasil analisis kelengkapan dokumen klaim asuransi BPJS berdasarkan aturan yang diberikan"
    )
    status: bool = Field(
        description="hasil cek kelengkapan dokumen klaim asuransi BPJS"
    )
    saran: str = Field(
        description="Rekomendasi agar aturan yang diberikan terpenuhi hanya jika berkas belum lengkap"
    )
