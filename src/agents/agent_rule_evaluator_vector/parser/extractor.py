import src.agents.agent_rule_evaluator_vector.parser.searcher as src
from src.agents.agent_rule_evaluator_vector.parser.schema import NamaBerkas, Extractors


# mapping nama berkas dengan ekstraktor yang sesuai
extractors: Extractors = {
    NamaBerkas.e_klaim: lambda pages: src.multi_halaman(
        pages,
        kata_awal="Berkas Klaim Individual Pasien",
        kata_akhir="Hasil Grouping",
        pola_akhir=r"Generated[\s\r\n:]+E-Klaim [\w\.\s@\-:]+\n",
    ),
    NamaBerkas.sep_bpjs_rsds: lambda pages: src.multi_halaman(
        pages,
        kata_awal="Dengan tampilnya luaran SEP elektronik ini merupakan hasil validasi terhadap eligibilitas Pasien secara elektronik",
    ),
    NamaBerkas.form_rawat_inap_rsds: lambda pages: src.multi_halaman(
        pages,
        kata_awal="SEP DAN FORM RAWAT INAP\nRUMAH SAKIT UMUM DAERAH DOKTER SOETOMO",
    ),
    NamaBerkas.ringkasan_pasien_pulang_rawat_inap: lambda pages: src.multi_halaman(
        pages,
        kata_awal="RINGKASAN PASIEN PULANG RAWAT INAP",
        kata_akhir="Telah diserahkan dan diterima salinan Ringkasan Pasien Pulang Rawat Inap",
    ),
    NamaBerkas.jasa_raharja: lambda pages: src.multi_halaman(
        pages,
        kata_awal="PT Jasa Raharja",
    ),
    NamaBerkas.protokol_pemberian_kemoterapi: lambda pages: src.multi_halaman(
        pages,
        kata_awal="PROTOKOL PEMBERIAN KEMOTERAPI",
        kata_akhir="Nama dan Tanda Tangan DPJP",
    ),
    NamaBerkas.monitoring_dan_efek_samping_pasien_kemoterapi: lambda pages: src.multi_halaman(
        pages,
        kata_awal="MONITORING DAN EFEK SAMPING PASIEN KEMOTERAPI",
        kata_akhir="Nama dan Tanda Tangan DPJP",
    ),
    NamaBerkas.laporan_operasi: lambda pages: src.multi_halaman(
        pages,
        kata_awal="LAPORAN OPERASI",
        kata_akhir="Nama dan Tanda Tangan Dokter Operator",
    ),
    NamaBerkas.surat_pernyataan_approval_validasi_biometrik: lambda pages: (
        match
        if (
            match := src.multi_halaman(
                pages, kata_awal="SURAT PERNYATAAN APPROVAL VALIDASI BIOMETRIK"
            )
        )
        else src.halaman_scan(pages, "SURAT PERNYATAAN APPROVAL VALIDASI BIOMETRIK")
    ),
    NamaBerkas.e_resep: lambda pages: src.multi_halaman(
        pages, kata_awal="E-RESEP", kata_akhir="DPJP"
    ),
    NamaBerkas.asesmen_gizi: lambda pages: src.multi_halaman(
        pages,
        kata_awal="ASESMEN GIZI",
    ),
    NamaBerkas.resume_medis_rawat_jalan: lambda pages: src.multi_halaman(
        pages,
        kata_awal="RESUME MEDIS RAWAT JALAN",
        kata_akhir="Nama dan Tanda Tangan DPJP",
    ),
    NamaBerkas.instalasi_transfusi_darah_penyerahan_kantong_darah: lambda pages: src.multi_halaman(
        pages,
        kata_awal="Instalasi Transfusi Darah\nPenyerahan Kantong Darah",
    ),
    NamaBerkas.hasil_pemeriksaan_radiologi: lambda pages: src.multi_halaman(
        pages,
        kata_awal="HASIL PEMERIKSAAN RADIOLOGI",
        kata_akhir="Hasil Telah Diverifikasi :",
    ),
    NamaBerkas.rincian_biaya_perawatan: lambda pages: src.multi_halaman(
        pages,
        kata_awal="RINCIAN BIAYA PERAWATAN",
        kata_akhir="Kasir",
    ),
    NamaBerkas.surat_keterangan_telah_dilakukan_pengambilan_sampel_skrining_hipotiroid_kongenital: lambda pages: (
        match
        if (
            match := src.multi_halaman(
                pages, kata_awal="SKRINING HIPOTIROID KONGENITAL"
            )
        )
        else src.halaman_scan(pages, "SKRINING HIPOTIROID KONGENITAL")
    ),
    NamaBerkas.surat_pernyataan_kronologi: lambda pages: (
        match
        if (match := src.multi_halaman(pages, kata_awal="SURAT PERNYATAAN KRONOLOGI"))
        else src.halaman_scan(pages, "SURAT PERNYATAAN KRONOLOGI")
    ),
    NamaBerkas.surat_keterangan_penggunaan_alat_bantu_pernafasan: lambda pages: src.multi_halaman(
        pages,
        kata_awal="SURAT KETERANGAN PENGGUNAAN ALAT BANTU PERNAFASAN",
        kata_akhir="Nama dan Tanda Tangan DPJP",
    ),
    NamaBerkas.surat_keterangan_lahir: lambda pages: src.multi_halaman(
        pages, kata_awal="SURAT KETERANGAN LAHIR", kata_akhir="Penolong persalinan"
    ),
    NamaBerkas.protokol_pemberian_konsentrat: lambda pages: src.multi_halaman(
        pages,
        kata_awal="PROTOKOL PEMBERIAN KONSENTRAT",
        kata_akhir="Nama dan Tanda Tangan DPJP",
    ),
    NamaBerkas.laporan_hasil_eeg: lambda pages: (
        found
        if (
            found := src.multi_halaman(
                pages,
                kata_awal="LAPORAN HASIL ELEKTROENSEFALOGRAFI ( EEG )",
                kata_akhir="Interpretasi",
            )
        )
        # ketika menunggu hasil keluar
        else src.multi_halaman(
            pages,
            kata_awal="HASIL PEMERIKSAAN POLI NEUROFISIOLOGI KLINIS",
            kata_akhir="Dokumen ini sah dan telah divalidasi secara sistem elektronik ",
        )
    ),
    NamaBerkas.monitoring_carsinoma_tiroid: lambda pages: src.multi_halaman(
        pages,
        kata_awal="MONITORING CARSINOMA TIROID",
        kata_akhir="Nama dan Tanda Tangan DPJP",
    ),
    NamaBerkas.hasil_pemeriksaan_laboratorium_patologi_klinik: lambda pages: src.multi_halaman(
        pages,
        kata_awal="HASIL PEMERIKSAAN LABORATORIUM PATOLOGI KLINIK",
        kata_akhir="Nama dan Tanda Tangan DPJP",
    ),
    NamaBerkas.kartu_terapi_rehabilitasi_medik: lambda pages: src.multi_halaman(
        pages, kata_awal="KARTU TERAPI REHABILITASI MEDIK"
    ),
    NamaBerkas.catatan_harian_radiasi_eksterna: lambda pages: src.multi_halaman(
        pages, kata_awal="CATATAN HARIAN RADIASI EKSTERNA"
    ),
    NamaBerkas.protokol_pemberian_kelasi_besi: lambda pages: src.multi_halaman(
        pages,
        kata_awal="PROTOKOL PEMBERIAN KELASI BESI",
        kata_akhir="Nama dan Tanda Tangan DPJP",
    ),
    NamaBerkas.hasil_pemeriksaan_tee: lambda pages: src.multi_halaman(
        pages,
        # kata_awal="HASIL PEMERIKSAAN ECHOCARDIOGRAPHY"
        kata_awal="HASIL PEMERIKSAAN TTE",
    ),
    # TODO: perlu contoh case
    # NamaBerkas.resep_obat_atau_alat_kesehatan: lambda pages: src.multi_halaman(
    #     pages,
    #     kata_awal="E-RESEP",
    # ),
    # TODO:: perlu contoh case
    # NamaBerkas.hasil_pemeriksaan_setting_ppm: lambda pages: src.multi_halaman(
    #     pages,
    # ),
    # TODO:: perlu contoh case
    # NamaBerkas.hasil_ecg_segment: lambda pages: src.multi_halaman(
    #     pages,
    # ),
    # TODO: apakah perlu dibedakan?
    # NamaBerkas.laporan_operasi_rawat_inap: lambda pages: src.multi_halaman(
    #     pages,
    # ),
    # TODO: apakah perlu dibedakan?
    # NamaBerkas.hasil_pemeriksaan_radiologi_mri: lambda pages: src.multi_halaman(
    #     pages,
    #     kata_awal="HASIL PEMERIKSAAN RADIOLOGI",
    #     kata_akhir="Hasil Telah Diverifikasi :",
    # ),
    # TODO: apakah perlu dibedakan?
    # NamaBerkas.hasil_pemeriksaan_radiologi_ct_scan: lambda pages: src.multi_halaman(
    #     pages,
    # ),
    # TODO: apakah perlu dibedakan?
    # NamaBerkas.hasil_pemeriksaan_radiologi_tindakan_bmd: lambda pages: src.multi_halaman(
    #     pages,
    # ),
    # TODO: apakah perlu dibedakan?
    # NamaBerkas.laporan_operasi_rawat_jalan: lambda pages: src.multi_halaman(
    #     pages,
    # ),
}
