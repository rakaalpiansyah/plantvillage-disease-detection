"""
gradcam.py
Skrip untuk menghasilkan visualisasi Explainable AI (Grad-CAM).
Menyoroti area piksel mana yang digunakan oleh CNN untuk memprediksi penyakit.
"""
import os
import sys
import numpy as np
import tensorflow as tf
from PIL import Image
import matplotlib.cm as cm
import argparse
import config

# Pastikan path model keras tersedia
KERAS_MODEL_PATH = "artifacts/model.keras"

def get_img_array(img_path, size):
    """Membaca gambar dan mengubahnya ke tensor (1, size, size, 3) yang diskalakan ke [0, 1]."""
    img = tf.keras.utils.load_img(img_path, target_size=size)
    array = tf.keras.utils.img_to_array(img)
    array = np.expand_dims(array, axis=0) / 255.0
    return array, img

def make_gradcam_heatmap(img_array, model, last_conv_layer_name, pred_index=None):
    """Menghasilkan array heatmap Grad-CAM."""
    # Membuat model yang memetakan input ke aktivasi layer conv terakhir dan output prediksi
    grad_model = tf.keras.models.Model(
        model.inputs, 
        [model.get_layer(last_conv_layer_name).output, model.output]
    )

    # GradientTape untuk melacak gradien
    with tf.GradientTape() as tape:
        last_conv_layer_output, preds = grad_model(img_array)
        if pred_index is None:
            pred_index = tf.argmax(preds[0])
        class_channel = preds[:, pred_index]

    # Gradien output layer conv terakhir terhadap prediksi kelas
    grads = tape.gradient(class_channel, last_conv_layer_output)

    # Rata-rata spasial gradien
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

    # Kalikan fitur dengan gradien (pembobotan)
    last_conv_layer_output = last_conv_layer_output[0]
    heatmap = last_conv_layer_output @ pooled_grads[..., tf.newaxis]
    heatmap = tf.squeeze(heatmap)

    # Terapkan ReLU agar hanya mengambil fitur positif (yang berkontribusi ke kelas)
    heatmap = tf.maximum(heatmap, 0) / tf.math.reduce_max(heatmap)
    return heatmap.numpy()

def save_and_display_gradcam(img_path, heatmap, cam_path="gradcam_result.png", alpha=0.4):
    """Melapiskan heatmap ke atas gambar asli dan menyimpannya."""
    # Baca gambar asli
    img = tf.keras.utils.load_img(img_path)
    img = tf.keras.utils.img_to_array(img)

    # Rescale heatmap dari [0, 1] ke [0, 255]
    heatmap = np.uint8(255 * heatmap)

    # Gunakan colormap 'jet'
    # Dalam versi matplotlib baru, cm.get_cmap digantikan, tapi ini aman untuk numpy
    jet = cm.get_cmap("jet")

    # Ambil nilai RGB dari jet colormap
    jet_colors = jet(np.arange(256))[:, :3]
    jet_heatmap = jet_colors[heatmap]

    # Resize heatmap sesuai gambar asli
    jet_heatmap = tf.keras.utils.array_to_img(jet_heatmap)
    jet_heatmap = jet_heatmap.resize((img.shape[1], img.shape[0]))
    jet_heatmap = tf.keras.utils.img_to_array(jet_heatmap)

    # Lapisan overlay
    superimposed_img = jet_heatmap * alpha + img
    superimposed_img = tf.keras.utils.array_to_img(superimposed_img)

    # Simpan
    superimposed_img.save(cam_path)
    print(f"✅ Visualisasi Grad-CAM berhasil disimpan ke: {cam_path}")

def main(image_path):
    if not os.path.exists(KERAS_MODEL_PATH):
        print(f"❌ Error: Model Keras '{KERAS_MODEL_PATH}' tidak ditemukan. Anda perlu melatih model terlebih dahulu atau pastikan model.keras ada.")
        sys.exit(1)

    print("Memuat model Keras... (ini mungkin butuh beberapa detik)")
    model = tf.keras.models.load_model(KERAS_MODEL_PATH)
    
    # Membuang layer augmentasi jika ada, untuk gradcam kita butuh inference model yang bersih
    from src.model import build_inference_model
    inf_model = build_inference_model(model)
    # Pindahkan bobot
    inf_model.set_weights(model.get_weights())

    # Cari nama layer Conv2D terakhir
    last_conv_layer_name = None
    for layer in inf_model.layers:
        if isinstance(layer, tf.keras.layers.Conv2D):
            last_conv_layer_name = layer.name
    
    if last_conv_layer_name is None:
        print("❌ Error: Tidak dapat menemukan layer Conv2D pada model.")
        sys.exit(1)
        
    print(f"Target layer Grad-CAM: {last_conv_layer_name}")

    img_array, _ = get_img_array(image_path, size=config.IMG_SIZE)
    
    # Prediksi
    preds = inf_model.predict(img_array)
    pred_idx = np.argmax(preds[0])
    
    # Baca label kelas
    try:
        with open(os.path.join(config.TFLITE_DIR, "label.txt"), "r") as f:
            class_names = [line.strip() for line in f.readlines()]
        predicted_class = class_names[pred_idx]
    except:
        predicted_class = f"Kelas {pred_idx}"
        
    print(f"Model memprediksi kelas: {predicted_class} (Conf: {preds[0][pred_idx]*100:.1f}%)")

    # Generate Heatmap
    heatmap = make_gradcam_heatmap(img_array, inf_model, last_conv_layer_name, pred_index=pred_idx)
    
    # Save image
    out_name = f"gradcam_{os.path.basename(image_path)}"
    save_and_display_gradcam(image_path, heatmap, cam_path=out_name)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generasi peta panas Grad-CAM untuk interpretasi prediksi CNN.")
    parser.add_argument("image_path", help="Path ke gambar yang ingin divisualisasikan.")
    args = parser.parse_args()
    
    main(args.image_path)
