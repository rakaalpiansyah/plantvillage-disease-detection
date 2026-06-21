"""
src/data.py
Pemuatan dataset dari direktori lokal (PlantVillage) dan
pipeline praproses (resize, normalisasi, augmentasi, caching, batching).
"""

import glob
import os
import time

import tensorflow as tf

import config


def get_dataset_info():
    """Mengambil metadata dataset (jumlah kelas, nama kelas, jumlah citra)."""
    if not config.DATASET_DIR.exists():
        raise FileNotFoundError(
            f"Direktori dataset tidak ditemukan di {config.DATASET_DIR}\n"
            f"Silakan tunggu proses download/clone selesai."
        )

    # Cara cepat mendapatkan nama kelas dari nama folder
    class_names = sorted([d.name for d in config.DATASET_DIR.iterdir() if d.is_dir()])
    num_classes = len(class_names)
    
    total_images = sum([len(files) for r, d, files in os.walk(config.DATASET_DIR)])

    if not config.TEST_MODE:
        assert total_images >= 1000, "Dataset harus berisi minimal 1000 gambar."

    return {
        "class_names": class_names,
        "num_classes": num_classes,
        "total_images": total_images,
    }


def _preprocess(image, label):
    # image_dataset_from_directory sudah meresize, sisa normalisasi
    image = tf.cast(image, tf.float32) / 255.0
    return image, label


def _clear_stale_cache_lockfiles():
    """Membersihkan lockfile cache TF dari proses sebelumnya yang gagal."""
    for prefix in (config.TRAIN_CACHE_FILE, config.VAL_CACHE_FILE):
        for lock in glob.glob(prefix + "*lockfile"):
            try:
                os.remove(lock)
                print(f"Lockfile lama dihapus: {lock}")
            except OSError as e:
                print(f"Tidak bisa menghapus lockfile {lock}: {e}")
    time.sleep(0.5)


def build_pipelines(batch_size=None):
    """Membangun pipeline tf.data siap latih dari direktori."""
    batch_size = batch_size or config.BATCH_SIZE
    autotune = tf.data.AUTOTUNE

    if not config.DATASET_DIR.exists():
        raise FileNotFoundError(f"Direktori dataset tidak ditemukan: {config.DATASET_DIR}")

    # Menggunakan tf.keras.utils.image_dataset_from_directory
    # Subset train dan validation di-split 80/20
    train_ds, val_ds = tf.keras.utils.image_dataset_from_directory(
        config.DATASET_DIR,
        labels="inferred",
        label_mode="int",
        color_mode="rgb",
        batch_size=batch_size,
        image_size=config.IMG_SIZE,
        shuffle=True,
        seed=config.SEED,
        validation_split=0.2,
        subset="both",
    )

    # Split val_ds menjadi val_ds (10%) dan test_ds (10%)
    val_batches = len(val_ds) // 2
    test_ds = val_ds.skip(val_batches)
    val_ds = val_ds.take(val_batches)

    if config.TEST_MODE:
        print(f"[TEST MODE] Menggunakan subset sangat kecil untuk validasi pipeline.")
        test_batches = max(1, config.TEST_MAX_SAMPLES // batch_size)
        train_ds = train_ds.take(test_batches * 2)
        val_ds = val_ds.take(test_batches)
        test_ds = test_ds.take(test_batches)

    _clear_stale_cache_lockfiles()

    train_ds = (
        train_ds.map(_preprocess, num_parallel_calls=autotune)
        .cache(config.TRAIN_CACHE_FILE)
        .prefetch(autotune)
    )
    val_ds = (
        val_ds.map(_preprocess, num_parallel_calls=autotune)
        .cache(config.VAL_CACHE_FILE)
        .prefetch(autotune)
    )
    test_ds = (
        test_ds.map(_preprocess, num_parallel_calls=autotune)
        .prefetch(autotune)
    )
    
    return train_ds, val_ds, test_ds


def build_train_val_pipelines(batch_size=None):
    """Versi ringan build_pipelines: hanya train+val (dipakai saat training/resume)."""
    train_ds, val_ds, _ = build_pipelines(batch_size)
    return train_ds, val_ds


def get_datasets(batch_size=None):
    """Fungsi praktis: langsung mengembalikan dataset siap pakai + info."""
    info = get_dataset_info()
    train_ds, val_ds, test_ds = build_pipelines(batch_size)
    return {
        "train_ds": train_ds,
        "val_ds": val_ds,
        "test_ds": test_ds,
        "info": info,
    }
