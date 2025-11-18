# Plans

- definisikan vectorstore:

  - rule
  - nama segmen (dokumen)
  - chunk dokumen

- Segmentasi:

  - contoh dokumen:

    - eklaim
    - sep
    - dst.

- looping setiap segmen (dokumen)

  - vectorstore[rule]: aturan yang berkaitan dengan eklaim
  - contoh output:
    - Aturan Validasi Klaim BPJS No.123:
      Kelas Perawatan pada Berkas Klaim Individual Pasien harus sama dengan Kls. Rawat pada berkas Surat Eligibilitas Peserta BPJS
    - Aturan Validasi Klaim BPJS No.124: Kelas Perawatan pada Berkas Klaim Individual Pasien harus sama nilainya dengan Hak Kelas Perawatan pada berkas Formulir Rawat Inap RSDS. Perbedaan cara penulisan angka romawi dan angka latin bisa dibaikan, yang penting nilainya sama
  - untuk hasil yang akurat, perlu dispesifikkan di awal, nama dokumen yang dibutuhkan!

- cari dokumen yang dibutuhkan untuk setiap rule

  - vectorstore[dok]: ambil satu item saja, tapi looping setiap rule
  - contoh output:

    - eklaim
    - sep
    - formulir rawat inap

  - temuan qdrant:
    - pakai dense tidak akurat
    - pakai sparse akurat tapi ada result yang nyempil. Bagaimana cara filternya?
      - simpan dokumen yang diperlukan per rule!

- buat prompt validasi yang menggabungkan antara
  - isi dokumen _kemungkinan bisa besar_
  - chunk dokumen
  - semua aturan terkait

```
list konteks:
{konteks}

list rules:
{rules}

cek validasi
```

# setup

```bash
docker run --rm -p 6333:6333 -p 6334:6334 \
    -v "$(pwd)/qdrant_storage:/qdrant/storage:z" \
    qdrant/qdrant
```

http://localhost:6333/dashboard
