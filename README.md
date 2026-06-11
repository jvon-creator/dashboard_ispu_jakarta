# Dashboard ISPU Jakarta — Tugas 6 Business Intelligence

Dashboard ini dibuat dengan Python Streamlit untuk mendemonstrasikan analisis kualitas udara DKI Jakarta berdasarkan clean dataset ISPU hasil Tugas 3–5.

## Isi Dashboard

Dashboard memuat 5 visualisasi interaktif sesuai kebutuhan asesmen:

1. **Overview Kualitas Udara Jakarta**  
   KPI rata-rata ISPU, persentase Tidak Sehat+, pencemar dominan, stasiun prioritas, peta/ringkasan kondisi terkini per SPKU.

2. **Tren Temporal Kualitas Udara**  
   Grafik tren ISPU dengan granularitas harian, bulanan, atau tahunan, serta identifikasi tahun terbaik dan terburuk.

3. **Perbandingan Kualitas Udara Antar Stasiun**  
   Perbandingan rata-rata ISPU dan distribusi kategori udara antar 5 SPKU.

4. **Analisis Parameter Pencemar Kritis**  
   Komposisi pencemar kritis, tren kemunculan per tahun, dan perbandingan karakteristik pencemar antar stasiun.

5. **Pola Musiman Kualitas Udara**  
   Heatmap bulan-tahun dan grafik bulanan untuk menemukan periode dengan polusi tertinggi.

Setiap visualisasi dilengkapi narasi **Analisis utama** dan **Insight tindak lanjut** yang dapat digunakan saat presentasi.

## Struktur Folder

```text
dashboard_ispu_jakarta_dark_tugas_6/
├── app.py
├── requirements.txt
├── README.md
├── .streamlit/
│   └── config.toml
└── data/
    └── ispu_jakarta_bersih.csv
```

## Cara Menjalankan Lokal

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Cara Deploy ke Streamlit Cloud

1. Buat repository baru di GitHub.
2. Upload seluruh isi folder ini ke repository tersebut.
3. Buka Streamlit Cloud.
4. Pilih repository dan arahkan ke file `app.py`.
5. Klik **Deploy**.

## Catatan Data

Dataset yang digunakan adalah clean dataset hasil validasi Tugas 3–5. Grain data adalah **1 baris = 1 tanggal + 1 stasiun SPKU**. Dashboard bersifat deskriptif-diagnostik, sehingga penjelasan penyebab polusi membutuhkan data tambahan seperti meteorologi, lalu lintas, industri, dan sumber emisi lain.
