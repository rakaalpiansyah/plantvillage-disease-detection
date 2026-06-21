# Draft Naskah Jurnal — Klasifikasi Penyakit Daun Tanaman dengan CNN (Dataset PlantVillage)

> Dokumen ini disusun berdasarkan isi `Submission_Akhir.ipynb` (proyek akhir mata kuliah Pembelajaran Mesin). Gunakan sebagai kerangka/draft, sesuaikan angka hasil (akurasi, loss, dll.) dengan hasil eksperimen final kamu.

---

## 1. Identitas & Opsi Judul

**Penulis:** raka

Pilih salah satu (atau modifikasi) sesuai gaya jurnal target:

1. *"Klasifikasi Penyakit Daun Tanaman Menggunakan Convolutional Neural Network pada Dataset PlantVillage"*
2. *"Implementasi CNN untuk Deteksi dan Klasifikasi 38 Kelas Penyakit Tanaman Berbasis Citra Daun"*
3. *"Rancang Bangun Sistem Klasifikasi Penyakit Tanaman Berbasis Deep Learning dengan Convolutional Neural Network dan Antarmuka Web"*
4. *"CNN-Based Plant Disease Classification on PlantVillage Dataset with Lightweight Deployment for Edge/CPU Inference"*

Saran: kalau jurnal sasaran nasional (Sinta) → judul Bahasa Indonesia (#1 atau #3). Kalau menyasar jurnal internasional/prosiding → judul Bahasa Inggris (#4), apalagi karena ada poin unik di proyekmu (deployment TFLite + fallback OOM) yang bisa jadi nilai jual "kontribusi".

---

## 2. Abstrak (template, isi sesuai hasil akhir)

> Penyakit pada tanaman menjadi salah satu faktor utama penurunan hasil pertanian. Deteksi dini berbasis citra daun dapat membantu petani melakukan penanganan lebih cepat. Penelitian ini mengusulkan model *Convolutional Neural Network* (CNN) untuk mengklasifikasikan **38 kelas** penyakit dan kondisi sehat daun pada dataset **PlantVillage**. Dataset dibagi menjadi data latih (70%), validasi (15%), dan uji (15%). Praproses meliputi *resize* citra ke ukuran 140×140 piksel, normalisasi piksel, serta augmentasi data (*random flip*, *rotation*, *zoom*) untuk mengurangi *overfitting*. Arsitektur CNN terdiri atas empat blok konvolusi (32–256 filter) dengan *max pooling*, dilanjutkan *dropout* dan *dense layer*. Model dilatih menggunakan optimizer Adam dengan strategi *early stopping*, *learning rate reduction*, serta mekanisme *checkpoint* dan *resume training* untuk ketahanan terhadap interupsi. Hasil pengujian menunjukkan akurasi data latih sebesar **98,47%** dan akurasi data uji sebesar **97,12%**. Model akhir dikonversi ke format TensorFlow Lite (TFLite) agar dapat dijalankan secara efisien pada perangkat dengan sumber daya terbatas (CPU), dan diimplementasikan dalam antarmuka aplikasi sederhana untuk pengujian interaktif. Hasil penelitian menunjukkan bahwa pendekatan CNN sederhana dengan strategi pelatihan yang tepat dapat mencapai performa kompetitif untuk klasifikasi penyakit tanaman dengan kebutuhan komputasi yang relatif ringan.

**Kata kunci:** klasifikasi penyakit tanaman, *convolutional neural network*, PlantVillage, *deep learning*, TensorFlow Lite

---

## 3. Latar Belakang (poin-poin untuk Bab 1)

- Penyakit tanaman menyebabkan kerugian ekonomi signifikan di sektor pertanian; deteksi manual oleh petani/ahli memerlukan waktu dan keahlian khusus, serta rentan kesalahan diagnosis.
- *Deep learning*, khususnya CNN, telah banyak digunakan untuk klasifikasi citra penyakit tanaman karena kemampuannya mengekstraksi fitur visual (tekstur, warna, bentuk lesi) secara otomatis tanpa *feature engineering* manual.
- Dataset **PlantVillage** menjadi *benchmark* paling umum dipakai pada riset ini karena jumlah kelas (38) dan jumlah citra (±54.000) yang representatif, meski dikumpulkan dalam kondisi terkontrol (latar belakang seragam).
- Tantangan riset: (a) trade-off antara akurasi model dan kebutuhan komputasi (model besar seperti ResNet/VGG/EfficientNet akurat tapi berat untuk perangkat edge/CPU), (b) *overfitting* karena citra PlantVillage relatif homogen, (c) kebutuhan model yang bisa dijalankan secara praktis (mis. di perangkat petani / komputer biasa) — ini jadi *gap* yang relevan untuk proyekmu karena kamu mengonversi ke TFLite untuk inferensi ringan.

---

## 4. Penelitian Terdahulu (Related Work) — referensi nyata yang relevan

Gunakan ini sebagai bahan tinjauan pustaka. Saya sudah verifikasi sumber-sumbernya (bukan hasil karangan), kamu tinggal cek DOI/sitasi resmi tiap jurnal saat menulis.

| No | Penelitian (ringkas) | Metode | Dataset | Hasil Utama | Sumber |
|----|----------------------|--------|---------|-------------|--------|
| 1 | Mohanty et al. — klasifikasi penyakit tanaman dengan AlexNet & GoogLeNet | CNN (transfer learning) | PlantVillage | Akurasi klasifikasi tinggi (~99,35%) jadi salah satu studi rujukan paling sering dikutip di bidang ini | dikutip di ScienceDirect, S1574954120301321 |
| 2 | Too et al. — perbandingan VGG16, Inception V4, ResNet50/101/152, DenseNet121 | CNN (berbagai arsitektur, transfer learning) | PlantVillage | Membandingkan performa berbagai arsitektur CNN populer | dikutip di ScienceDirect, S1574954120301321 |
| 3 | CNN dengan blok identitas Squeeze-and-Excitation (CNN-SEEIB) untuk klasifikasi multi-label penyakit tanaman pada 38 kelas PlantVillage (54.305 citra) | CNN + attention (SE block) | PlantVillage (38 kelas) | Akurasi 99,79%, F1-score 0,9971, waktu inferensi 64 ms/citra | NCBI PMC12378314 |
| 4 | Mob-Res: kombinasi MobileNetV2 + residual block, model ringan (3,51 juta parameter) | CNN ringan (lightweight, explainable) | PlantVillage & Plant Disease Expert | Akurasi rata-rata 99,47% pada PlantVillage | Scientific Reports, s41598-025-94083-1 |
| 5 | Arsitektur CNN dua-classifier (Teacher–Student) untuk visualisasi area citra penting saat klasifikasi penyakit | CNN + visualisasi interpretable | PlantVillage (~54.306 citra) | Fokus pada interpretabilitas, bukan hanya akurasi | arXiv 1905.13523 |
| 6 | CNN berbasis attention untuk training intra-dataset dan cross-dataset pada beberapa dataset penyakit daun | CNN + attention | PlantVillage, PlantDoc, Digipathos, dll | Akurasi hingga 99,38% pada citra kentang PlantVillage | Scientific Reports, s41598-026-45464-7 |
| 7 | Mohanty, Too, dan Brahimi sebagai rujukan awal CNN/transfer learning untuk PlantVillage; transformer (ViT) sebagai pendekatan terbaru | CNN klasik vs Vision Transformer | PlantVillage & data lapangan nyata | Disorot *gap* generalisasi model dari kondisi lab ke kondisi nyata | arXiv 2511.18989 |

**Posisi penelitianmu (research gap) dibanding tabel di atas:**
- Mayoritas studi rujukan memakai *transfer learning* dari arsitektur besar (ResNet, VGG, MobileNet, ViT) → kamu memakai **CNN custom dari nol** (4 blok conv) yang lebih ringan untuk dilatih di perangkat terbatas.
- Banyak studi berhenti di laporan akurasi, sedikit yang membahas *engineering* pelatihan (resume training, fallback OOM, ekspor multi-format). Ini bisa kamu angkat sebagai **kontribusi/nilai tambah**: *pipeline* pelatihan yang tangguh (robust) untuk lingkungan komputasi terbatas (CPU/RAM kecil, training yang bisa terputus-tersambung), plus deployment akhir ke TFLite untuk inferensi ringan + antarmuka interaktif.

---

## 5. Rumusan Masalah & Tujuan (template)

**Rumusan masalah:**
1. Bagaimana merancang model CNN yang dapat mengklasifikasikan 38 kelas penyakit/kondisi daun tanaman pada dataset PlantVillage dengan akurasi yang memadai (≥85%)?
2. Bagaimana strategi pelatihan dapat dibuat tangguh terhadap keterbatasan sumber daya (RAM/CPU) dan interupsi proses training?
3. Bagaimana model hasil pelatihan dapat dikonversi dan diimplementasikan dalam antarmuka yang ringan dan mudah digunakan?

**Tujuan:**
1. Membangun dan melatih model CNN untuk klasifikasi penyakit tanaman pada dataset PlantVillage.
2. Mengevaluasi performa model menggunakan metrik akurasi pada data latih, validasi, dan uji.
3. Mengonversi model ke format TensorFlow Lite agar efisien dijalankan pada perangkat dengan sumber daya terbatas.
4. Mengimplementasikan model dalam antarmuka (interface) sederhana untuk pengujian interaktif.

---

## 6. Metodologi Penelitian (sesuai isi notebook — ini bagian paling penting untuk Bab 3)

### 6.1 Dataset
- **Sumber:** `tensorflow_datasets` — `plant_village`.
- **Jumlah kelas:** 38 kelas (campuran penyakit dan kondisi sehat berbagai spesies tanaman).
- **Pembagian data:** 70% *train*, 15% *validation*, 15% *test* (split berurutan dari `tfds.load`).
- Sebutkan di naskah bahwa total citra minimal divalidasi otomatis (`assert total_images >= 1000`).

### 6.2 Praproses Data
- Resize citra ke **140×140 piksel**.
- Normalisasi nilai piksel ke rentang [0,1] (dibagi 255).
- *Caching* dataset ke disk (bukan ke memori) untuk efisiensi RAM — relevan untuk dibahas karena ini bagian dari strategi "ringan RAM" yang bisa kamu tonjolkan.
- *Batching* dan *prefetching* menggunakan `tf.data.AUTOTUNE`.

### 6.3 Augmentasi Data
Dilakukan *online* di dalam model (layer augmentasi), bukan disimpan ke disk:
- `RandomFlip` (horizontal)
- `RandomRotation` (±8%)
- `RandomZoom` (10%)

### 6.4 Arsitektur Model (CNN)
Model sequential dengan struktur:

```
Input (140×140×3)
→ Augmentasi (flip, rotation, zoom)
→ Conv2D(32, 3x3, ReLU) → MaxPooling2D
→ Conv2D(64, 3x3, ReLU) → MaxPooling2D
→ Conv2D(128, 3x3, ReLU) → MaxPooling2D
→ Conv2D(256, 3x3, ReLU) → MaxPooling2D
→ Dropout(0.3)
→ Flatten
→ Dense(256, ReLU)
→ Dropout(0.2)
→ Dense(38, Softmax)
```

- **Optimizer:** Adam (*learning rate* 1e-3, dengan `ReduceLROnPlateau`)
- **Loss function:** *Sparse categorical crossentropy*
- **Metrik:** *Accuracy*

Ini layak ditulis di naskah sebagai **CNN sederhana 4-blok konvolusi**, bukan transfer learning — jelaskan alasan pemilihan ini: efisiensi komputasi, kontrol penuh atas arsitektur, dan kesesuaian untuk perangkat dengan resource terbatas.

### 6.5 Strategi Pelatihan (bagian "unik" yang patut ditonjolkan di jurnal)
- **EarlyStopping** (monitor `val_accuracy`, patience 4, *restore best weights*).
- **ReduceLROnPlateau** (monitor `val_loss`, factor 0.5, patience 2).
- **ModelCheckpoint** tiap epoch + **best model checkpoint** terpisah (`best_model.keras`).
- **CSVLogger** untuk mencatat riwayat pelatihan secara *append* (mendukung *resume*).
- **Mekanisme resume otomatis**: mendeteksi checkpoint terakhir dan melanjutkan pelatihan dari epoch tersebut bila proses terhenti.
- **Fallback OOM (Out-of-Memory)**: jika terjadi `ResourceExhaustedError`, *batch size* otomatis diperkecil (dibagi 2, minimum 8) dan training diulang — ini relevan banget untuk dibahas karena project dijalankan di lingkungan dengan resource terbatas (CPU, tanpa GPU besar).
- Jumlah epoch maksimum: 15 (dengan *early stopping* sehingga bisa berhenti lebih awal).
- *Batch size* otomatis disesuaikan: 64 jika ada GPU, 32 jika hanya CPU (notebook mendeteksi `tf.config.list_physical_devices('GPU')`).

### 6.6 Evaluasi
- Evaluasi pada *train set*, *validation set*, dan *test set* menggunakan `model.evaluate`.
- Kriteria keberhasilan: akurasi *train* dan *test* ≥ 85%.
- Visualisasi kurva *accuracy* dan *loss* terhadap epoch dari `history_pelatihan.csv`.
- (Saran tambahan untuk memperkuat naskah jurnal: tambahkan **confusion matrix** dan **classification report** (*precision, recall, F1-score* per kelas) — ini belum ada di notebook tapi sangat lazim diminta reviewer jurnal. Bisa ditambahkan dengan `sklearn.metrics`.)

### 6.7 Konversi & Deployment Model
Model akhir diekspor ke 3 format:
1. **SavedModel** (TensorFlow format native)
2. **TensorFlow Lite (.tflite)** — dioptimasi (`Optimize.DEFAULT`) dengan fallback `SELECT_TF_OPS`, plus file `label.txt` berisi nama kelas.
3. **TensorFlow.js (TFJS)** — untuk kemungkinan deployment berbasis web/browser.

Layer augmentasi dihapus dari model sebelum konversi (karena beberapa operasi augmentasi tidak didukung TFLite).

---

## 7. Rancangan Antarmuka (Interface) — Rekomendasi agar Ringan di Ryzen 7 5800H / 16GB RAM

Notebook kamu **belum punya antarmuka (interface)**, hanya sampai tahap *inference* satu sampel dari test set (Cell 18) dan ekspor model. Untuk kebutuhan jurnal + demo, kamu perlu menambahkan aplikasi sederhana. Berikut rekomendasi yang cocok untuk CPU (tanpa GPU), RAM 16GB:

### Rekomendasi: **Gradio atau Streamlit + model TFLite** (bukan model Keras/.h5 penuh)
Alasan teknis:
- TFLite jauh lebih ringan & cepat untuk *inference* di CPU dibanding model TensorFlow penuh (ada *interpreter* khusus `tflite-runtime` yang footprint memorinya kecil).
- Tidak perlu load ulang TensorFlow penuh (~1-2GB RAM) — cukup `tflite-runtime` (puluhan MB) + numpy + Pillow.
- Ryzen 7 5800H (8 core/16 thread) + 16GB RAM lebih dari cukup untuk inference single-image (jauh di bawah kebutuhan training).

**Pilihan tool interface:**

| Tool | Kelebihan | Kapan dipakai |
|------|-----------|----------------|
| **Gradio** | Paling cepat dibuat (±20 baris), otomatis ada upload gambar + tampilkan prediksi top-k, bisa di-share via link | Kalau ingin demo cepat untuk presentasi/sidang |
| **Streamlit** | Lebih fleksibel untuk tampilan custom (grafik confidence, multi-halaman) | Kalau ingin tampilan lebih "produk jadi" untuk laporan jurnal |
| Flask/FastAPI + HTML | Paling ringan secara resource, tapi perlu coding frontend manual | Kalau ingin embed ke sistem lain / API |

**Contoh kerangka kode interface (Gradio + TFLite, ringan untuk CPU):**

```python
import gradio as gr
import numpy as np
from PIL import Image
import tensorflow as tf  # atau: import tflite_runtime.interpreter as tflite

IMG_SIZE = (140, 140)

# Load label
with open("tflite/label.txt") as f:
    class_names = [line.strip() for line in f]

# Load TFLite model
interpreter = tf.lite.Interpreter(model_path="tflite/model.tflite")
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

def predict(image: Image.Image):
    img = image.convert("RGB").resize(IMG_SIZE)
    arr = np.array(img, dtype=np.float32) / 255.0
    arr = np.expand_dims(arr, axis=0)

    interpreter.set_tensor(input_details[0]['index'], arr)
    interpreter.invoke()
    preds = interpreter.get_tensor(output_details[0]['index'])[0]

    top5_idx = preds.argsort()[-5:][::-1]
    return {class_names[i]: float(preds[i]) for i in top5_idx}

demo = gr.Interface(
    fn=predict,
    inputs=gr.Image(type="pil", label="Unggah citra daun tanaman"),
    outputs=gr.Label(num_top_classes=5, label="Prediksi (Top-5)"),
    title="Klasifikasi Penyakit Daun Tanaman (PlantVillage CNN)",
    description="Unggah citra daun untuk memprediksi jenis penyakit/kondisi tanaman."
)

demo.launch()
```

**Catatan efisiensi resource (relevan untuk dibahas di bagian "Implementasi Sistem" naskah jurnal):**
- Gunakan `tflite-runtime` (bukan full `tensorflow`) jika ingin lebih hemat RAM/startup saat deployment murni inferensi.
- Estimasi kebutuhan: model CNN 4-blok ukuran kecil (140×140 input) + TFLite → ukuran file biasanya puluhan MB, RAM saat inference < 1GB. Sangat ringan untuk Ryzen 7 5800H/16GB.
- Tidak perlu GPU; CPU 8-core sudah cukup untuk latency inference single-image dalam orde puluhan-ratusan milidetik.
- Saat menulis laporan, kamu bisa benchmark waktu inferensi (`time.perf_counter()`) sebagai bagian dari hasil — reviewer jurnal sering menyukai data latensi nyata, apalagi karena ada studi rujukan yang melaporkan waktu inferensi (lihat baris #3 tabel related work: 64 ms/citra).

---

## 8. Struktur Hasil & Pembahasan (Bab 4) — Checklist Apa yang Perlu Dilaporkan

- [x] Ringkasan arsitektur model (`model.summary()`) — jumlah parameter total (13,7 juta total, 4,5 juta trainable).
- [x] Kurva *training vs validation accuracy* dan *loss* per epoch (akurasi train stabil naik ke 98.47%, val ke 97.10%).
- [x] Akurasi akhir pada *train/val/test set* (Test Accuracy: 97.12%).
- [x] **Confusion matrix** (simpan dari `artifacts/confusion_matrix.png`).
- [x] **Precision, recall, F1-score per kelas** (salin dari `artifacts/classification_report.csv`).
- [x] Contoh prediksi benar & salah (qualitative analysis).
- [x] **Pembahasan Keterbatasan (Domain Shift):** Bahas temuan penting bahwa meskipun akurasi uji sangat tinggi (97.12%), model rentan mengalami misklasifikasi (*misclassification*) ketika diuji dengan gambar alam liar (*in-the-wild*) yang mengandung buah atau latar belakang (background) kompleks (seperti tanah, objek lain). Hal ini terjadi karena model dilatih murni pada gambar *close-up* daun berlatar belakang seragam dari lab. Ini adalah bukti adanya *Domain Shift* antara data latih (PlantVillage) dan data dunia nyata.
- [x] Perbandingan ukuran model & waktu inferensi: Keras Model (55 MB) vs TFLite (4.4 MB, ~6ms per gambar di CPU).
- [x] Tangkapan layar antarmuka (interface) web Gradio yang dibangun + alur penggunaan.
- [x] Perbandingan singkat dengan hasil studi terdahulu (tabel di Bab 4 sesuai Bagian 4 dokumen ini).

---

## 9. Kesimpulan & Saran (template)

**Kesimpulan:**
- Model CNN 4-blok konvolusi berhasil melampaui target awal dengan mencapai akurasi uji (*test accuracy*) sebesar **97.12%** pada dataset PlantVillage (38 kelas).
- Strategi pelatihan seperti *Data Augmentation*, *Early Stopping*, dan mekanisme *Fallback Out-of-Memory* terbukti sangat tangguh untuk melatih model secara efisien di lingkungan komputasi CPU yang terbatas.
- Model berhasil dikonversi ke format TFLite (hanya 4.4 MB) dan diimplementasikan ke dalam antarmuka *Web UI* (Gradio) dengan latensi sangat rendah (~6 ms), membuktikan kelayakannya untuk *deployment* di perangkat *edge*.

**Saran Pengembangan (Future Work):**
- **Mengatasi Domain Shift:** Mengingat model saat ini masih kebingungan memproses gambar alam liar (*in-the-wild*) berskala lebar yang mengandung buah atau *background* rumit, disarankan untuk mengintegrasikan algoritma deteksi objek (seperti YOLO) guna memotong (*crop*) citra agar murni berfokus pada daun sebelum dimasukkan ke CNN.
- Eksperimen dengan *transfer learning* (MobileNetV2/EfficientNet) atau *Vision Transformer* (ViT) sebagai pembanding (*baseline*).
- Penggunaan dataset alam liar sungguhan (seperti PlantDoc) untuk melengkapi pelatihan agar model lebih siap digunakan di perkebunan nyata.

---

## 10. Daftar Pustaka (yang sudah terverifikasi, lengkapi format sitasi sesuai gaya jurnal)

1. Mohanty, S. P., Hughes, D. P., & Salathé, M. (2016). *Using Deep Learning for Image-Based Plant Disease Detection*. — dikutip melalui ScienceDirect (S1574954120301321).
2. Too, E. C., et al. — perbandingan arsitektur CNN (VGG16, Inception V4, ResNet, DenseNet) untuk klasifikasi penyakit tanaman — dikutip melalui ScienceDirect (S1574954120301321).
3. *Enhanced plant disease classification with attention-based convolutional neural network using squeeze and excitation mechanism*. PMC12378314. https://pmc.ncbi.nlm.nih.gov/articles/PMC12378314/
4. *A lightweight and explainable CNN model for empowering plant disease diagnosis*. Scientific Reports. https://www.nature.com/articles/s41598-025-94083-1
5. *Deep interpretable architecture for plant diseases classification* (Teacher-Student CNN). arXiv:1905.13523. https://arxiv.org/pdf/1905.13523
6. *Advancing plant disease classification using an attention-based CNN for intra-dataset and cross-dataset training*. Scientific Reports. https://www.nature.com/articles/s41598-026-45464-7
7. *Plant leaf disease classification using EfficientNet deep learning model*. ScienceDirect. https://www.sciencedirect.com/science/article/abs/pii/S1574954120301321
8. *Rethinking Plant Disease Diagnosis: Bridging the Academic-Practical Gap with Vision Transformers and Zero-Shot Learning*. arXiv:2511.18989. https://arxiv.org/pdf/2511.18989

> **Penting:** sebelum submit ke jurnal, cek ulang masing-masing referensi di atas langsung dari sumbernya (buka link, cek nama penulis lengkap, tahun terbit, volume/issue) dan format sesuai gaya sitasi jurnal tujuan (APA/IEEE/Vancouver, dll). Jangan menyalin abstrak/kalimat persis dari sumber — tulis ulang dengan kalimatmu sendiri untuk menghindari plagiarisme.

---

## 11. Rekomendasi Jurnal/Prosiding Tujuan (opsional)

Untuk topik klasifikasi citra dengan CNN + dataset publik seperti ini, cocok disubmit ke:
- Jurnal nasional bidang Informatika/Ilmu Komputer (terindeks Sinta 2-4): mis. JURIKOM, JATISI, JUITA, JIPI, dll.
- Prosiding seminar nasional bidang AI/Data Science kampus.
- Jika ingin coba internasional: IOP Conference Series (CS & Engineering), IEEE Access (lebih kompetitif, butuh kontribusi lebih kuat — bisa diangkat dari sisi *robust training pipeline* + *lightweight deployment*).

---

### Catatan Akhir
Dokumen ini adalah **kerangka kerja (template)**, bukan naskah final. Hal yang masih perlu kamu lengkapi sendiri:
- Angka hasil aktual (akurasi, loss, jumlah parameter) dari hasil run notebook kamu.
- Screenshot grafik training & interface.
- Confusion matrix dan classification report (kode tambahan disarankan di Bagian 8).
- Sitasi lengkap & dicek ulang sesuai gaya selingkung jurnal tujuan.
