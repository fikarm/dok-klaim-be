from typing import Dict, List
from src.agents.agent_all_rules.toolset.dokumen_klaim_validator.types import JenisRawat


rules: Dict[JenisRawat, List[str]] = {
    JenisRawat.rawat_inap: [
        "Kelas Perawatan pada Berkas Klaim Individual Pasien harus sama dengan Kls. Rawat pada berkas Surat Eligibilitas Peserta BPJS.",
        "Kelas Perawatan pada Berkas Klaim Individual Pasien harus sama nilainya dengan Hak Kelas Perawatan pada berkas Formulir Rawat Inap RSDS. Perbedaan cara penulisan angka romawi dan angka latin bisa dibaikan, yang penting nilainya sama.",
        "Tanggal masuk pada Berkas Klaim Individual Pasien harus sama nilainya dengan Tgl. SEP pada berkas Surat Eligibilitas Peserta BPJS. Perbedaan penulisan format tanggal bisa diabaikan, yang penting nilai tanggalnya sama.",
        # "Pada berkas klaim individual pasien terdapat informasi Cara Pulang. Cara Pulang tersebut biasanya terdiri dari kode dan kalimat cara pulang. Bagian kode bisa diabaikan. Pastikan kalimat cara pulang tersebut muncul juga dalam berkas Ringkasan Pasien Pulang Rawat Inap setelah kalimat Keadaan Waktu KRS.",  # TODO: Atas Persetujuan Dokter?
        "Pada berkas Klaim Individual Pasien, pastikan Cara Pulang sama dengan berkas Ringkasan Pasien Pulang Rawat Inap, dimana Atas Persetujuan Dokter = ['Membaik', 'Dipulangkan','Sembuh'].",  # TODO: Atas Persetujuan Dokter?
        "Pada Berkas Klaim Individual Pasien, jika terdapat prosedur dengan kode 99.25 Injection or infusion of cancer chemotherapeutic substance, maka harus ada berkas Protokol Pemberian Kemoterapi dan harus ada Berkas Monitoring dan Efek Samping Pasien Kemoterapi",
        'Cek Pada Berkas Klaim Individual Pasien, apabila LOS (Length of Stay) kurang dari atau sama dengan 3 hari dan cara pulang bukan meninggal, maka output INA CBG tidak boleh mengandung kata "(BERAT)" ',
        "Pada Berkas Klaim Individual Pasien, apabila LOS (Length of Stay) lebih dari 5 hari, maka Diagnosa Utama sebaiknya tidak menggunakan kode Z51.1",
        "Pada Berkas Klaim Individual Pasien, setelah kata Prosedur, terdapat beberapa kode ICD-9. Jika ada kode ICD-9 lebih kecil atau sama 86, maka harus melampirkan berkas Laporan Operasi Rawat Inap",
        "Pada Berkas Klaim Individual Pasien, cek setelah kata Prosedur, jika ada salah satu kode ICD-9 berikut ini : 96.71, 96.72, 93.90, dan '93.960', maka harus ada berkas Surat Keterangan Penggunaan Alat Bantu Pernafasan",
        "Pada Berkas Klaim Individual Pasien, bila ada output hasil Special CMG, maka wajib ada berkas resep obat/alkes.",
        "Pada Berkas Klaim Individual Pasien, apabila terdapat Diagnosa Sekunder dengan kode Z38.0, maka harus ada berkas Surat Keterangan Lahir",
        # "Pada Berkas Klaim Individual Pasien, setelah kata Diagnosa Utama, terdapat satu kode ICD-10. Jika kode ICD-10 itu diawali dengan huruf S, maka harus ada berkas Jasa Raharja",  # TODO: contoh pdf
        # "Pada Berkas Klaim Individual Pasien, setelah kata Diagnosa Utama, terdapat satu kode ICD-10. Jika kode ICD-10 itu diawali dengan huruf S, maka harus ada berkas Surat Pernyataan Kronologis",  # TODO: contoh pdf
        # "Pada Berkas Klaim Individual Pasien, setelah kata Diagnosa Utama, terdapat satu kode ICD-10. Jika kode ICD-10 itu diawali dengan kata T00, T01, T02, T03, sampai T79, maka harus ada berkas Jasa Raharja",  # TODO: contoh pdf
        # "Pada Berkas Klaim Individual Pasien, setelah kata Diagnosa Utama, terdapat satu kode ICD-10. Jika kode ICD-10 itu diawali dengan kata T00, T01, T02, T03, sampai T79, maka harus ada berkas Surat Pernyataan Kronologis",  # TODO: contoh pdf
        # "Pada Berkas Klaim Individual Pasien, setelah kata Diagnosa Utama, terdapat satu kode ICD-10. Jika kode ICD-10 itu adalah Z51.1 dan LOS (Length of Stay) lebih dari 5 hari, maka beri saran agar melakukan reseleksi Diagnosa Utama",
        # "Pada Berkas Klaim Individual Pasien, setelah kata Diagnosa Utama, terdapat satu kode ICD-10. Jika kode ICD-10 itu adalah D56.1 maka harus ada berkas Protokol PEMBERIAN KELASI BESI",
        # "Pada Berkas Klaim Individual Pasien, setelah kata Diagnosa Utama, terdapat satu kode ICD-10. Jika kode ICD-10 itu adalah D56.1 maka harus ada berkas E-RESEP",
        # "Pada Berkas Klaim Individual Pasien, setelah kata Diagnosa Utama, terdapat satu kode ICD-10. Jika kode ICD-10 itu adalah D66 atau D67, maka harus ada berkas Protokol PEMBERIAN KOSENTRAT",
        # "Pada Berkas Klaim Individual Pasien, setelah kata Diagnosa Utama, terdapat satu kode ICD-10. Jika kode ICD-10 itu adalah D66 atau D67, maka harus ada berkas HASIL PEMERIKSAAN LABORATORIUM PATOLOGI KLINIK (Faal Koagulasi)",
        # "Pada Berkas Klaim Individual Pasien, setelah kata Diagnosa Utama, terdapat satu kode ICD-10. Jika kode ICD-10 itu adalah D66 atau D67, maka harus ada berkas E-RESEP",
        # "Pada Berkas Klaim Individual Pasien, setelah kata Diagnosa Utama, terdapat satu kode ICD-10. Jika kode ICD-10 itu adalah E40, E41, E42, E43, E44, E45, dan E46 maka wajib ada berkas Asesmen Gizi",
        # "Pada Berkas Klaim Individual Pasien, setelah kata Diagnosa Sekunder, terdapat beberapa kode ICD-10. Jika terdapat kode ICD-10: E40, E41, E42, E43, E44, E45, dan E46 maka wajib ada berkas Asesmen Gizi",
        # "Pada Berkas Klaim Individual Pasien, setelah kata Diagnosa Sekunder, terdapat beberapa kode ICD-10. Jika terdapat kode ICD-10: O80, 081, 082, 083, dan O84 maka harus ada berkas Surat Keterangan Telah Dilakukan Pengambilan Sampel Skrining Hipotiroid Kongenital",
        # "Pada Berkas Klaim Individual Pasien, setelah kata Diagnosa Sekunder, terdapat beberapa kode ICD-10. Jika terdapat kode ICD-10: O80, 081, 082, 083, dan O84 maka harus ada berkas Surat Keterangan Lahir (melahirkan di RSDS)",
        # "Pada Berkas Klaim Individual Pasien, setelah kata Diagnosa Sekunder, terdapat beberapa kode ICD-10. Jika terdapat kode ICD-10: Z38.0 maka harus ada berkas Surat Keterangan Lahir (lahir di RSDS)",
        # "Pada Berkas Klaim Individual Pasien, setelah kata Diagnosa Sekunder, terdapat beberapa kode ICD-10. Jika kode ICD-10 itu diawali dengan huruf S, maka harus ada berkas Jasa Raharja",  # TODO: contoh pdf
        # "Pada Berkas Klaim Individual Pasien, setelah kata Diagnosa Sekunder, terdapat beberapa kode ICD-10. Jika kode ICD-10 itu diawali dengan huruf S, maka harus ada berkas Surat Pernyataan Kronologis",  # TODO: contoh pdf
        # "Pada Berkas Klaim Individual Pasien, setelah kata Diagnosa Sekunder, terdapat beberapa kode ICD-10. Jika kode ICD-10 itu diawali dengan kata T00, T01, T02, T03, sampai T79, maka harus ada berkas Jasa Raharja",  # TODO: contoh pdf
        # "Pada Berkas Klaim Individual Pasien, setelah kata Diagnosa Sekunder, terdapat beberapa kode ICD-10. Jika kode ICD-10 itu diawali dengan kata T00, T01, T02, T03, sampai T79, maka harus ada berkas Surat Pernyataan Kronologis",  # TODO: contoh pdf
        # "Pada Berkas Klaim Individual Pasien, setelah kata Prosedur, terdapat beberapa kode ICD-9. Jika ada kode ICD-9: 99.25 maka wajib ada berkas PROTOKOL PEMBERIAN KEMOTERAPI (pasien rawat inap)",
        # "Pada Berkas Klaim Individual Pasien, setelah kata Prosedur, terdapat beberapa kode ICD-9. Jika ada kode ICD-9: 96.71, maka harus ada berkas Surat Keterangan Penggunaan Alat Bantu Pernafasan",
        # "Pada Berkas Klaim Individual Pasien, setelah kata Prosedur, terdapat beberapa kode ICD-9. Jika ada kode ICD-9: 96.72, maka harus ada berkas Surat Keterangan Penggunaan Alat Bantu Pernafasan",
        # "Pada Berkas Klaim Individual Pasien, setelah kata Prosedur, terdapat beberapa kode ICD-9. Jika ada kode ICD-9: 93.90, maka harus ada berkas Surat Keterangan Penggunaan Alat Bantu Pernafasan",
        # "Pada Berkas Klaim Individual Pasien, setelah kata Prosedur, terdapat beberapa kode ICD-9. Jika ada kode ICD-9: 93.960, maka harus ada berkas Surat Keterangan Penggunaan Alat Bantu Pernafasan",
        # "Pada Berkas Klaim Individual Pasien, setelah kata Special CMG terdapat kata 'Rp'. Setelah kata 'Rp', terdapat angka yang menunjukkan besaran tarif dari Special CMG. Contoh: 0.00 (artinya 0 rupiah), 3,236,800.00 (artinya 3236800 rupiah). Jika besaran tarif Special CMG tidak 0.00, maka wajib ada berkas resep obat/alkes.",
        # "Pada Berkas Klaim Individual Pasien, jika setelah Prosedur terdapat kode 99.25, maka harus ditemukan Berkas Monitoring dan Efek Samping Pasien Kemoterapi",
        # "Kelas Perawatan pada Berkas Klaim Individual Pasien harus sama dengan Kls. Rawat pada berkas Surat Eligibilitas Peserta BPJS.",
        # "Kelas Perawatan pada Berkas Klaim Individual Pasien harus sama nilainya dengan Hak Kelas Perawatan pada berkas Formulir Rawat Inap RSDS. Perbedaan cara penulisan angka romawi dan angka latin bisa dibaikan, yang penting nilainya sama.",
        # "Tanggal masuk pada Berkas Klaim Individual Pasien harus sama nilainya dengan Tgl. SEP pada berkas Surat Eligibilitas Peserta BPJS. Perbedaan penulisan format tanggal bisa diabaikan, yang penting nilai tanggalnya sama.",
        # "Pada berkas klaim individual pasien terdapat informasi Cara Pulang. Cara Pulang tersebut biasanya terdiri dari kode dan kalimat cara pulang. Bagian kode bisa diabaikan. Pastikan kalimat cara pulang tersebut muncul juga dalam berkas Ringkasan Pasien Pulang Rawat Inap pada bagian Keadaan Waktu KRS.",  # TODO: Atas Persetujuan Dokter?
        # "Pada Berkas Klaim Individual Pasien, jika setelah Prosedur terdapat kode 99.25, maka harus ada berkas Protokol Pemberian Kemoterapi dan harus ada Berkas Monitoring dan Efek Samping Pasien Kemoterapi",
        # 'Cek Pada Berkas Klaim Individual Pasien, apabila LOS (Length of Stay) kurang dari atau sama dengan 3 hari dan cara pulang bukan meninggal, maka output INA CBG tidak boleh mengandung kata "(BERAT)" ',
        # "Pada Berkas Klaim Individual Pasien, apabila LOS (Length of Stay) lebih dari 5 hari, maka Diagnosa Utama sebaiknya tidak menggunakan kode Z51.1",
        # "Pada Berkas Klaim Individual Pasien, setelah kata Prosedur, terdapat beberapa kode ICD-9. Jika ada kode ICD-9 dengan 2 angka pertama adalah 00, 01, 02, 03, sampai 86, maka harus ada berkas Laporan Operasi Rawat Inap",
        # "Pada Berkas Klaim Individual Pasien, cek setelah kata Prosedur, jika ada salah satu kode ICD-9 berikut ini : 96.71, 96.72, 93.90, dan 93.960, maka harus ada berkas Surat Keterangan Penggunaan Alat Bantu Pernafasan",
        # "Pada Berkas Klaim Individual Pasien, bila ada kode Special CMG, maka wajib ada berkas resep obat/alkes.",
        # "Pada Berkas Klaim Individual Pasien jika INA-CBG berbunyi Kemoterapi maka wajib melampirkan Protokol Pemberian Kemoterapi"
        # "Pada Berkas Klaim Individual Pasien jika INA-CBG berbunyi Kemoterapi maka wajib melampirkan Monitoring dan Efek Samping Pasien Kemoterapi",
        # "Pada Berkas Klaim Individual Pasien jika ada prosedur ICD-9 dengan kode digit diawali 00, 01, 02, 03, sampai 86 maka harus melampirkan Berkas Laporan Operasi Rawat Inap",
        # "Pada Berkas Klaim Individual Pasien, setelah kata Prosedur, terdapat beberapa kode ICD-9. Jika ada kode ICD-9 dengan 2 angka pertama adalah 00, 01, 02, 03, sampai 86, maka harus melampirkan berkas Laporan Operasi Rawat Inap",
        # "Pada Berkas Klaim Individual Pasien jika Special CMG muncul tarif (tidak Rp 0.00) maka wajib ada berkas berkas resep obat/alkes",
        # "Pada Berkas Klaim Individual Pasien jika Diagnosa Sekunder terdapat kode O80-O84 maka harus ada berkas berkas Surat Keterangan Telah Dilakukan Pengambilan Sampel Skrining Hipotiroid Kongenital dan Surat Keterangan Lahir (melahirkan di RSDS)",
        # "Pada Berkas Klaim Individual Pasien jika Diagnosa Sekunder terdapat kode Z38.0 maka harus ada berkas Surat Keterangan Lahir (lahir di RSDS)",
        # 'Pada Berkas Klaim Individual Pasien jika LOS (Length of Stay) hanya 3 hari maka pada Berkas Klaim Individual Pasien tidak boleh ada kata "berat" (terkecuali pasien meninggal)',
        # 'Pada Berkas Klaim Individual Pasien jika LOS kurang dari 3 hari dan INA CBG ada kata "Berat", maka harus di cek ulang berkas Ringkasan Pasien Pulang Rawat Inap', # TODO: apa yang dicek di ringkasan pasien pulan rawat inap?
        # 'Pada Berkas Klaim Individual Pasien jika LOS (Length of Stay) hanya 3 hari, maka INA CBG tidak boleh ada kata "berat" (kecuali pasien meninggal)',
        # 'Pada Berkas Klaim Individual Pasien jika LOS (Length of Stay) kurang dari 3 hari dan INA CBG ada kata "berat", maka harus di cek ulang berkas Ringkasan Pasien Pulang Rawat Inap',
        # # "Pada Berkas Klaim Individual Pasien jika Diagnosa Utama terdapat kode D56.1 maka harus ada berkas Protokol PEMBERIAN KELASI BESI",
        # # "Pada Berkas Klaim Individual Pasien jika Diagnosa Utama terdapat kode D56.1 maka harus ada berkas E-RESEP",
        # # "Pada Berkas Klaim Individual Pasien jika Diagnosa Utama terdapat kode D66 dan D67 maka harus ada berkas Protokol PEMBERIAN KOSENTRAT",
        # # "Pada Berkas Klaim Individual Pasien jika Diagnosa Utama terdapat kode D66 dan D67 maka harus ada berkas HASIL PEMERIKSAAN LABORATORIUM PATOLOGI KLINIK (Faal Koagulasi)",
        # # "Pada Berkas Klaim Individual Pasien jika Diagnosa Utama terdapat kode D66 dan D67 maka harus ada berkas E-RESEP",
        # # "Pada Berkas Klaim Individual Pasien jika terdapat kode diagnosa ICD-10 E40, E41, E42, E43, E44, E45, dan E46 maka wajib ada berkas Asesmen Gizi",
        # # "Pada Berkas Klaim Individual Pasien jika terdapat prosedur ICD-9: 99.25 maka wajib ada berkas PROTOKOL PEMBERIAN KEMOTERAPI (pasien rawat inap)",
    ],
    JenisRawat.rawat_jalan: [
        # "Pada Berkas Klaim Individual Pasien cara pulang harus sama nilainya dengan cara pulang pada berkas Resume Medis Rawat Jalan",
        "Pada Berkas Klaim Individual Pasien jika terdapat Diagnosa Utama ICD-10 Z51.1 maka wajib ada berkas PROTOKOL PEMBERIAN KEMOTERAPI (pasien rawat jalan)",
        "Pada Berkas Klaim Individual Pasien jika terdapat Prosedur ICD-9: 99.04, 99.03, 99.05, maka wajib ada berkas INSTALASI TRANSFUSI DARAH PENYERAHAN KANTONG DARAH",
        "Pada Berkas Klaim Individual Pasien jika INA-CBG disebutkan PROSEDUR MAGNETIC RESONANCE IMAGING (MRI) maka wajib ada berkas HASIL PEMERIKSAAN RADIOLOGI MRI",
        "Pada Berkas Klaim Individual Pasien jika INA-CBG disebutkan CT SCAN LAIN-LAIN  maka wajib ada berkas HASIL PEMERIKSAAN RADIOLOGI CT SCAN",
        # "Pada Berkas Klaim Individual Pasien jika INA-CBG disebutkan PROSEDUR ULTRASOUND LAIN-LAIN maka wajib ada berkas HASIL PEMERIKSAAN RADIOLOGI USG",
        "Pada Berkas Klaim Individual Pasien jika INA-CBG disebutkan PROSEDUR ELEKROENSEFALOGRAFI (EEG) maka wajib ada berkas LAPORAN HASIL ELEKTROENSEFALOGRAFI (EEG)",
        "Pada Berkas Klaim Individual Pasien jika INA-CBG disebutkan PROSEDUR EKOKARDIOGRAFI maka wajib ada berkas HASIL PEMERIKSAAN TEE (EKOKARDIOGRAFI)",
        "Pada Berkas Klaim Individual Pasien jika INA-CBG disebutkan PROSEDUR PENGAWASAN FUNGSI KARDIOVASKULAR maka wajib ada berkas HASIL PEMERIKSAAN SETTING PPM",
        # "Pada Berkas Klaim Individual Pasien jika INA-CBG disebutkan 89.41 maka wajib ada berkas HASIL ECG SEGMENT",
        # "Pada Berkas Klaim Individual Pasien jika INA-CBG disebutkan PELAYANAN KEDOKTERAN NUKLIR dan Diagnosa Utama C73 maka wajib ada berkas MONITORING CARSINOMA TIROID",
        # "Pada Berkas Klaim Individual Pasien jika terdapat prosedur Tindakan 92.18 maka wajib ada berkas HASIL PEMERIKSAAN RADIOLOGI (Tindakan BMD)",
        # "Pada Berkas Klaim Individual Pasien jika terdapat prosedur Tindakan 41.31 maka wajib ada berkas HASIL PEMERIKSAAN LABORATORIUM PATOLOGI KLINIK",
        # "Pada Berkas Klaim Individual Pasien jika INA-CBG disebutkan PROSEDUR THERAPI FISIK DAN PROSEDUR KECIL MUSKULOSKLETAL maka wajib ada berkas KARTU TERAPI REHABILITASI MEDIK",
        # "Pada Berkas Klaim Individual Pasien jika INA-CBG disebutkan PROSEDUR RADIOTERAPI maka wajib ada berkas CATATAN HARIAN RADIASI EKSTERNA",
        "Pada Berkas Klaim Individual Pasien jika INA-CBG disebutkan PROSEDUR LAIN- LAIN PADA MATA maka wajib ada berkas LAPORAN OPERASI rawat jalan",
    ],
}
