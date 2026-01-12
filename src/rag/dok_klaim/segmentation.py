import re
import pytesseract
from enum import Enum
from typing import TypeAlias, Callable, List, Dict
from pymupdf import Document, Page, Pixmap
from src.rag.jenis_dokumen.models import NamaBerkas


class JenisRawat(Enum):
    rawat_inap = "Rawat Inap"
    rawat_jalan = "Rawat Jalan"


class HalamanDitemukan(object):
    def __init__(self, lokasi: range, isi: str):
        self.lokasi = lokasi
        self.isi = isi


HalamanCari: TypeAlias = Document | List[Page]

Extractor: TypeAlias = Callable[[HalamanCari], HalamanDitemukan | None]

Extractors: TypeAlias = Dict[NamaBerkas, Extractor]

DaftarIsi: TypeAlias = List[NamaBerkas | None]

DaftarBerkas: TypeAlias = Dict[NamaBerkas, HalamanDitemukan]


def text_search(pages: List[Page] | Document, kata_kunci: str, pola: str | None = None):
    """
    Mencari first match halaman yang mengandung kata kunci dan pola.

    args:
        `pola` adalah regex yang digunakan untuk filter lanjutan
               setelah kata kunci ditemukan

    returns:
        `int`  index dari argumen `pages`
    """
    i = -1  # input pages index, bukan pdf.page index
    for page in pages:
        i += 1

        if not isinstance(page, Page):
            continue

        text_page = page.get_textpage()

        # skip jika halaman tidak ada kata kunci yang dimaksud
        if not text_page.search(kata_kunci):
            continue

        # cek pola jika perlu
        if pola and not re.search(pola, text_page.extractText()):
            continue

        # kata kunci dan pola ditemukan
        # kembalikan index dari input `pages`

        return i


def ocr(px: Pixmap) -> str:
    """Ekstraksi teks dari image

    Args:
        page (Page): single pymupdf Page object
        px (Pixmap): area dari Page untuk dilakukan OCR
        zoom (float): resize image
    Returns:
        str: teks hasil ocr
    """
    text = pytesseract.image_to_string(px.pil_image(), lang="ind")
    return text


def get_scanned_image(page: Page, threshold=0.75) -> Pixmap | None:
    """
    Deteksi apakah ada gambar scan pada sebuah halaman
    dengan cara menghitung persentasi luas gambar yang
    menutupi halaman. Jika kurang dari `threshold` maka
    dianggap bukan scanned page
    """
    doc = page.parent

    if not isinstance(doc, Document):
        return

    imgs = page.get_image_info(xrefs=True)  # type: ignore

    for img in imgs:
        # kalkulasi coverage
        bbox = img["bbox"]
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        area = w * h
        page_area = (page.rect[2] - page.rect[0]) * (page.rect[3] - page.rect[1])
        coverage = area / page_area

        # pastikan gambar menutupi sebagian besar halaman
        if coverage > threshold:
            # kembalikan gambar dalam objek Pixmap
            return Pixmap(doc, img["xref"])

    return


def halaman_scan(pages: List[Page] | Document, kata_kunci: str):
    """
    Mencari first match halaman yang mengandung kata kunci.
    Halaman akan dikonversi ke gambar (raster) terlebih dahulu.
    Setelah itu baru dicari teks menggunakan Tesseract OCR.
    """
    for page in pages:
        # skip jika halaman tidak ada gambar scan
        scanned_image = get_scanned_image(page)
        if not scanned_image:
            continue

        text = ocr(scanned_image)

        # cari kata kunci
        if not re.search(kata_kunci, text):
            continue

        # kata kunci dan pola ditemukan
        if page.number:
            return HalamanDitemukan(range(page.number, page.number + 1), text)


def multi_halaman(
    pages: List[Page] | Document,
    kata_awal: str,
    kata_akhir: str | None = None,
    pola_awal: str | None = None,
    pola_akhir: str | None = None,
):
    # mencari halaman awal
    start = text_search(pages, kata_awal, pola_awal)
    if start is None:
        return

    pdf_page_start = pages[start].number
    if pdf_page_start is None:
        return

    # mencari halaman akhir
    end = text_search(pages[start:], kata_akhir, pola_akhir) if kata_akhir else None
    if end is None:
        end = start
    else:
        # perlu ditambah index start
        # karena array pages sudah di-slice sebelumnya
        end = start + end

    pdf_page_end = pages[end].number
    if pdf_page_end is None:
        return

    isi = get_texts(pages[start : end + 1])

    return HalamanDitemukan(range(pdf_page_start, pdf_page_end + 1), isi)


def get_texts(pages: List[Page]):
    texts = ""
    for page in pages:
        texts += page.get_textpage().extractText() + "\n"
    return texts


# mapping nama berkas dengan ekstraktor yang sesuai
extractors: Extractors = {
    NamaBerkas.e_klaim: lambda pages: multi_halaman(
        pages,
        kata_awal="Berkas Klaim Individual Pasien",
        kata_akhir="Hasil Grouping",
        pola_akhir=r"Generated[\s\r\n:]+E-Klaim [\w\.\s@\-:]+\n",
    ),
    NamaBerkas.sep_bpjs_rsds: lambda pages: multi_halaman(
        pages,
        kata_awal="Dengan tampilnya luaran SEP elektronik ini merupakan hasil validasi terhadap eligibilitas Pasien secara elektronik",
    ),
    NamaBerkas.form_rawat_inap_rsds: lambda pages: multi_halaman(
        pages,
        kata_awal="SEP DAN FORM RAWAT INAP\nRUMAH SAKIT UMUM DAERAH DOKTER SOETOMO",
    ),
    NamaBerkas.ringkasan_pasien_pulang_rawat_inap: lambda pages: multi_halaman(
        pages,
        kata_awal="RINGKASAN PASIEN PULANG RAWAT INAP",
        kata_akhir="Telah diserahkan dan diterima salinan Ringkasan Pasien Pulang Rawat Inap",
    ),
    NamaBerkas.jasa_raharja: lambda pages: multi_halaman(
        pages,
        kata_awal="PT Jasa Raharja",
    ),
    NamaBerkas.protokol_pemberian_kemoterapi: lambda pages: multi_halaman(
        pages,
        kata_awal="PROTOKOL PEMBERIAN KEMOTERAPI",
        kata_akhir="Nama dan Tanda Tangan DPJP",
    ),
    NamaBerkas.monitoring_dan_efek_samping_pasien_kemoterapi: lambda pages: multi_halaman(
        pages,
        kata_awal="MONITORING DAN EFEK SAMPING PASIEN KEMOTERAPI",
        kata_akhir="Nama dan Tanda Tangan DPJP",
    ),
    NamaBerkas.laporan_operasi: lambda pages: multi_halaman(
        pages,
        kata_awal="LAPORAN OPERASI",
        kata_akhir="Nama dan Tanda Tangan Dokter Operator",
    ),
    NamaBerkas.surat_pernyataan_approval_validasi_biometrik: lambda pages: (
        match
        if (
            match := multi_halaman(
                pages, kata_awal="SURAT PERNYATAAN APPROVAL VALIDASI BIOMETRIK"
            )
        )
        else halaman_scan(pages, "SURAT PERNYATAAN APPROVAL VALIDASI BIOMETRIK")
    ),
    NamaBerkas.e_resep: lambda pages: multi_halaman(
        pages, kata_awal="E-RESEP", kata_akhir="DPJP"
    ),
    NamaBerkas.asesmen_gizi: lambda pages: multi_halaman(
        pages,
        kata_awal="ASESMEN GIZI",
    ),
    NamaBerkas.resume_medis_rawat_jalan: lambda pages: multi_halaman(
        pages,
        kata_awal="RESUME MEDIS RAWAT JALAN",
        kata_akhir="Nama dan Tanda Tangan DPJP",
    ),
    NamaBerkas.instalasi_transfusi_darah_penyerahan_kantong_darah: lambda pages: multi_halaman(
        pages,
        kata_awal="Instalasi Transfusi Darah\nPenyerahan Kantong Darah",
    ),
    NamaBerkas.hasil_pemeriksaan_radiologi: lambda pages: multi_halaman(
        pages,
        kata_awal="HASIL PEMERIKSAAN RADIOLOGI",
        kata_akhir="Hasil Telah Diverifikasi :",
    ),
    NamaBerkas.hasil_pemeriksaan_echocardiography: lambda pages: multi_halaman(
        pages,
        kata_awal="HASIL PEMERIKSAAN ECHOCARDIOGRAPHY",
        kata_akhir="DPJP",
    ),
    NamaBerkas.hasil_pemeriksaan_mata: lambda pages: multi_halaman(
        pages,
        kata_awal="HASIL PEMERIKSAAN MATA RSUD DR SOETOMO SURABAYA",
    ),
    NamaBerkas.hasil_pemeriksaan_bronkoskopi: lambda pages: multi_halaman(
        pages,
        kata_awal="HASIL PEMERIKSAAN BRONKOSKOPI RSUD DR SOETOMO SURABAYA",
    ),
    NamaBerkas.hasil_pemeriksaan_usg: lambda pages: multi_halaman(
        pages,
        kata_awal="HASIL PEMERIKSAAN USG",
    ),
    NamaBerkas.rincian_biaya_perawatan: lambda pages: multi_halaman(
        pages,
        kata_awal="RINCIAN BIAYA PERAWATAN",
        kata_akhir="Kasir",
    ),
    NamaBerkas.surat_keterangan_telah_dilakukan_pengambilan_sampel_skrining_hipotiroid_kongenital: lambda pages: (
        match
        if (match := multi_halaman(pages, kata_awal="SKRINING HIPOTIROID KONGENITAL"))
        else halaman_scan(pages, "SKRINING HIPOTIROID KONGENITAL")
    ),
    NamaBerkas.surat_pernyataan_kronologi: lambda pages: (
        match
        if (match := multi_halaman(pages, kata_awal="SURAT PERNYATAAN KRONOLOGI"))
        else halaman_scan(pages, "SURAT PERNYATAAN KRONOLOGI")
    ),
    NamaBerkas.surat_keterangan_penggunaan_alat_bantu_pernafasan: lambda pages: multi_halaman(
        pages,
        kata_awal="SURAT KETERANGAN PENGGUNAAN ALAT BANTU PERNAFASAN",
        kata_akhir="Nama dan Tanda Tangan DPJP",
    ),
    NamaBerkas.surat_keterangan_lahir: lambda pages: multi_halaman(
        pages, kata_awal="SURAT KETERANGAN LAHIR", kata_akhir="Penolong persalinan"
    ),
    NamaBerkas.protokol_pemberian_konsentrat: lambda pages: multi_halaman(
        pages,
        kata_awal="PROTOKOL PEMBERIAN KONSENTRAT",
        kata_akhir="Nama dan Tanda Tangan DPJP",
    ),
    NamaBerkas.laporan_hasil_eeg: lambda pages: (
        found
        if (
            found := multi_halaman(
                pages,
                kata_awal="LAPORAN HASIL ELEKTROENSEFALOGRAFI ( EEG )",
                kata_akhir="Interpretasi",
            )
        )
        # ketika menunggu hasil keluar
        else multi_halaman(
            pages,
            kata_awal="HASIL PEMERIKSAAN POLI NEUROFISIOLOGI KLINIS",
            kata_akhir="Dokumen ini sah dan telah divalidasi secara sistem elektronik ",
        )
    ),
    NamaBerkas.monitoring_carsinoma_tiroid: lambda pages: multi_halaman(
        pages,
        kata_awal="MONITORING CARSINOMA TIROID",
        kata_akhir="Nama dan Tanda Tangan DPJP",
    ),
    NamaBerkas.hasil_pemeriksaan_laboratorium_patologi_klinik: lambda pages: multi_halaman(
        pages,
        kata_awal="HASIL PEMERIKSAAN LABORATORIUM PATOLOGI KLINIK",
        kata_akhir="Nama dan Tanda Tangan DPJP",
    ),
    NamaBerkas.kartu_terapi_rehabilitasi_medik: lambda pages: multi_halaman(
        pages, kata_awal="KARTU TERAPI REHABILITASI MEDIK"
    ),
    NamaBerkas.catatan_harian_radiasi_eksterna: lambda pages: multi_halaman(
        pages, kata_awal="CATATAN HARIAN RADIASI EKSTERNA"
    ),
    NamaBerkas.protokol_pemberian_kelasi_besi: lambda pages: multi_halaman(
        pages,
        kata_awal="PROTOKOL PEMBERIAN KELASI BESI",
        kata_akhir="Nama dan Tanda Tangan DPJP",
    ),
    NamaBerkas.hasil_pemeriksaan_tee: lambda pages: multi_halaman(
        pages,
        # kata_awal="HASIL PEMERIKSAAN ECHOCARDIOGRAPHY"
        kata_awal="HASIL PEMERIKSAAN TTE",
    ),
    NamaBerkas.surat_keterangan_kematian: lambda pages: multi_halaman(
        pages,
        kata_awal="Surat Keterangan Kematian",
    ),
    NamaBerkas.lembar_hasil_tindakan_uji_fungsi: lambda pages: multi_halaman(
        pages,
        kata_awal="LEMBAR HASIL TINDAKAN UJI FUNGSI",
        kata_akhir="Nama dan Tanda Tangan DPJP",
    ),
    # TODO: perlu contoh case
    # NamaBerkas.resep_obat_atau_alat_kesehatan: lambda pages: multi_halaman(
    #     pages,
    #     kata_awal="E-RESEP",
    # ),
    # TODO:: perlu contoh case
    # NamaBerkas.hasil_pemeriksaan_setting_ppm: lambda pages: multi_halaman(
    #     pages,
    # ),
    # TODO:: perlu contoh case
    # NamaBerkas.hasil_ecg_segment: lambda pages: multi_halaman(
    #     pages,
    # ),
    # TODO: apakah perlu dibedakan?
    # NamaBerkas.laporan_operasi_rawat_inap: lambda pages: multi_halaman(
    #     pages,
    # ),
    # TODO: apakah perlu dibedakan?
    # NamaBerkas.hasil_pemeriksaan_radiologi_mri: lambda pages: multi_halaman(
    #     pages,
    #     kata_awal="HASIL PEMERIKSAAN RADIOLOGI",
    #     kata_akhir="Hasil Telah Diverifikasi :",
    # ),
    # TODO: apakah perlu dibedakan?
    # NamaBerkas.hasil_pemeriksaan_radiologi_ct_scan: lambda pages: multi_halaman(
    #     pages,
    # ),
    # TODO: apakah perlu dibedakan?
    # NamaBerkas.hasil_pemeriksaan_radiologi_tindakan_bmd: lambda pages: multi_halaman(
    #     pages,
    # ),
    # TODO: apakah perlu dibedakan?
    # NamaBerkas.laporan_operasi_rawat_jalan: lambda pages: multi_halaman(
    #     pages,
    # ),
}
