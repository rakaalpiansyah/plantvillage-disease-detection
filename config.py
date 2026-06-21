"""
config.py
Konfigurasi terpusat untuk seluruh pipeline (data, model, training, export).
Ubah nilai di sini saja kalau ingin mengubah perilaku pipeline secara global.
"""

import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Path dasar proyek
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
CHECKPOINT_DIR = BASE_DIR / "checkpoints"
ARTIFACTS_DIR = BASE_DIR / "artifacts"
SAVED_MODEL_DIR = ARTIFACTS_DIR / "saved_model"
TFLITE_DIR = ARTIFACTS_DIR / "tflite"
TFJS_DIR = ARTIFACTS_DIR / "tfjs_model"
LOG_DIR = BASE_DIR / "logs"

CSV_LOG_PATH = LOG_DIR / "history_pelatihan.csv"
BEST_MODEL_PATH = CHECKPOINT_DIR / "best_model.keras"

TRAIN_CACHE_FILE = str(CHECKPOINT_DIR / "train_cache")
VAL_CACHE_FILE = str(CHECKPOINT_DIR / "val_cache")

for d in (CHECKPOINT_DIR, ARTIFACTS_DIR, SAVED_MODEL_DIR, TFLITE_DIR, TFJS_DIR, LOG_DIR):
    os.makedirs(d, exist_ok=True)

# ---------------------------------------------------------------------------
# Dataset
# ---------------------------------------------------------------------------
DATASET_DIR = BASE_DIR / "dataset" / "color"
VAL_SPLIT_RATIO = 0.15
TEST_SPLIT_RATIO = 0.15

IMG_SIZE = (140, 140)
SEED = 42

# ---------------------------------------------------------------------------
# Training (disesuaikan untuk CPU, RAM terbatas — mis. Ryzen 7 5800H 16GB)
# ---------------------------------------------------------------------------
# Batch size lebih kecil dari notebook asli (32) agar lebih aman di RAM 16GB
# saat dijalankan murni CPU. Bisa dinaikkan kalau RAM lapang.
BATCH_SIZE = 32
EPOCHS = 15
LEARNING_RATE = 1e-3
MIN_TRAIN_ACC_TARGET = 0.85
MIN_TEST_ACC_TARGET = 0.85

EARLYSTOP_PATIENCE = 4
REDUCE_LR_PATIENCE = 2
REDUCE_LR_FACTOR = 0.5
MIN_LR = 1e-6

# ---------------------------------------------------------------------------
# Test mode (untuk validasi pipeline sebelum full training)
# ---------------------------------------------------------------------------
# Jika True, gunakan subset kecil dataset (limit gambar per kelas)
# agar pipeline bisa divalidasi dalam hitungan menit.
TEST_MODE = False  # Ubah ke False untuk training penuh
TEST_MAX_SAMPLES = 50  # Batasi jumlah sampel yang dibaca per kelas saat TEST_MODE=True
TEST_EPOCHS = 2

# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------
TFJS_ENABLED = False  # Set True jika tensorflowjs terinstal


MAX_OOM_RETRY = 3
MIN_BATCH_SIZE = 8
