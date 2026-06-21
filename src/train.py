"""
src/train.py
Script training utama: bisa dijalankan langsung lewat
    python -m src.train
Mendukung resume otomatis dari checkpoint terakhir dan fallback
pengecilan batch size otomatis jika terjadi ResourceExhaustedError (OOM).
Dirancang untuk jalan di CPU (tanpa GPU) dengan RAM terbatas.
"""

import glob
import re
import time
import traceback

import tensorflow as tf

import config
from src import data as data_module
from src import model as model_module


def detect_hardware_and_batch_size():
    gpus = tf.config.list_physical_devices("GPU")
    if gpus:
        print("GPU terdeteksi:", gpus)
        batch_size = 64
        try:
            from tensorflow.keras import mixed_precision

            mixed_precision.set_global_policy("mixed_float16")
            print("Mixed precision (mixed_float16) diaktifkan.")
        except Exception as e:
            print("Mixed precision tidak tersedia:", e)
    else:
        print("Tidak ada GPU terdeteksi; menggunakan CPU.")
        batch_size = config.BATCH_SIZE
    return batch_size


def build_callbacks():
    checkpoint_fp = str(config.CHECKPOINT_DIR / "model-epoch-{epoch:02d}.keras")
    checkpoint_cb = tf.keras.callbacks.ModelCheckpoint(
        checkpoint_fp, monitor="val_accuracy", save_best_only=False, save_freq="epoch"
    )
    best_checkpoint_cb = tf.keras.callbacks.ModelCheckpoint(
        str(config.BEST_MODEL_PATH), monitor="val_accuracy", save_best_only=True
    )
    csv_logger_cb = tf.keras.callbacks.CSVLogger(str(config.CSV_LOG_PATH), append=True)
    earlystop_cb = tf.keras.callbacks.EarlyStopping(
        monitor="val_accuracy",
        patience=config.EARLYSTOP_PATIENCE,
        restore_best_weights=True,
    )
    reduce_lr_cb = tf.keras.callbacks.ReduceLROnPlateau(
        monitor="val_loss",
        factor=config.REDUCE_LR_FACTOR,
        patience=config.REDUCE_LR_PATIENCE,
        min_lr=config.MIN_LR,
    )
    return [earlystop_cb, reduce_lr_cb, checkpoint_cb, best_checkpoint_cb, csv_logger_cb]


def find_resume_state(model):
    """Mendeteksi checkpoint terakhir untuk melanjutkan training, jika ada."""
    initial_epoch = 0
    pattern = str(config.CHECKPOINT_DIR / "model-epoch-*.keras")
    ckpts = sorted(glob.glob(pattern))
    if not ckpts:
        return model, initial_epoch

    latest = ckpts[-1]
    m = re.search(r"model-epoch-(\d+)\.keras", latest)
    if m:
        initial_epoch = int(m.group(1))
        print(f"Checkpoint ditemukan: {latest} (berhenti di epoch {initial_epoch}).")
        try:
            model = tf.keras.models.load_model(latest)
            print("Model berhasil dimuat dari checkpoint, melanjutkan training.")
        except Exception as e:
            print("Gagal memuat checkpoint, memulai dari awal. Error:", e)
            initial_epoch = 0
    return model, initial_epoch


def train_with_oom_fallback(
    model, batch_size, epochs, initial_epoch, callbacks
):
    """Melatih model dengan fallback otomatis: kecilkan batch size saat OOM."""
    attempt = 0
    while attempt < config.MAX_OOM_RETRY:
        try:
            print(
                f"\nIterasi {attempt + 1}: batch_size={batch_size} "
                f"(mulai dari epoch={initial_epoch})"
            )
            train_ds, val_ds = data_module.build_train_val_pipelines(
                batch_size=batch_size
            )
            history = model.fit(
                train_ds,
                validation_data=val_ds,
                epochs=epochs,
                initial_epoch=initial_epoch,
                callbacks=callbacks,
                verbose=1,
            )
            return history, batch_size, model

        except tf.errors.ResourceExhaustedError as e:
            print("\nResourceExhaustedError (memori penuh):", e)
            attempt += 1
            if batch_size <= config.MIN_BATCH_SIZE:
                print("Batch size sudah minimum, tidak bisa diperkecil lagi.")
                raise
            # Simpan weights sebelum clone
            old_weights = model.get_weights()
            batch_size = max(config.MIN_BATCH_SIZE, batch_size // 2)
            print(f"Mencoba ulang dengan batch_size={batch_size} ...")
            tf.keras.backend.clear_session()
            model = tf.keras.models.clone_model(model)
            model.compile(
                optimizer=tf.keras.optimizers.Adam(learning_rate=config.LEARNING_RATE),
                loss="sparse_categorical_crossentropy",
                metrics=["accuracy"],
            )
            # Restore weights setelah clone
            model.set_weights(old_weights)
            print("Weights berhasil ditransfer ke model baru.")
        except Exception:
            print("\nError tak terduga selama training:")
            traceback.print_exc()
            raise

    raise RuntimeError("Training gagal setelah beberapa kali percobaan (OOM berulang).")


def main():
    print("=" * 60)
    print("  PLANT DISEASE CLASSIFIER — Training Pipeline")
    print("=" * 60)

    # Tampilkan mode
    if config.TEST_MODE:
        print("\n[TEST MODE] Training dengan subset kecil untuk validasi pipeline.")
        epochs = config.TEST_EPOCHS
    else:
        print("\n[FULL MODE] Training dengan dataset lengkap.")
        epochs = config.EPOCHS

    batch_size = detect_hardware_and_batch_size()

    print("\nMengunduh/memuat dataset...")
    start_data = time.perf_counter()
    info = data_module.get_dataset_info()
    num_classes = info["num_classes"]
    print(f"Jumlah kelas: {num_classes}")
    print(f"Total citra di dataset: {info['total_images']:,}")

    elapsed_data = time.perf_counter() - start_data
    print(f"Dataset dimuat dalam {elapsed_data:.1f} detik.")

    print("\nMembangun model...")
    model = model_module.build_model(num_classes=num_classes)
    model, initial_epoch = find_resume_state(model)
    model.summary()

    callbacks = build_callbacks()

    print(f"\nMemulai training (epochs={epochs}, batch_size={batch_size})...")
    start_train = time.perf_counter()

    history, used_batch, model = train_with_oom_fallback(
        model=model,
        batch_size=batch_size,
        epochs=epochs,
        initial_epoch=initial_epoch,
        callbacks=callbacks,
    )

    elapsed_train = time.perf_counter() - start_train
    print(f"\n{'=' * 60}")
    print(f"  Training selesai!")
    print(f"  Waktu total training: {elapsed_train:.1f} detik ({elapsed_train/60:.1f} menit)")
    print(f"  Batch size yang digunakan: {used_batch}")
    print(f"{'=' * 60}")

    final_model_path = config.ARTIFACTS_DIR / "final_model.keras"
    model.save(str(final_model_path))
    print(f"Model final disimpan ke: {final_model_path}")


if __name__ == "__main__":
    main()
