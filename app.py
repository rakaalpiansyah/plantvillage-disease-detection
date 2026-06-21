"""
app.py
Antarmuka (interface) web sederhana untuk demo klasifikasi penyakit
daun tanaman. Menggunakan model TFLite (bukan model Keras penuh) agar
ringan dijalankan di CPU dengan RAM terbatas (mis. Ryzen 7 5800H, 16GB RAM).

Cara jalan:
    python app.py
Lalu buka URL lokal yang muncul di terminal (biasanya http://127.0.0.1:7860).

Prasyarat: jalankan src/train.py lalu src/export.py terlebih dahulu,
agar file artifacts/tflite/model.tflite dan label.txt sudah tersedia.
"""

import sys
import time

import numpy as np
import tensorflow as tf
from PIL import Image

import config
import gradio as gr
from src.detector import remove_background

MODEL_PATH = config.TFLITE_DIR / "model.tflite"
LABEL_PATH = config.TFLITE_DIR / "label.txt"


def load_labels():
    if not LABEL_PATH.exists():
        print(
            f"ERROR: File label tidak ditemukan: {LABEL_PATH}\n"
            "Jalankan pipeline ini terlebih dahulu:\n"
            "  python -m src.train\n"
            "  python -m src.export"
        )
        sys.exit(1)
    with open(LABEL_PATH) as f:
        return [line.strip() for line in f if line.strip()]


def load_interpreter():
    if not MODEL_PATH.exists():
        print(
            f"ERROR: Model TFLite tidak ditemukan: {MODEL_PATH}\n"
            "Jalankan pipeline ini terlebih dahulu:\n"
            "  python -m src.train\n"
            "  python -m src.export"
        )
        sys.exit(1)
    interpreter = tf.lite.Interpreter(model_path=str(MODEL_PATH))
    interpreter.allocate_tensors()
    return interpreter


# Inisialisasi saat startup
print("Memuat model TFLite dan label...")
CLASS_NAMES_RAW = load_labels()
INTERPRETER = load_interpreter()
INPUT_DETAILS = INTERPRETER.get_input_details()
OUTPUT_DETAILS = INTERPRETER.get_output_details()
IMG_SIZE = config.IMG_SIZE
print(f"Model dimuat: {len(CLASS_NAMES_RAW)} kelas, input size {IMG_SIZE}")

def format_label(raw_label):
    if "___" not in raw_label:
        return raw_label
    plant, condition = raw_label.split("___", 1)
    plant = plant.replace("_", " ")
    if condition.lower() == "healthy":
        return f"🌿 {plant} (Sehat)"
    else:
        condition = condition.replace("_", " ")
        return f"⚠️ {plant} - Sakit ({condition})"

CLASS_NAMES_FORMATTED = [format_label(c) for c in CLASS_NAMES_RAW]

# Ambil daftar tanaman yang didukung
SUPPORTED_PLANTS = sorted(list(set([
    c.split("___")[0].replace("_", " ") for c in CLASS_NAMES_RAW if "___" in c
])))


def predict(image: Image.Image, enable_autocrop: bool):
    if image is None:
        return {}, "Silakan unggah citra daun terlebih dahulu.", "Tidak ada gambar", None

    start = time.perf_counter()
    
    # Simpan original untuk comparison
    processed_image = image
    
    # TAHAP 1: Localization / Auto-Crop (Jika diaktifkan)
    if enable_autocrop:
        processed_image = remove_background(image)
        
    # TAHAP 2: Classification (CNN)
    img = processed_image.convert("RGB").resize(IMG_SIZE)
    arr = np.array(img, dtype=np.float32) / 255.0
    arr = np.expand_dims(arr, axis=0)

    INTERPRETER.set_tensor(INPUT_DETAILS[0]["index"], arr)
    INTERPRETER.invoke()
    preds = INTERPRETER.get_tensor(OUTPUT_DETAILS[0]["index"])[0]

    elapsed_ms = (time.perf_counter() - start) * 1000

    top5_idx = preds.argsort()[-5:][::-1]
    result = {CLASS_NAMES_FORMATTED[i]: float(preds[i]) for i in top5_idx}
    
    # Ambil prediksi terbaik
    best_idx = top5_idx[0]
    best_raw = CLASS_NAMES_RAW[best_idx]
    best_conf = preds[best_idx] * 100
    
    if "healthy" in best_raw.lower():
        diagnosis = f"### ✅ Diagnosis Utama: Tanaman Sehat\nBerpeluang **{best_conf:.1f}%** bahwa daun ini terdeteksi sebagai **{CLASS_NAMES_FORMATTED[best_idx]}**."
    else:
        diagnosis = f"### ❌ Diagnosis Utama: Tanaman Terjangkit Penyakit\nBerpeluang **{best_conf:.1f}%** bahwa daun ini terdeteksi sebagai **{CLASS_NAMES_FORMATTED[best_idx]}**."
        
    info_text = f"Waktu inferensi total: {elapsed_ms:.1f} ms (CPU)"

    return result, diagnosis, info_text, processed_image


def build_demo():
    with gr.Blocks(
        title="Klasifikasi Penyakit Daun Tanaman",
        theme=gr.themes.Soft(),
    ) as demo:
        gr.Markdown(
            "## 🌿 Klasifikasi Cerdas Penyakit Daun Tanaman\n"
            "Aplikasi pendeteksi penyakit tanaman berbasis *Artificial Intelligence* (AI). "
            "Sistem ini menggunakan algoritma *Convolutional Neural Network* (CNN) yang telah dioptimasi dengan format **TFLite**, "
            "memungkinkannya berjalan sangat cepat dan hemat daya di CPU.\n\n"
            f"*Mendukung deteksi **{len(CLASS_NAMES_RAW)} kondisi** yang mencakup daun sehat dan berpenyakit.*"
        )
        
        with gr.Accordion("📋 Lihat Daftar Tanaman yang Didukung", open=False):
            gr.Markdown(f"Model ini telah dilatih untuk mengenali daun dari **{len(SUPPORTED_PLANTS)} jenis tanaman** berikut:\n\n" + ", ".join([f"**{p}**" for p in SUPPORTED_PLANTS]))

        with gr.Row():
            with gr.Column():
                image_input = gr.Image(type="pil", label="Unggah Foto Daun")
                enable_autocrop = gr.Checkbox(label="🪄 Aktifkan AI Background Removal (Untuk foto di alam liar / In-The-Wild)", value=False)
                predict_btn = gr.Button("🔍 Analisis Daun", variant="primary")
            with gr.Column():
                diagnosis_output = gr.Markdown("### ⏳ Menunggu gambar...")
                label_output = gr.Label(num_top_classes=5, label="Persentase Keyakinan (Top-5)")
                info_output = gr.Textbox(label="Performa Sistem", interactive=False)
        
        with gr.Row():
            # Untuk mendemonstrasikan hasil Auto-Crop ke user
            processed_image_output = gr.Image(type="pil", label="Citra Daun Setelah Diproses (Tahap 1)", interactive=False)

        predict_btn.click(fn=predict, inputs=[image_input, enable_autocrop], outputs=[label_output, diagnosis_output, info_output, processed_image_output])
        image_input.change(fn=predict, inputs=[image_input, enable_autocrop], outputs=[label_output, diagnosis_output, info_output, processed_image_output])
        enable_autocrop.change(fn=predict, inputs=[image_input, enable_autocrop], outputs=[label_output, diagnosis_output, info_output, processed_image_output])

        gr.Markdown(
            "---\n"
            "📖 **Cara penggunaan:** Unggah foto daun tanaman → klik **Prediksi** → "
            "lihat 5 prediksi teratas beserta tingkat keyakinan (confidence).\n\n"
            "*Pipeline: CNN 4-blok konvolusi → TFLite → Gradio*"
        )

    return demo


if __name__ == "__main__":
    demo = build_demo()
    demo.launch()
