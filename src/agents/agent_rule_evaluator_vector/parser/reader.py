import os
import src.agents.agent_rule_evaluator_vector.parser.searcher as cari
from pymupdf import Document
from src.agents.agent_rule_evaluator_vector.parser.extractor import extractors
from src.agents.agent_rule_evaluator_vector.parser.schema import (
    NamaBerkas,
    JenisRawat,
    DaftarIsi,
    DaftarBerkas,
)


class DokumenKlaim(object):
    pdf: Document
    name: str
    no_sep: str
    jenis_rawat: JenisRawat
    daftar_isi: DaftarIsi
    daftar_berkas: DaftarBerkas

    def __init__(self, pdf: Document):
        self.pdf = pdf
        self.name = os.path.basename(pdf.name or "")

        self.daftar_isi = [None] * pdf.page_count
        self.daftar_berkas = {}

        eklaim = self.__eklaim()
        self.jenis_rawat = self.__jenis_rawat(eklaim)
        self.no_sep = cari.nosep(eklaim) or ""

    def __eklaim(self):
        teks = self.get_berkas(NamaBerkas.e_klaim)

        if not teks:
            raise ValueError(f"Tidak ditemukan berkas E-Klaim dari dokumen {self.name}")

        return teks

    def __jenis_rawat(self, eklaim: str):
        """menentukan jenis rawat dari eklaim"""
        jenis_rawat = cari.jenis_rawat(eklaim)

        if jenis_rawat is None:
            raise ValueError(
                f"Jenis Rawat tidak dapat diidentifkasi dari berkas E Klaim yang ditemukan dalam dokumen {self.name}"
            )

        return jenis_rawat

    def get_berkas(self, nama: NamaBerkas):
        # gunakan cache jika sudah pernah ekstraksi
        if nama in self.daftar_berkas:
            return self.daftar_berkas[nama]

        # melakukan ekstraksi on demand
        if not nama in extractors:
            raise ValueError("Belum ada extractors untuk berkas: " + nama.value)

        # hanya cari pages yang belum punya NamaBerkas.
        # index pada daftar isi adalah sama dengan index di page pdf
        pages = []
        for no, halaman in enumerate(self.daftar_isi):
            if halaman is None:
                pages.append(self.pdf[no])

        # gunakan fungsi ekstraksi yang sesuai
        match = extractors[nama](pages)

        # kembalikan None jika tidak ada berkas
        if match is None:
            return

        # jika ditemukan, maka update daftar isi
        for no in match.lokasi:
            self.daftar_isi[no] = nama

        # cache isi berkas pada variabel daftar berkas
        self.daftar_berkas[nama] = match.isi

        return match.isi
