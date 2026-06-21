"""
src/export.py
Mengekspor model terlatih ke SavedModel, TensorFlow Lite (.tflite),
dan TensorFlow.js. TFLite adalah format yang dipakai oleh app.py
(interface) karena paling ringan untuk inferensi di CPU.
Jalankan:
    python -m src.export
"""

import os
import subprocess
import sys

import tensorflow as tf

import config
from src import data as data_module
from src import model as model_module


def _file_size_mb(path):
    """Mengembalikan ukuran file dalam MB."""
    if os.path.exists(path):
        size = os.path.getsize(path)
        return f"{size / (1024 * 1024):.2f} MB"
    return "N/A"


def export_saved_model(trained_model):
    """Ekspor ke SavedModel (format native TensorFlow)."""
    print("\n--- Ekspor ke SavedModel ---")
    inference_model = model_module.build_inference_model(trained_model)

    inference_model.export(str(config.SAVED_MODEL_DIR))
    print(f"[OK] SavedModel disimpan ke: {config.SAVED_MODEL_DIR}")
    return inference_model


def export_tflite():
    """Ekspor SavedModel ke TensorFlow Lite (.tflite)."""
    print("\n--- Ekspor ke TFLite ---")
    converter = tf.lite.TFLiteConverter.from_saved_model(str(config.SAVED_MODEL_DIR))
    converter.target_spec.supported_ops = [
        tf.lite.OpsSet.TFLITE_BUILTINS,
        tf.lite.OpsSet.SELECT_TF_OPS,
    ]
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    tflite_model = converter.convert()

    out_path = config.TFLITE_DIR / "model.tflite"
    with open(out_path, "wb") as f:
        f.write(tflite_model)
    print(f"TFLite diekspor ke: {out_path}")
    print(f"Ukuran file: {_file_size_mb(out_path)}")
    return out_path


def export_label_file(class_names):
    """Menyimpan nama kelas ke file teks (untuk interface)."""
    print("\n--- Ekspor Label ---")
    out_path = config.TFLITE_DIR / "label.txt"
    with open(out_path, "w") as f:
        f.write("\n".join(class_names))
    print(f"Label diekspor ke: {out_path} ({len(class_names)} kelas)")
    return out_path


def export_tfjs():
    """Ekspor ke TensorFlow.js (opsional — hanya jika package terinstal)."""
    print("\n--- Ekspor ke TFJS ---")
    if not config.TFJS_ENABLED:
        print("TFJS export dinonaktifkan (config.TFJS_ENABLED = False). Dilewati.")
        return

    # Cek apakah tensorflowjs terinstal
    try:
        import importlib
        importlib.import_module("tensorflowjs")
    except ImportError:
        print("Package 'tensorflowjs' tidak terinstal. Dilewati.")
        print("Untuk mengaktifkan: pip install tensorflowjs")
        return

    cmd = [
        sys.executable,
        "-m",
        "tensorflowjs.converters.converter",
        "--input_format",
        "tf_saved_model",
        "--output_format",
        "tfjs_graph_model",
        str(config.SAVED_MODEL_DIR),
        str(config.TFJS_DIR),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"TFJS diekspor ke: {config.TFJS_DIR}")
    else:
        print("Ekspor TFJS gagal. Detail error:")
        print(result.stderr.splitlines()[-1] if result.stderr else "Tidak ada stderr.")


def main():
    print("=" * 60)
    print("  PLANT DISEASE CLASSIFIER — Model Export")
    print("=" * 60)

    info = data_module.get_dataset_info()

    # Cari model terlatih (prioritas: best_model > final_model)
    model_path = config.BEST_MODEL_PATH
    if not model_path.exists():
        model_path = config.ARTIFACTS_DIR / "final_model.keras"
    if not model_path.exists():
        raise FileNotFoundError(
            "Tidak ditemukan model terlatih. Jalankan 'python -m src.train' terlebih dahulu."
        )

    print(f"\nMemuat model dari: {model_path}")
    trained_model = tf.keras.models.load_model(str(model_path))

    export_saved_model(trained_model)
    export_tflite()
    export_label_file(info["class_names"])
    export_tfjs()

    print(f"\n{'=' * 60}")
    print("  Export selesai!")
    print(f"  SavedModel : {config.SAVED_MODEL_DIR}")
    print(f"  TFLite     : {config.TFLITE_DIR / 'model.tflite'} ({_file_size_mb(config.TFLITE_DIR / 'model.tflite')})")
    print(f"  Labels     : {config.TFLITE_DIR / 'label.txt'}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
