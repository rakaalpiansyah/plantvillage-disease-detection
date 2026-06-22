# Klasifikasi Penyakit Daun Tanaman (PlantVillage) — Versi Python Project

Konversi dari `Submission_Akhir.ipynb` (notebook tugas akhir Pembelajaran Mesin) menjadi proyek Python modular, siap dikembangkan lebih lanjut dan dipakai sebagai dasar naskah jurnal.

**🏆 Performa Akhir Model:**
- **Akurasi Validasi:** 97.10%
- **Akurasi Pengujian (Test):** 97.12%
- **Arsitektur:** Custom CNN (4 Blok Konvolusi)
- **Deployment:** TensorFlow Lite (Ringan, inferensi CPU dalam ~6ms)

## Struktur Proyek

```
plant_disease_classifier/
├── config.py              # Semua konfigurasi terpusat (path, hyperparameter)
├── requirements.txt
├── app.py                  # Interface Gradio (pakai model TFLite, ringan di CPU)
├── src/
│   ├── data.py              # Load & praproses dataset PlantVillage (TFDS)
│   ├── model.py              # Arsitektur CNN 4 blok konvolusi
│   ├── train.py               # Training + resume checkpoint + fallback OOM
│   ├── evaluate.py            # Akurasi, confusion matrix, classification report
│   └── export.py              # Ekspor ke SavedModel / TFLite / TFJS
├── checkpoints/             # (otomatis dibuat) checkpoint training
├── artifacts/                # (otomatis dibuat) model hasil ekspor
└── logs/                       # (otomatis dibuat) history_pelatihan.csv
```

## Instalasi dan Persiapan Dataset

Karena dataset utama dari Mendeley TFDS seringkali diblokir (Error 403), kita mengunduh *source* aslinya langsung dari GitHub.

```bash
# 1. Buat dan aktifkan virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\activate

# 2. Install library yang dibutuhkan
pip install -r requirements.txt

# 3. Download Dataset PlantVillage asli (hanya perlu sekali)
git clone --depth 1 https://github.com/spMohanty/PlantVillage-Dataset.git dataset_temp
mkdir dataset
mv dataset_temp/raw/color dataset/color
rm -rf dataset_temp
```

> Catatan: `tensorflow-cpu` dipakai (bukan `tensorflow` biasa) karena proyek ini ditarget berjalan murni di CPU (mis. Ryzen 7 5800H, 16GB RAM), tanpa perlu GPU mahal.

## Urutan Menjalankan

```bash
# 1) Training (otomatis resume kalau ada checkpoint sebelumnya)
python -m src.train

# 2) Evaluasi (akurasi, confusion matrix, classification report, kurva training)
python -m src.evaluate

# 3) Ekspor model ke SavedModel + TFLite + label.txt (+ TFJS opsional)
python -m src.export

# 4) Jalankan interface web (pakai model TFLite hasil export)
python app.py
```

Setelah `python app.py` dijalankan, buka URL lokal yang muncul di terminal (default `http://127.0.0.1:7860`) di browser. 
Aplikasi akan menampilkan antarmuka cerdas dengan daftar 14 tanaman yang didukung (mencakup 38 kelas), serta terjemahan status daun (sehat/berpenyakit) secara interaktif.

## Catatan Penting: Domain Shift & Clever Hans Effect

Model ini dilatih pada dataset PlantVillage yang berisi **gambar daun close-up dengan latar belakang lab yang seragam**.
Melalui **Studi Ablasi** menggunakan algoritma segmentasi latar belakang (`rembg`), kami menemukan bahwa model mengalami fenomena **Clever Hans Effect**.

Ketika latar belakang asli dihapus dan diganti dengan warna solid abu-abu digital murni, akurasi model turun secara drastis (sekitar 26.3% sampel mengalami misklasifikasi). Hal ini membuktikan bahwa CNN tidak hanya mempelajari fitur patologis daun (bercak/lesi), tetapi juga 'menghafal' tekstur dan pola pencahayaan dari latar belakang dataset PlantVillage.
Ini adalah temuan krusial yang memvalidasi kelemahan model *in-vitro* ketika dihadapkan pada data alam liar (*in-the-wild*), dan menjadi kontribusi analitis utama dalam paper jurnal yang dihasilkan.

## Untuk Penulisan Jurnal

File paper komprehensif sudah di-generate secara otomatis! Anda dapat menjalankan `generate_paper.py` untuk membuat file `.docx` siap pakai yang formatnya sudah disesuaikan dengan template CoreID Journal (IEEE style, 25 referensi).

* File hasil: `Paper_CoreID_v2_Komprehensif.docx`
* Naskah Markdown asli: `Paper_CoreID_Klasifikasi_Penyakit_Tanaman_CNN.md`
