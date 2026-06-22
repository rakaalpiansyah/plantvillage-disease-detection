# Klasifikasi Penyakit Daun Tanaman Menggunakan Convolutional Neural Network pada Dataset PlantVillage dengan Deployment Lightweight untuk Inferensi Edge

**Raka Alpiansyah**

Program Studi Informatika, Universitas XYZ
Email: raka@email.com

---

**Abstrak** — Penyakit pada tanaman menjadi salah satu faktor utama penurunan hasil pertanian global. Deteksi dini berbasis citra daun menggunakan kecerdasan buatan dapat membantu petani melakukan penanganan secara lebih cepat dan akurat. Penelitian ini mengusulkan model *Convolutional Neural Network* (CNN) dengan arsitektur empat blok konvolusi untuk mengklasifikasikan 38 kelas penyakit dan kondisi sehat daun pada dataset PlantVillage. Dataset yang terdiri dari 54.305 citra dibagi menjadi data latih (80%), validasi (10%), dan uji (10%) menggunakan *stratified split*. Praproses meliputi *resize* citra ke 140×140 piksel, normalisasi piksel, serta augmentasi data (*random flip, rotation, zoom*). Model dilatih menggunakan *optimizer* Adam dengan strategi *Early Stopping*, *ReduceLROnPlateau*, serta mekanisme *Fallback Out-of-Memory* untuk ketahanan di lingkungan komputasi terbatas. Hasil pengujian menunjukkan akurasi data latih sebesar 98,47% dan akurasi data uji sebesar 97,12%. Model dikonversi ke format TensorFlow Lite (4,4 MB) dan diimplementasikan dalam antarmuka web Gradio dengan latensi ~6 ms per citra. Studi ablasi terhadap 38 sampel citra *in-vitro* yang diproses menggunakan segmentasi U-Net (rembg) mengungkap fenomena *Clever Hans Effect*, di mana CNN terbukti mengalami *overfitting* pada tekstur latar belakang dataset, bukan pada fitur patologis daun. Temuan ini menegaskan keterbatasan fundamental dataset PlantVillage untuk aplikasi dunia nyata dan menjadi landasan kritis bagi pengembangan arsitektur *two-stage pipeline* di masa depan.

**Kata kunci:** klasifikasi penyakit tanaman, *convolutional neural network*, PlantVillage, *deep learning*, TensorFlow Lite, *domain shift*

---

## I. PENDAHULUAN

Penyakit tanaman merupakan salah satu ancaman paling serius terhadap ketahanan pangan global. Menurut data Food and Agriculture Organization (FAO), penyakit tanaman menyebabkan kerugian hasil panen sebesar 20-40% setiap tahunnya di seluruh dunia [1]. Deteksi dini penyakit tanaman secara tradisional masih sangat bergantung pada inspeksi visual oleh ahli agronomi, yang memerlukan waktu, biaya, dan keahlian khusus, serta rentan terhadap kesalahan diagnosis subjektif.

Perkembangan pesat di bidang *deep learning*, khususnya *Convolutional Neural Network* (CNN), telah membuka paradigma baru dalam klasifikasi citra penyakit tanaman secara otomatis. CNN memiliki kemampuan unggul dalam mengekstraksi fitur visual hierarkis (tekstur, warna, bentuk lesi) secara otomatis tanpa memerlukan rekayasa fitur manual (*feature engineering*) [2]. Dataset PlantVillage, yang berisi 54.305 citra daun dari 14 spesies tanaman dengan 38 kelas penyakit dan kondisi sehat, telah menjadi *benchmark* paling umum dalam riset klasifikasi penyakit tanaman berbasis *deep learning* [3].

Meskipun berbagai arsitektur CNN seperti ResNet, VGG, dan EfficientNet telah mencapai akurasi tinggi pada dataset ini, sebagian besar model tersebut memiliki jumlah parameter yang sangat besar sehingga tidak efisien untuk dijalankan pada perangkat *edge* atau CPU dengan sumber daya terbatas [4]. Selain itu, mayoritas penelitian terdahulu berhenti pada pelaporan metrik akurasi tanpa membahas aspek rekayasa pelatihan (*training engineering*) seperti ketahanan terhadap interupsi, manajemen memori, dan *deployment* model ke format ringan [5].

Penelitian ini bertujuan untuk: (1) membangun model CNN empat blok konvolusi yang ringan namun kompetitif untuk mengklasifikasikan 38 kelas penyakit tanaman, (2) menerapkan strategi pelatihan yang tangguh (*robust*) terhadap keterbatasan sumber daya komputasi, (3) mengonversi dan men-*deploy* model ke format TensorFlow Lite dengan antarmuka web interaktif, dan (4) melakukan studi ablasi untuk menganalisis kerentanan model terhadap *domain shift* antara citra laboratorium dan kondisi dunia nyata.

---

## II. TINJAUAN PUSTAKA

Klasifikasi penyakit tanaman menggunakan CNN telah diteliti secara ekstensif dalam lima tahun terakhir. Tabel I menyajikan ringkasan penelitian terdahulu yang relevan.

**Tabel I. Perbandingan Penelitian Terdahulu**

| No | Peneliti (Tahun) | Metode | Dataset | Akurasi |
|----|-----------------|--------|---------|---------|
| 1 | Chen et al. (2025) [2] | CNN + attention (SE Block) | PlantVillage (38 kelas) | 99,79% |
| 2 | Kumar & Singh (2024) [3] | MobileNetV2 + Residual | PlantVillage & PlantDoc | 99,47% |
| 3 | Li et al. (2025) [4] | USENet (MobileNetV3 + SPP) | PlantVillage | F1: 0,993 |
| 4 | Rahman et al. (2025) [5] | TensorFlow CNN + Flask | PlantVillage | 96,9% |
| 5 | Wang & Zhang (2024) [6] | DenseNet + Segmented Images | PlantVillage | 98,17% |
| 6 | Zhao et al. (2025) [7] | ViT + MoE | PlantVillage & PlantDoc | 97,2% |

Berdasarkan tinjauan pustaka di atas, dapat diidentifikasi beberapa *research gap* berikut:

1. Mayoritas penelitian menggunakan arsitektur *transfer learning* dari model besar (ResNet, VGG, MobileNet) yang membutuhkan sumber daya komputasi tinggi, sementara pengembangan CNN *custom* yang ringan dan efisien untuk perangkat terbatas masih minim.
2. Aspek rekayasa pelatihan seperti *resume training*, *fallback Out-of-Memory* (OOM), dan konversi multi-format jarang dibahas dalam literatur.
3. Analisis kritis terhadap kerentanan model CNN yang dilatih pada dataset laboratorium (*in-vitro*) terhadap fenomena *domain shift* masih terbatas, padahal hal ini krusial untuk implementasi di dunia nyata.

---

## III. METODE PENELITIAN

### A. Dataset

Penelitian ini menggunakan dataset PlantVillage yang bersumber dari `tensorflow_datasets`. Dataset terdiri dari 54.305 citra daun tanaman yang mencakup 14 spesies dengan total 38 kelas (kombinasi jenis tanaman dan kondisi penyakit/sehat). Pembagian data dilakukan secara stratified dengan rasio 80% data latih, 10% data validasi, dan 10% data uji untuk memastikan setiap kelas terwakili secara proporsional.

### B. Praproses Data

Tahap praproses meliputi langkah-langkah berikut:

1. **Resize citra** ke dimensi 140×140 piksel untuk menyeragamkan ukuran input.
2. **Normalisasi piksel** ke rentang [0, 1] dengan membagi nilai piksel dengan 255.
3. **Konversi ruang warna** secara eksplisit ke RGB menggunakan `img.convert("RGB")` untuk mencegah inkonsistensi format (BGR vs RGB).
4. **Caching dataset** ke disk (bukan memori) menggunakan `tf.data.cache()` untuk efisiensi RAM.
5. **Batching dan prefetching** menggunakan `tf.data.AUTOTUNE` untuk optimasi *pipeline* I/O.

### C. Augmentasi Data

Augmentasi dilakukan secara *online* (di dalam arsitektur model) menggunakan *layer* augmentasi Keras, sehingga tidak memerlukan penyimpanan salinan gambar tambahan ke disk:

- `RandomFlip` (horizontal)
- `RandomRotation` (±8%)
- `RandomZoom` (10%)

### D. Arsitektur Model CNN

Model menggunakan arsitektur *sequential* CNN empat blok konvolusi yang dirancang secara *custom* (bukan *transfer learning*). Arsitektur lengkap ditampilkan pada Gambar 1.

```
Input (140×140×3)
→ Augmentasi (Flip, Rotation, Zoom)
→ Conv2D(32, 3×3, ReLU, padding=same) → MaxPooling2D
→ Conv2D(64, 3×3, ReLU, padding=same) → MaxPooling2D
→ Conv2D(128, 3×3, ReLU, padding=same) → MaxPooling2D
→ Conv2D(256, 3×3, ReLU, padding=same) → MaxPooling2D
→ Dropout(0.3)
→ Flatten
→ Dense(256, ReLU) → Dropout(0.2)
→ Dense(38, Softmax)
```

**Gambar 1.** Arsitektur CNN empat blok konvolusi yang diusulkan.

Model dikompilasi menggunakan *optimizer* Adam (*learning rate* = 1×10⁻³), fungsi *loss* Sparse Categorical Crossentropy, dan metrik akurasi. Total parameter model adalah 13,7 juta (4,5 juta *trainable*).

### E. Strategi Pelatihan

Penelitian ini menerapkan beberapa strategi pelatihan untuk memastikan ketangguhan proses di lingkungan komputasi terbatas:

1. **Early Stopping:** Memantau `val_accuracy` dengan *patience* 4 epoch dan *restore best weights*.
2. **ReduceLROnPlateau:** Memantau `val_loss` dengan faktor reduksi 0,5 dan *patience* 2 epoch.
3. **ModelCheckpoint:** Menyimpan *checkpoint* terbaik (`best_model.keras`) secara terpisah setiap epoch.
4. **CSVLogger:** Mencatat riwayat pelatihan secara *append* untuk mendukung mekanisme *resume*.
5. **Resume Training:** Mendeteksi *checkpoint* terakhir secara otomatis dan melanjutkan pelatihan dari epoch tersebut jika proses terhenti.
6. **Fallback OOM:** Jika terjadi `ResourceExhaustedError`, *batch size* otomatis diperkecil (dibagi 2, minimum 8) dan pelatihan diulang tanpa intervensi manual.

Jumlah epoch maksimum ditetapkan 15 dengan *batch size* 32 (CPU) atau 64 (GPU).

### F. Konversi dan Deployment Model

Model akhir diekspor ke tiga format:

1. **SavedModel** (format native TensorFlow)
2. **TensorFlow Lite (.tflite)** dengan optimasi `Optimize.DEFAULT` dan *fallback* `SELECT_TF_OPS`
3. **TensorFlow.js (TFJS)** untuk potensi *deployment* berbasis browser

Layer augmentasi dihapus dari model sebelum konversi karena beberapa operasi augmentasi tidak didukung oleh runtime TFLite. Antarmuka web dibangun menggunakan framework Gradio dengan fitur unggah citra, klasifikasi Top-5, dan diagnosis otomatis.

### G. Studi Ablasi: Analisis Domain Shift

Untuk menganalisis kerentanan model terhadap *domain shift*, dilakukan studi ablasi menggunakan algoritma segmentasi U-Net (pustaka `rembg`) sebagai *preprocessing* tambahan. Eksperimen dilakukan pada 38 sampel citra dari dataset PlantVillage dengan dua skenario:

- **Skenario 1 (CNN Murni):** Citra asli langsung diklasifikasikan oleh model TFLite.
- **Skenario 2 (rembg + CNN):** Latar belakang citra dihapus menggunakan `rembg`, diganti dengan warna solid abu-abu (RGB: 180, 180, 180), kemudian diklasifikasikan oleh model TFLite yang sama.

---

## IV. HASIL DAN PEMBAHASAN

### A. Hasil Pelatihan Model

Model CNN empat blok konvolusi berhasil dilatih selama 15 epoch. Kurva pelatihan menunjukkan konvergensi yang stabil tanpa indikasi *overfitting* yang signifikan. Ringkasan hasil pelatihan ditampilkan pada Tabel II.

**Tabel II. Hasil Evaluasi Model CNN**

| Metrik | Nilai |
|--------|-------|
| Akurasi Data Latih (*Training Accuracy*) | 98,47% |
| Akurasi Data Validasi (*Validation Accuracy*) | 97,10% |
| Akurasi Data Uji (*Test Accuracy*) | 97,12% |
| Ukuran Model Keras (.keras) | 55 MB |
| Ukuran Model TFLite (.tflite) | 4,4 MB |
| Waktu Inferensi per Citra (CPU) | ~6 ms |
| Total Parameter | 13.700.000 |
| Parameter *Trainable* | 4.500.000 |

Akurasi uji sebesar 97,12% melampaui target minimum yang ditetapkan (85%) dan kompetitif dibandingkan dengan penelitian terdahulu yang menggunakan arsitektur jauh lebih kompleks [2][3]. Reduksi ukuran model dari 55 MB (Keras) menjadi 4,4 MB (TFLite) menunjukkan efektivitas kuantisasi untuk *deployment* pada perangkat *edge*.

### B. Perbandingan dengan Penelitian Terdahulu

**Tabel III. Perbandingan Performa dengan Studi Terdahulu**

| Peneliti | Arsitektur | Parameter | Ukuran Model | Akurasi |
|----------|-----------|-----------|-------------|---------|
| Chen et al. [2] | CNN + SE Block | >20 juta | ~80 MB | 99,79% |
| Kumar & Singh [3] | MobileNetV2 | 3,51 juta | ~14 MB | 99,47% |
| Li et al. [4] | USENet | ~41 ribu | ~0,5 MB | F1: 0,993 |
| **Penelitian ini** | **CNN 4-Blok** | **4,5 juta** | **4,4 MB** | **97,12%** |

Meskipun akurasi model yang diusulkan sedikit lebih rendah dibandingkan arsitektur *state-of-the-art* seperti CNN-SE Block (99,79%) dan MobileNetV2 (99,47%), model ini menawarkan keunggulan dalam hal kesederhanaan arsitektur, kemudahan reproduksi, dan ukuran model TFLite yang sangat ringan (4,4 MB) untuk *deployment* pada perangkat terbatas.

### C. Hasil Studi Ablasi

Hasil studi ablasi yang membandingkan prediksi CNN murni dengan pipeline rembg + CNN pada 38 sampel citra *in-vitro* PlantVillage ditampilkan pada Tabel IV (sampel representatif).

**Tabel IV. Hasil Studi Ablasi (Sampel Representatif)**

| Citra | Skenario 1 (CNN) | Conf. | Skenario 2 (rembg+CNN) | Conf. | Status |
|-------|------------------|-------|----------------------|-------|--------|
| Apple_healthy | Class_3 (✓) | 100% | Class_24 (✗) | 74,8% | Turun |
| Apple_Apple_scab | Class_0 (✓) | 100% | Class_13 (✗) | 59,5% | Turun |
| Tomato_Bacterial_spot | Class_28 (✓) | 100% | Class_28 (✓) | 99,5% | Stabil |
| Grape_Black_rot | Class_11 (✓) | 99,9% | Class_11 (✓) | 97,9% | Stabil |
| Corn_healthy | Class_10 (✓) | 100% | Class_24 (✗) | 52,0% | Turun |
| Strawberry_Leaf_scorch | Class_26 (✓) | 100% | Class_26 (✓) | 100% | Stabil |
| Peach_Bacterial_spot | Class_16 (✓) | 100% | Class_16 (✓) | 100% | Stabil |
| Cherry_healthy | Class_6 (✓) | 100% | Class_19 (✗) | 100% | Turun |
| Tomato_healthy | Class_37 (✓) | 100% | Class_37 (✓) | 38,8% | Turun |

Dari 38 sampel, CNN murni berhasil mengklasifikasikan semua citra dengan benar (akurasi 100% pada data asli PlantVillage). Namun, setelah latar belakang dihapus menggunakan rembg dan diganti dengan warna solid abu-abu, **10 dari 38 sampel (26,3%) mengalami misklasifikasi**, sementara beberapa citra yang tetap benar menunjukkan penurunan tingkat kepercayaan yang signifikan.

### D. Pembahasan: Fenomena Clever Hans Effect

Temuan studi ablasi ini mengungkap fenomena yang dikenal dalam literatur *machine learning* sebagai **Clever Hans Effect** [8]. Model CNN yang dilatih pada dataset PlantVillage ternyata tidak sepenuhnya belajar mengidentifikasi fitur patologis daun (bercak, lesi, perubahan warna), melainkan turut "menghafal" pola tekstur, bayangan, dan gradien pencahayaan pada latar belakang kertas abu-abu yang menjadi ciri khas dataset tersebut.

Ketika `rembg` menghapus latar belakang asli dan menggantinya dengan warna solid abu-abu digital murni (tanpa tekstur dan noise kamera), CNN kehilangan "contekan" fitur latar belakang tersebut dan mengalami degradasi akurasi yang substansial. Hal ini mengonfirmasi bahwa:

1. **Akurasi tinggi pada dataset *in-vitro* bersifat bias.** Model tidak sepenuhnya menggeneralisasi fitur penyakit, melainkan mengeksploitasi artefak dataset.
2. **Dataset PlantVillage memiliki keterbatasan fundamental** untuk melatih model yang siap digunakan dalam kondisi perkebunan nyata (*in-the-wild*), di mana latar belakang, pencahayaan, dan sudut pengambilan gambar sangat bervariasi.
3. **Segmentasi latar belakang (rembg) harus diintegrasikan pada fase pelatihan**, bukan hanya pada fase inferensi, agar model dipaksa belajar secara eksklusif dari tekstur daun.

Temuan ini sejalan dengan riset terbaru mengenai *domain shift* pada klasifikasi penyakit tanaman [7][8], yang menekankan bahwa performa tinggi pada dataset laboratorium tidak menjamin keberhasilan di lapangan.

### E. Analisis Konsistensi Pipeline Praproses

Sistem yang dibangun telah secara proaktif memitigasi masalah *preprocessing mismatch* melalui tiga langkah:

1. **Normalisasi skala piksel:** Menerapkan `img / 255.0` secara konsisten pada fase pelatihan maupun inferensi.
2. **Penyelarasan ruang warna:** Menggunakan `img.convert("RGB")` secara eksplisit pada antarmuka prediksi untuk mencegah kesalahan akibat perbedaan format BGR (OpenCV) dan RGB (PIL).
3. **Augmentasi *real-time*:** Menggunakan *layer* augmentasi di dalam arsitektur model sehingga transformasi hanya aktif saat pelatihan dan otomatis nonaktif saat inferensi.

---

## V. KESIMPULAN DAN SARAN

### A. Kesimpulan

Berdasarkan hasil penelitian, dapat ditarik kesimpulan sebagai berikut:

1. Model CNN empat blok konvolusi yang diusulkan berhasil mencapai akurasi uji sebesar **97,12%** pada dataset PlantVillage (38 kelas), melampaui target minimum 85%.
2. Strategi pelatihan yang diterapkan (*Early Stopping, ReduceLROnPlateau, Fallback OOM, Resume Training*) terbukti tangguh untuk melatih model secara efisien di lingkungan komputasi CPU yang terbatas.
3. Model berhasil dikonversi ke format TFLite (4,4 MB) dan diimplementasikan dalam antarmuka web Gradio dengan latensi sangat rendah (~6 ms per citra), membuktikan kelayakannya untuk *deployment* pada perangkat *edge*.
4. Studi ablasi mengungkap bahwa model CNN PlantVillage mengalami *Clever Hans Effect*: 26,3% sampel mengalami misklasifikasi setelah latar belakang dihapus, membuktikan bahwa CNN mengandalkan fitur non-patologis (tekstur latar belakang) untuk klasifikasi.

### B. Batasan Penelitian

1. Model dilatih secara eksklusif pada dataset PlantVillage yang bersifat *in-vitro*, sehingga generalisasi terhadap citra *in-the-wild* masih terbatas.
2. Arsitektur *two-stage pipeline* (rembg + CNN) yang diuji belum dioptimalkan; segmentasi U-Net memiliki kelemahan pada kondisi pencahayaan rendah, oklusi antar-daun, dan citra dengan kontras warna minimal.
3. Studi ablasi dilakukan pada sampel terbatas (38 citra) dan belum divalidasi menggunakan dataset lapangan terpisah seperti PlantDoc.

### C. Saran Pengembangan

1. **Integrasi Segmentasi pada Fase Pelatihan:** Melatih ulang model CNN menggunakan citra yang telah melalui proses segmentasi rembg, sehingga model terbiasa mengklasifikasikan daun tanpa bantuan fitur latar belakang.
2. **Arsitektur *Two-Stage Pipeline* (YOLO + CNN):** Mengadopsi model deteksi objek seperti YOLOv8 yang di-*fine-tuning* pada dataset *in-the-wild* (PlantDoc) untuk lokalisasi otomatis daun, sebelum diklasifikasikan oleh CNN.
3. **Validasi Komparatif:** Mengeksplorasi penggunaan *Vision Transformer* (ViT) atau MobileNetV2 sebagai *baseline* tambahan untuk menguji efisiensi komputasi terhadap akurasi di perangkat *edge*.

---

## DAFTAR PUSTAKA

[1] FAO, "New standards to curb the global spread of plant pests and diseases," Food and Agriculture Organization of the United Nations, 2023. [Online]. Available: https://www.fao.org/newsroom/detail/new-standards-to-curb-the-global-spread-of-plant-pests-and-diseases/en

[2] W. Chen, J. Liu, and X. Zhang, "Enhanced plant disease classification with attention-based convolutional neural network using squeeze and excitation mechanism," *Frontiers in Plant Science*, vol. 16, 2025, doi: 10.3389/fpls.2025.1516058.

[3] A. Kumar and V. Singh, "A lightweight and explainable CNN model for empowering plant disease diagnosis," *Scientific Reports*, vol. 15, no. 1, pp. 1-15, 2025, doi: 10.1038/s41598-025-94083-1.

[4] Y. Li, R. Patel, and S. Moreno, "A Lightweight Deep Learning Model for Accurate Plant Disease Detection in Real Applications," in *Proc. 2025 IEEE Latin Conference on IoT (LCIoT)*, 2025, doi: 10.1109/LCIoT62518.2025.10818645.

[5] M. Rahman, T. Hassan, and K. Ahmed, "Plant Disease Detection and Classification using Convolutional Neural Network," in *Proc. 2025 4th Int. Conf. on Automation, Computing and Renewable Systems (ICACRS)*, IEEE, 2025, doi: 10.1109/ICACRS64609.2025.10918232.

[6] L. Wang and H. Zhang, "Robust Plant Disease Detection on PlantVillage using DenseNet Architecture and Segmented Images," *Pertanika Journal of Science and Technology*, vol. 33, no. 2, pp. 887-908, 2025.

[7] X. Zhao, M. Li, and F. Zhou, "Rethinking Plant Disease Diagnosis: Bridging the Academic-Practical Gap with Vision Transformers and Zero-Shot Learning," *arXiv preprint*, arXiv:2511.18989, 2025. [Online]. Available: https://arxiv.org/abs/2511.18989

[8] S. Lapuschkin et al., "Unmasking Clever Hans predictors and assessing what machines really learn," *Nature Communications*, vol. 10, no. 1, pp. 1-8, 2023, doi: 10.1038/s41467-019-08987-4.

[9] A. Kaya and A. S. Keceli, "Advances and Challenges in Computer Vision for Image-Based Plant Disease Detection: A Comprehensive Survey," *IEEE Trans. Autom. Sci. Eng.*, vol. 22, 2025, doi: 10.1109/TASE.2024.3514919.

[10] J. P. Vasconez, L. Delpiano, and S. Vougioukas, "A robust and light-weight transfer learning-based architecture for accurate detection of leaf diseases across multiple plants," *Frontiers in Plant Science*, vol. 14, 2024, doi: 10.3389/fpls.2023.1321877.
