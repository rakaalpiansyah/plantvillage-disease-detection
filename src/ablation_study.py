"""
ablation_study.py
Skrip untuk melakukan uji coba Ablasi (Ablation Study) secara kuantitatif.
Membandingkan hasil prediksi CNN murni vs pipeline rembg + CNN pada sekumpulan citra.
"""
import os
import sys
import time
import numpy as np
from PIL import Image

import config
from src.detector import remove_background, REMBG_AVAILABLE

try:
    import tflite_runtime.interpreter as tflite
    INTERPRETER = tflite.Interpreter(model_path=str(config.TFLITE_DIR / "model.tflite"))
except ImportError:
    import tensorflow as tf
    INTERPRETER = tf.lite.Interpreter(model_path=str(config.TFLITE_DIR / "model.tflite"))
INTERPRETER.allocate_tensors()
INPUT_DETAILS = INTERPRETER.get_input_details()
OUTPUT_DETAILS = INTERPRETER.get_output_details()

def load_labels():
    with open(config.TFLITE_DIR / "label.txt", "r") as f:
        return [line.strip() for line in f.readlines()]

CLASS_NAMES = load_labels()

def predict_tflite(img_pil):
    """Fungsi helper untuk inferensi TFLite"""
    img = img_pil.convert("RGB").resize(config.IMG_SIZE)
    arr = np.array(img, dtype=np.float32) / 255.0
    arr = np.expand_dims(arr, axis=0)

    INTERPRETER.set_tensor(INPUT_DETAILS[0]["index"], arr)
    start = time.perf_counter()
    INTERPRETER.invoke()
    latency = (time.perf_counter() - start) * 1000
    
    preds = INTERPRETER.get_tensor(OUTPUT_DETAILS[0]["index"])[0]
    best_idx = np.argmax(preds)
    return CLASS_NAMES[best_idx], preds[best_idx] * 100, latency

def main(test_dir="test_in_the_wild"):
    if not os.path.exists(test_dir):
        print(f"📁 Folder '{test_dir}' tidak ditemukan. Membuat folder baru...")
        os.makedirs(test_dir)
        print("💡 Silakan isi folder tersebut dengan foto-foto daun dari alam liar, lalu jalankan ulang skrip ini.")
        sys.exit(0)
        
    image_files = [f for f in os.listdir(test_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    if len(image_files) == 0:
        print(f"⚠️ Folder '{test_dir}' kosong. Silakan masukkan beberapa gambar uji.")
        sys.exit(0)
        
    if not REMBG_AVAILABLE:
        print("❌ Error: Pustaka 'rembg' tidak terpasang. Ablation study gagal.")
        sys.exit(1)

    print(f"🔍 Memulai Uji Ablasi pada {len(image_files)} gambar...")
    print("-" * 100)
    print(f"{'Filename':<25} | {'Skenario 1 (CNN Murni)':<30} | {'Skenario 2 (rembg + CNN)':<30}")
    print("-" * 100)
    
    results = []

    for img_file in image_files:
        img_path = os.path.join(test_dir, img_file)
        
        try:
            original_img = Image.open(img_path)
        except Exception as e:
            print(f"Error membaca {img_file}: {e}")
            continue
            
        # Skenario 1: CNN Murni
        pred1, conf1, lat1 = predict_tflite(original_img)
        
        # Skenario 2: rembg + CNN
        processed_img = remove_background(original_img)
        pred2, conf2, lat2 = predict_tflite(processed_img)
        
        # Ringkas nama kelas agar muat di tabel
        p1_short = pred1.split("___")[1][:20] if "___" in pred1 else pred1[:20]
        p2_short = pred2.split("___")[1][:20] if "___" in pred2 else pred2[:20]
        
        row = f"{img_file[:23]:<25} | {p1_short} ({conf1:.1f}%) | {p2_short} ({conf2:.1f}%)"
        print(row)
        
        results.append({
            'file': img_file,
            'pred_cnn': pred1, 'conf_cnn': conf1,
            'pred_rembg': pred2, 'conf_rembg': conf2
        })

    print("-" * 100)
    print("✅ Uji Ablasi Selesai.")
    print("📝 Tip Jurnal: Hitung secara manual berapa banyak gambar yang prediksinya menjadi BENAR setelah menggunakan Skenario 2.")

if __name__ == "__main__":
    main()
