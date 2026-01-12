import os
import re

from pymupdf import Document

from src.rag.dok_klaim.embeddings import embed as qdrant_embed, remove_nosep
from src.rag.dok_klaim.splitter import chunking
from src.rag.dok_klaim.segmentation import (
    NamaBerkas,
    JenisRawat,
    DaftarIsi,
    DaftarBerkas,
    HalamanDitemukan,
    extractors,
)


class DokumenKlaim(object):
    pdf: Document
    name: str
    nosep: str
    jenis_rawat: JenisRawat
    daftar_isi: DaftarIsi
    daftar_berkas: DaftarBerkas

    def __init__(self, pdf: Document):
        self.pdf = pdf
        self.name = os.path.basename(pdf.name or "")

        self.daftar_isi = [None] * pdf.page_count
        self.daftar_berkas = {}

        self.nosep = self.__nosep() or ""
        self.jenis_rawat = self.__jenis_rawat()

    def __nosep(self):
        eklaim = self.__eklaim()
        pattern = r"Nomor SEP\n:\n(\w+)"
        match = re.search(pattern, eklaim)
        if match:
            return match.group(1)

    def __eklaim(self):
        ditemukan = self.get_berkas(NamaBerkas.e_klaim)

        if not ditemukan:
            raise ValueError(f"Tidak ditemukan berkas E-Klaim dari dokumen {self.name}")

        return ditemukan.isi

    def __jenis_rawat(self) -> JenisRawat:
        """menentukan jenis rawat dari eklaim"""
        eklaim = self.__eklaim()

        pattern = r"Jenis Perawatan[^:]*:[\D\n]*\d - (Rawat \w+)"
        match = re.search(pattern, eklaim)

        if match is None:
            raise ValueError(
                f"Jenis Rawat tidak dapat diidentifkasi dari berkas E Klaim yang ditemukan dalam dokumen {self.name}"
            )

        jenis_rawat = match.group(1).strip()

        if "Rawat Inap" == jenis_rawat:
            return JenisRawat.rawat_inap

        return JenisRawat.rawat_jalan

    def get_berkas(self, nama: NamaBerkas) -> HalamanDitemukan | None:
        # gunakan cache jika sudah pernah ekstraksi
        if nama in self.daftar_berkas:
            return self.daftar_berkas[nama]

        # melakukan ekstraksi on demand
        if not nama in extractors:
            # raise ValueError("Belum ada ekstraktor untuk berkas: " + nama.value)
            return None

        # hanya cari pages yang belum punya NamaBerkas.
        # index pada daftar isi adalah sama dengan index di page pdf
        pages = []
        for no, halaman in enumerate(self.daftar_isi):
            if halaman is None:
                pages.append(self.pdf[no])

        # gunakan fungsi ekstraksi yang sesuai
        halaman_ditemukan = extractors[nama](pages)

        # print("---")
        # print(nama)
        # print(self.daftar_isi)
        # # print(str(match.isi)[:100])
        # print("---")

        # kembalikan None jika tidak ada berkas
        if halaman_ditemukan is None:
            return

        # jika ditemukan, maka update daftar isi
        for no in halaman_ditemukan.lokasi:
            self.daftar_isi[no] = nama

        # cache isi berkas pada variabel daftar berkas
        self.daftar_berkas[nama] = halaman_ditemukan

        # print(match.isi)

        return halaman_ditemukan

    def embed(self):
        print("\n==== Dok Embed ====")

        for b in extractors:
            # segementation
            halaman = self.get_berkas(b)

            if not halaman:
                continue

            # chunking and embbedding
            pages = self.pdf[halaman.lokasi.start : halaman.lokasi.stop]
            qdrant_embed(self.nosep, b.value, pages)

            print("[%2d:%2d]" % (halaman.lokasi.start, halaman.lokasi.stop), b.value)

    def cleanup(self):
        remove_nosep(self.nosep)
