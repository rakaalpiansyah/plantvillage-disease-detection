# PROJECT_PLAN — Tech Stack & Kesesuaian dengan Draft Jurnal

## 0. Jawaban singkat: apakah draft MD kemarin sudah sesuai?

**Sudah sesuai secara konsep** (judul, related work, metodologi, alur evaluasi semuanya
masih relevan dan tidak berubah). Yang **berubah/ditambah** karena sekarang
dikembangkan sebagai proyek Python biasa (bukan notebook):

| Bagian di draft MD sebelumnya | Status setelah jadi project Python |
|---|---|
| Bab 6.1–6.5 (dataset, praproses, arsitektur, training) | **Tidak berubah** secara konsep — hanya dipecah jadi modul (`src/data.py`, `src/model.py`, `src/train.py`) |
| Bab 6.6 Evaluasi | **Diperkuat** — confusion matrix & classification report yang kemarin baru "disarankan" sekarang sudah jadi kode jadi (`src/evaluate.py`) |
| Bab 6.7 Konversi & Deployment | **Tidak berubah** — tetap SavedModel → TFLite → TFJS, sekarang di `src/export.py` |
| Bab 7 Rancangan Interface | **Direalisasikan** — kode Gradio + TFLite yang kemarin baru contoh kerangka, sekarang jadi `app.py` yang langsung bisa dijalankan |
| Bab 4 (related work), Bab 10 (daftar pustaka) | **Tidak berubah**, masih berlaku apa adanya |

Jadi: **tidak perlu menulis ulang draft jurnal dari nol**. Tinggal update bagian
"Implementasi Sistem"/Bab 3-4 di naskah supaya menyebutkan proyek ini sebagai
implementasi dalam bentuk modular Python (bukan notebook tunggal), karena ini
justru poin plus untuk reproducibility (lazim dilirik baik oleh reviewer jurnal).

---

## 1. Tech Stack Lengkap

| Layer | Teknologi | Alasan Pemilihan |
|---|---|---|
| Bahasa | Python 3.10/3.11 | Standar untuk ML/data science |
| Deep learning framework | TensorFlow (CPU) 2.16.1 + Keras | Sama dengan notebook asli, paling banyak dukungan tutorial untuk skripsi/jurnal di Indonesia |
| Dataset | `tensorflow_datasets` (`plant_village`) | Dataset publik, sudah terstandar, mudah dikutip |
| Preprocessing pipeline | `tf.data` (cache ke disk, `AUTOTUNE`) | Hemat RAM — penting untuk environment dengan RAM terbatas |
| Augmentasi | `tf.keras.layers.RandomFlip/RandomRotation/RandomZoom` | Augmentasi *online*, tidak perlu simpan citra baru ke disk |
| Model | CNN custom 4 blok konvolusi (32→256 filter) | Ringan untuk dilatih di CPU dibanding model transfer-learning besar |
| Training utilities | `EarlyStopping`, `ReduceLROnPlateau`, `ModelCheckpoint`, `CSVLogger` | Standar Keras, mendukung resume training & mencegah overfitting |
| Evaluasi | `scikit-learn` (`confusion_matrix`, `classification_report`), `matplotlib` | Standar evaluasi klasifikasi multi-kelas untuk laporan jurnal |
| Format model deployment | TFLite (utama), SavedModel, TFJS (opsional) | TFLite paling ringan untuk inferensi CPU; TFJS untuk kemungkinan demo web tanpa server |
| Interface | **Gradio** | Paling cepat dibangun, otomatis sediakan UI upload gambar + bisa langsung dipakai untuk demo sidang/laporan |
| Environment target | CPU (Ryzen 7 5800H, 16GB RAM, tanpa GPU) | Semua keputusan teknis (batch size, cache disk, TFLite) diarahkan ke sini |

### Mengapa bukan PyTorch / transfer learning besar (ResNet, EfficientNet, ViT)?
Karena notebook aslinya sudah berbasis TensorFlow/Keras dan CNN custom — mengganti
framework di tengah jalan akan membuat hasil training sebelumnya (kalau ada) tidak
bisa dipakai lagi, dan tidak menambah nilai untuk tujuan tugas akhir kuliah. Kalau
target jurnalmu internasional dan ingin "kontribusi lebih besar", baru pertimbangkan
menambahkan **perbandingan** dengan MobileNetV2 (transfer learning) sebagai baseline
kedua — ini bisa jadi eksperimen tambahan, bukan pengganti arsitektur utama.

---

## 2. Estimasi Kebutuhan Resource (Ryzen 7 5800H, 16GB RAM)

| Tahap | Perkiraan RAM | Catatan |
|---|---|---|
| Download & prepare dataset (TFDS) | 1–3 GB sementara | Tergantung ukuran dataset PlantVillage (±54.000 citra), disimpan ke disk bukan RAM |
| Training (CPU, batch_size=32, img 140×140) | 2–6 GB | Cache `tf.data` ke disk (`.cache(path)`) membuat training tidak menumpuk semua citra di RAM |
| Evaluasi + confusion matrix | < 2 GB | Hanya prediksi batch demi batch |
| Ekspor TFLite | < 1 GB | Proses konversi, sekali jalan |
| **Interface (`app.py`, TFLite)** | **< 1 GB** | Paling ringan dari semua tahap — inilah yang membuat TFLite dipilih untuk deployment |

8 core/16 thread Ryzen 7 5800H cukup untuk training CNN 4-blok ini, hanya akan
lebih lambat per-epoch dibanding GPU (training bisa berjam-jam untuk 15 epoch
penuh tergantung ukuran dataset — pertimbangkan mengurangi `EPOCHS` atau memakai
subset data dulu untuk eksperimen cepat sebelum run penuh).

---

## 3. Checklist Pengembangan Selanjutnya

- [x] Jalankan `python -m src.train` penuh, catat waktu training per epoch (data ini bagus untuk dilaporkan di jurnal sebagai bukti efisiensi di CPU).
- [x] Jalankan `python -m src.evaluate`, simpan `confusion_matrix.png` dan `classification_report.csv` — masukkan ke naskah jurnal sebagai Gambar/Tabel hasil.
- [x] Jalankan `python -m src.export`, lalu `python app.py` — ambil screenshot interface untuk bagian "Implementasi Sistem".
- [x] Tambahkan benchmark waktu inferensi (`app.py` sudah otomatis menampilkan ini per prediksi) sebagai data kuantitatif tambahan.
- [x] Lakukan Studi Ablasi (menggunakan `rembg`) untuk menganalisis domain shift dan membuktikan adanya **Clever Hans Effect** pada model yang dilatih dengan dataset PlantVillage.
- [x] Update naskah jurnal menjadi versi komprehensif (`Paper_CoreID_Klasifikasi_Penyakit_Tanaman_CNN.md`), lalu buat script Python (`generate_paper.py`) untuk otomatis mengekspor ke format `.docx` (template CoreID, IEEE style, 25 referensi).
