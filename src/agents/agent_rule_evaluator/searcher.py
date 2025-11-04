import re
import fitz
import pytesseract
from PIL import Image
from fitz import Document, Page
from typing import List
from src.agents.agent_rule_evaluator.types import HalamanDitemukan, JenisRawat


def text_search(pages: List[Page] | Document, kata_kunci: str, pola: str | None = None):
    """
    Mencari first match halaman yang mengandung kata kunci dan pola.

    args:
        `pola` adalah regex yang digunakan untuk filter lanjutan
               setelah kata kunci ditemukan

    returns:
        `int`  index dari argumen `pages`
    """
    i = -1
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

        print(">>> ::", i, kata_kunci)
        print(str(text_page.extractText())[:50])

        return i


def page_image_as_text(page: Page, zoom=2):
    # konversi Page ke Image
    display = page.get_displaylist()
    mat = fitz.Matrix(zoom, zoom)  # to increase the resolution
    pix = display.get_pixmap(mat)
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    text = pytesseract.image_to_string(img)
    return text


def is_scanned_page(page: Page, threshold=0.95):
    """
    Deteksi apakah ada gambar scan pada sebuah halaman
    dengan cara menghitung persentasi luas gambar yang
    menutupi halaman. Jika kurang dari `threshold` maka
    dianggap bukan scanned page
    """
    doc = page.parent

    if not isinstance(doc, Document):
        return False

    imgs = page.get_image_info()  # type: ignore

    for img in imgs:
        bbox = img["bbox"]
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        area = w * h
        if (area / page.rect.get_area()) > threshold:
            return True

    return False


def halaman_scan(pages: List[Page] | Document, kata_kunci: str):
    """
    Mencari first match halaman yang mengandung kata kunci.
    Halaman akan dikonversi ke gambar (raster) terlebih dahulu.
    Setelah itu baru dicari teks menggunakan Tesseract OCR.
    """
    for page in pages:
        # skip jika halaman tidak ada gambar scan
        if not is_scanned_page(page):
            continue

        text = page_image_as_text(page)

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

    print(">>>", start)

    # mencari halaman akhir
    end = text_search(pages[start:], kata_akhir, pola_akhir) if kata_akhir else None
    if end is None:
        end = start

    print(">>>", end)

    page_start = pages[start].number
    if page_start is None:
        return

    page_end = pages[end].number
    if page_end is None:
        return

    # print(">>>", pages)
    isi = get_texts(pages[start : end + 1])
    print(">>>", page_start, page_end, isi[:20])

    return HalamanDitemukan(range(page_start, page_end + 1), isi)


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
