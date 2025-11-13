import re
import pytesseract
from typing import List
from pymupdf import Document, Page, Pixmap
from src.agents.agent_rule_evaluator_vector.parser.schema import HalamanDitemukan, JenisRawat


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


def nosep(eklaim: str):
    pattern = r"Nomor SEP\n:\n(\w+)"
    match = re.search(pattern, eklaim)
    if match:
        return match.group(1)


def jenis_rawat(eklaim: str) -> JenisRawat | None:
    pattern = r"Jenis Perawatan\n:\n\d+\s-\s([\w ]+)"
    match = re.search(pattern, eklaim)

    if match is None:
        return

    jenis_rawat = match.group(1).strip()

    if "Rawat Inap" == jenis_rawat:
        return JenisRawat.rawat_inap

    return JenisRawat.rawat_jalan
