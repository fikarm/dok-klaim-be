import src.agents.agent_all_rules.toolset.dokumen_klaim_validator.searcher as cari
from src.agents.agent_all_rules.toolset.dokumen_klaim_validator.types import (
    NamaBerkas,
    SemuaEkstraktor,
    HalamanCari,
)


def e_klaim(pages: HalamanCari):
    return cari.multi_halaman(
        pages,
        kata_awal="Berkas Klaim Individual Pasien",
        kata_akhir="Hasil Grouping",
        pola_akhir=r"Generated[\s\r\n:]+E-Klaim [\w\.\s@\-:]+\n",
    )


def sep_bpjs_rsds(pages: HalamanCari):
    return cari.multi_halaman(
        pages,
        kata_awal="Dengan tampilnya luaran SEP elektronik ini merupakan hasil validasi terhadap eligibilitas Pasien secara elektronik",
    )


def form_rawat_inap_rsds(pages: HalamanCari):
    return cari.multi_halaman(
        pages,
        kata_awal="SEP DAN FORM RAWAT INAP\nRUMAH SAKIT UMUM DAERAH DOKTER SOETOMO",
    )


def ringkasan_pasien_pulang_rawat_inap(pages: HalamanCari):
    return cari.multi_halaman(
        pages,
        kata_awal="RINGKASAN PASIEN PULANG RAWAT INAP",
        kata_akhir="Telah diserahkan dan diterima salinan Ringkasan Pasien Pulang Rawat Inap",
    )


def rincian_biaya_perawatan(pages: HalamanCari):
    return cari.multi_halaman(
        pages,
        kata_awal="RINCIAN BIAYA PERAWATAN",
        kata_akhir="Kasir",
    )


def protokol_pemberian_kemoterapi(pages: HalamanCari):
    return cari.multi_halaman(
        pages,
        kata_awal="PROTOKOL PEMBERIAN KEMOTERAPI",
        kata_akhir="Nama dan Tanda Tangan DPJP",
    )


def monitoring_dan_efek_samping_pasien_kemoterapi(pages: HalamanCari):
    return cari.multi_halaman(
        pages,
        kata_awal="MONITORING DAN EFEK SAMPING PASIEN KEMOTERAPI",
        kata_akhir="Nama dan Tanda Tangan DPJP",
    )


def surat_pernyataan_kronologi(pages: HalamanCari):
    match = cari.multi_halaman(
        pages,
        kata_awal="SURAT PERNYATAAN KRONOLOGI",
    )
    if match:
        return match

    # mencari dalam bentuk gambar
    return cari.halaman_scan(pages, "SURAT PERNYATAAN KRONOLOGI")


def surat_pernyataan_approval_validasi_biometrik(pages: HalamanCari):
    match = cari.multi_halaman(
        pages,
        kata_awal="SURAT PERNYATAAN APPROVAL VALIDASI BIOMETRIK",
    )
    if match:
        return match

    # mencari dalam bentuk gambar
    return cari.halaman_scan(pages, "SURAT PERNYATAAN APPROVAL VALIDASI BIOMETRIK")


# RJ
def resume_medis_rawat_jalan(pages: HalamanCari):
    return cari.multi_halaman(
        pages,
        kata_awal="RESUME MEDIS RAWAT JALAN",
        kata_akhir="Nama dan Tanda Tangan DPJP",
    )


def instalasi_transfusi_darah_penyerahan_kantong_darah(pages: HalamanCari):
    return cari.multi_halaman(
        pages,
        kata_awal="Instalasi Transfusi Darah\nPenyerahan Kantong Darah",
    )


def hasil_pemeriksaan_radiologi(pages: HalamanCari):
    return cari.multi_halaman(
        pages,
        kata_awal="HASIL PEMERIKSAAN RADIOLOGI",
        kata_akhir="Hasil Telah Diverifikasi :",
    )


def hasil_pemeriksaan_radiologi_mri(pages: HalamanCari):
    # TODO:
    pass


def hasil_pemeriksaan_radiologi_ct_scan(pages: HalamanCari):
    return cari.multi_halaman(
        pages,
        kata_awal="HASIL PEMERIKSAAN RADIOLOGI",
        kata_akhir="Hasil Telah Diverifikasi :",
        pola_awal=": CT",
    )


def kartu_terapi_rehabilitasi_medik(pages: HalamanCari):
    return cari.multi_halaman(
        pages,
        kata_awal="Kartu Terapi Rehabilitasi Medik",
    )


def laporan_operasi(pages: HalamanCari):
    return cari.multi_halaman(
        pages,
        kata_awal="LAPORAN OPERASI",
        kata_akhir="Nama dan Tanda Tangan Dokter Operator",
    )


def asesmen_gizi(pages: HalamanCari):
    return cari.multi_halaman(
        pages,
        kata_awal="ASESMEN GIZI",
    )


def protokol_pemberian_kelasi_besi(pages: HalamanCari):
    return cari.multi_halaman(
        pages,
        kata_awal="PROTOKOL PEMBERIAN KELASI BESI",
    )


def surat_keterangan_penggunaan_alat_bantu_pernafasan(pages: HalamanCari):
    return cari.multi_halaman(
        pages,
        kata_awal="Surat Keterangan Penggunaan Alat Bantu Pernafasan",
    )


def resep_obat_atau_alat_kesehatan(pages: HalamanCari):
    return cari.multi_halaman(
        pages,
        kata_awal="Resep Obat",
    )


def catatan_harian_radiasi_eksterna(pages: HalamanCari):
    return cari.multi_halaman(
        pages,
        kata_awal="Radiasi Eksterna",
    )


def laporan_hasil_eeg(pages: HalamanCari):
    return cari.multi_halaman(
        pages,
        kata_awal="LAPORAN HASIL ELEKTROENSEFALOGRAFI ( EEG )",
    )


def jasa_raharja(pages: HalamanCari):
    return cari.multi_halaman(
        pages,
        kata_awal="PT Jasa Raharja",
    )


def hasil_pemeriksaan_tee(pages: HalamanCari):
    return cari.multi_halaman(
        pages,
        kata_awal="Hasil Pemeriksaan TEE",
    )


def hasil_pemeriksaan_setting_ppm(pages: HalamanCari):
    return cari.multi_halaman(
        pages,
        kata_awal="SETTING PPM",
    )


def surat_keterangan_telah_dilakukan_pengambilan_sampel_skrining_hipotiroid_kongenital(
    pages: HalamanCari,
):
    return cari.multi_halaman(
        pages,
        kata_awal="SHK",
    )


def surat_keterangan_lahir(pages: HalamanCari):
    return cari.multi_halaman(
        pages,
        kata_awal="Surat Keterangan Lahir",
    )


def protokol_pemberian_konsentrat(pages: HalamanCari):
    return cari.multi_halaman(
        pages,
        kata_awal="Konsentrat",
    )


# mapping nama berkas dengan ekstraktor yang sesuai
ekstraktor: SemuaEkstraktor = {
    NamaBerkas.e_klaim: e_klaim,
    NamaBerkas.sep_bpjs_rsds: sep_bpjs_rsds,
    NamaBerkas.form_rawat_inap_rsds: form_rawat_inap_rsds,
    NamaBerkas.ringkasan_pasien_pulang_rawat_inap: ringkasan_pasien_pulang_rawat_inap,
    NamaBerkas.rincian_biaya_perawatan: rincian_biaya_perawatan,
    NamaBerkas.protokol_pemberian_kemoterapi: protokol_pemberian_kemoterapi,
    NamaBerkas.monitoring_dan_efek_samping_pasien_kemoterapi: monitoring_dan_efek_samping_pasien_kemoterapi,
    NamaBerkas.surat_pernyataan_kronologi: surat_pernyataan_kronologi,
    NamaBerkas.surat_pernyataan_approval_validasi_biometrik: surat_pernyataan_approval_validasi_biometrik,
    NamaBerkas.resume_medis_rawat_jalan: resume_medis_rawat_jalan,
    NamaBerkas.instalasi_transfusi_darah_penyerahan_kantong_darah: instalasi_transfusi_darah_penyerahan_kantong_darah,
    NamaBerkas.hasil_pemeriksaan_radiologi: hasil_pemeriksaan_radiologi,
    NamaBerkas.hasil_pemeriksaan_radiologi_mri: hasil_pemeriksaan_radiologi_mri,
    NamaBerkas.hasil_pemeriksaan_radiologi_ct_scan: hasil_pemeriksaan_radiologi_ct_scan,
    NamaBerkas.kartu_terapi_rehabilitasi_medik: kartu_terapi_rehabilitasi_medik,
    NamaBerkas.laporan_operasi: laporan_operasi,
    NamaBerkas.laporan_operasi_rawat_inap: laporan_operasi,
    NamaBerkas.laporan_operasi_rawat_jalan: laporan_operasi,
    NamaBerkas.asesmen_gizi: asesmen_gizi,
    NamaBerkas.protokol_pemberian_kelasi_besi: protokol_pemberian_kelasi_besi,
    NamaBerkas.surat_keterangan_penggunaan_alat_bantu_pernafasan: surat_keterangan_penggunaan_alat_bantu_pernafasan,
    NamaBerkas.resep_obat_atau_alat_kesehatan: resep_obat_atau_alat_kesehatan,
    NamaBerkas.catatan_harian_radiasi_eksterna: catatan_harian_radiasi_eksterna,
    NamaBerkas.laporan_hasil_eeg: laporan_hasil_eeg,
    NamaBerkas.jasa_raharja: jasa_raharja,
    NamaBerkas.hasil_pemeriksaan_tee: hasil_pemeriksaan_tee,
    NamaBerkas.hasil_pemeriksaan_setting_ppm: hasil_pemeriksaan_setting_ppm,
    NamaBerkas.surat_keterangan_telah_dilakukan_pengambilan_sampel_skrining_hipotiroid_kongenital: surat_keterangan_telah_dilakukan_pengambilan_sampel_skrining_hipotiroid_kongenital,
    NamaBerkas.surat_keterangan_lahir: surat_keterangan_lahir,
    NamaBerkas.protokol_pemberian_konsentrat: protokol_pemberian_konsentrat,
    # NamaBerkas.e_resep: e_resep,
    # NamaBerkas.hasil_ecg_segment: "",
    #
    #
    #
    #
    #
    #
    #
    # NamaBerkas.e_klaim: "",
    # NamaBerkas.sep_bpjs_rsds: "",
    # NamaBerkas.form_rawat_inap_rsds: "",
    # NamaBerkas.ringkasan_pasien_pulang_rawat_inap: "",
    # NamaBerkas.jasa_raharja: "",
    # NamaBerkas.surat_pernyataan_kronologi: "",
    # NamaBerkas.protokol_pemberian_kemoterapi: "",
    # NamaBerkas.monitoring_dan_efek_samping_pasien_kemoterapi: "",
    # NamaBerkas.laporan_operasi: "",
    # NamaBerkas.laporan_operasi_rawat_inap: "",
    # NamaBerkas.surat_keterangan_penggunaan_alat_bantu_pernafasan: "",
    # NamaBerkas.resep_obat_atau_alat_kesehatan: "",
    # NamaBerkas.surat_keterangan_telah_dilakukan_pengambilan_sampel_skrining_hipotiroid_kongenital: "",
    # NamaBerkas.surat_keterangan_lahir: "",
    # NamaBerkas.surat_pernyataan_approval_validasi_biometrik: "",
    # NamaBerkas.protokol_pemberian_kelasi_besi: "",
    # NamaBerkas.e_resep: "",
    # NamaBerkas.protokol_pemberian_konsentrat: "",
    # NamaBerkas.asesmen_gizi: "",
    # NamaBerkas.resume_medis_rawat_jalan: "",
    # NamaBerkas.instalasi_transfusi_darah_penyerahan_kantong_darah: "",
    # NamaBerkas.hasil_pemeriksaan_radiologi_mri: "",
    # NamaBerkas.hasil_pemeriksaan_radiologi_ct_scan: "",
    # NamaBerkas.hasil_pemeriksaan_radiologi: "",
    # NamaBerkas.laporan_hasil_eeg: "",
    # NamaBerkas.hasil_pemeriksaan_tee: "",
    # NamaBerkas.hasil_pemeriksaan_setting_ppm: "",
    # NamaBerkas.hasil_ecg_segment: "",
    # NamaBerkas.monitoring_carsinoma_tiroid: "",
    # NamaBerkas.hasil_pemeriksaan_radiologi_tindakan_bmd: "",
    # NamaBerkas.hasil_pemeriksaan_laboratorium_patologi_klinik: "",
    # NamaBerkas.kartu_terapi_rehabilitasi_medik: "",
    # NamaBerkas.catatan_harian_radiasi_eksterna: "",
    # NamaBerkas.laporan_operasi_rawat_jalan: "",
    # NamaBerkas.rincian_biaya_perawatan: "",
}
