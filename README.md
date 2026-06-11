# Dashboard ISPU Jakarta — Tugas 6 Business Intelligence

Dashboard ini dibuat menggunakan **Python Streamlit** untuk mendemonstrasikan analisis Business Intelligence kualitas udara DKI Jakarta berbasis dataset ISPU yang telah dibersihkan pada Tugas 3–5.

## Isi Dashboard

Dashboard memuat 5 visualisasi interaktif sesuai kebutuhan asesmen:

1. **Overview Kualitas Udara Jakarta**  
   KPI utama: rata-rata ISPU, persentase Tidak Sehat+, pencemar dominan, dan ringkasan kondisi terkini per stasiun.

2. **Tren Temporal Kualitas Udara**  
   Tren ISPU harian, bulanan, atau tahunan yang dapat difilter per stasiun serta identifikasi tahun terbaik dan terburuk.

3. **Perbandingan Kualitas Udara Antar Stasiun**  
   Perbandingan rata-rata ISPU, persentase Tidak Sehat+, dan distribusi kategori udara antar 5 SPKU.

4. **Analisis Parameter Pencemar Kritis**  
   Komposisi dan tren kemunculan PM10, PM2.5, O3, CO, SO2, dan NO2 sebagai pencemar dominan.

5. **Pola Musiman Kualitas Udara**  
   Heatmap bulan-tahun dan profil bulanan untuk mengidentifikasi periode dengan polusi tertinggi.

Setiap visualisasi dilengkapi dengan **Analisis Utama** dan **Insight Tindak Lanjut** yang dapat digunakan Dinas Lingkungan Hidup DKI Jakarta.

## Struktur Folder

```text
.
├── app.py
├── requirements.txt
├── README.md
├── .streamlit/
│   └── config.toml
└── data/
    └── ispu_jakarta_bersih.csv
```

## Cara Menjalankan di Lokal

1. Buat virtual environment, lalu aktifkan.

```bash
python -m venv .venv
source .venv/bin/activate      # macOS/Linux
.venv\Scripts\activate         # Windows
```

2. Install dependencies.

```bash
pip install -r requirements.txt
```

3. Jalankan Streamlit.

```bash
streamlit run app.py
```

## Deploy ke Streamlit Cloud

1. Buat repository baru di GitHub.
2. Upload seluruh isi folder ini ke repository.
3. Buka Streamlit Cloud.
4. Pilih repository dan branch yang digunakan.
5. Pada bagian main file path, isi:

```text
app.py
```

6. Klik **Deploy**.

## Catatan Presentasi

Saat demo kepada asesor, gunakan alur berikut:

1. Mulai dari filter rentang tanggal dan stasiun di sidebar.
2. Tunjukkan KPI utama pada halaman awal.
3. Buka tab Visualisasi 1 sampai Visualisasi 5 secara berurutan.
4. Pada setiap tab, jelaskan grafik, kemudian bacakan bagian **Analisis Utama** dan **Insight Tindak Lanjut**.
5. Akhiri dengan menampilkan fitur unduh data hasil filter.

## Data

Dashboard menggunakan clean dataset hasil proses validasi dan pembersihan pada Tugas 3–5. Grain data adalah:

```text
1 baris = 1 tanggal + 1 stasiun SPKU
```
