"""
src/evaluate.py
Evaluasi model terlatih: akurasi train/val/test, confusion matrix,
classification report (precision/recall/F1 per kelas), dan kurva
training accuracy/loss. Jalankan:
    python -m src.evaluate
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Backend non-interaktif agar aman di headless/server
import matplotlib.pyplot as plt
import tensorflow as tf
from sklearn.metrics import classification_report, confusion_matrix

import config
from src import data as data_module


def load_trained_model(path=None):
    path = path or config.BEST_MODEL_PATH
    if not path.exists():
        # Fallback ke final_model jika best_model tidak ada
        alt_path = config.ARTIFACTS_DIR / "final_model.keras"
        if alt_path.exists():
            path = alt_path
            print(f"best_model.keras tidak ditemukan, menggunakan: {path}")
        else:
            raise FileNotFoundError(
                f"Tidak ditemukan model terlatih di {config.BEST_MODEL_PATH} "
                f"maupun {alt_path}. Jalankan 'python -m src.train' terlebih dahulu."
            )
    print(f"Memuat model dari: {path}")
    return tf.keras.models.load_model(str(path))


def evaluate_accuracy(model, train_ds, val_ds, test_ds):
    print("\nMengevaluasi akurasi pada tiap split...")
    train_loss, train_acc = model.evaluate(train_ds, verbose=0)
    val_loss, val_acc = model.evaluate(val_ds, verbose=0)
    test_loss, test_acc = model.evaluate(test_ds, verbose=0)

    print(f"  Train accuracy : {train_acc:.4f}  (loss: {train_loss:.4f})")
    print(f"  Valid accuracy : {val_acc:.4f}  (loss: {val_loss:.4f})")
    print(f"  Test accuracy  : {test_acc:.4f}  (loss: {test_loss:.4f})")

    if train_acc >= config.MIN_TRAIN_ACC_TARGET and test_acc >= config.MIN_TEST_ACC_TARGET:
        print("  [OK] Kriteria akurasi minimum (85%) terpenuhi.")
    else:
        print("  [!] Akurasi belum mencapai target 85%, pertimbangkan tuning lebih lanjut.")

    return {
        "train_acc": train_acc,
        "train_loss": train_loss,
        "val_acc": val_acc,
        "val_loss": val_loss,
        "test_acc": test_acc,
        "test_loss": test_loss,
    }


def plot_training_curves(csv_path=None, save_path=None):
    csv_path = csv_path or config.CSV_LOG_PATH
    if not csv_path.exists():
        print(f"File log tidak ditemukan: {csv_path} — skip plot kurva training.")
        return

    df = pd.read_csv(csv_path)
    df = df.drop_duplicates(subset="epoch", keep="last").sort_values("epoch")
    epochs_range = df["epoch"] + 1

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Accuracy
    ax = axes[0]
    if "accuracy" in df.columns:
        ax.plot(epochs_range, df["accuracy"], label="Train Accuracy", marker="o", linewidth=2)
    if "val_accuracy" in df.columns:
        ax.plot(epochs_range, df["val_accuracy"], label="Val Accuracy", marker="s", linewidth=2)
    ax.set_title("Training and Validation Accuracy", fontsize=13, fontweight="bold")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Accuracy")
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Loss
    ax = axes[1]
    if "loss" in df.columns:
        ax.plot(epochs_range, df["loss"], label="Train Loss", marker="o", linewidth=2)
    if "val_loss" in df.columns:
        ax.plot(epochs_range, df["val_loss"], label="Val Loss", marker="s", linewidth=2)
    ax.set_title("Training and Validation Loss", fontsize=13, fontweight="bold")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Loss")
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    out_path = save_path or (config.ARTIFACTS_DIR / "training_curves.png")
    plt.savefig(out_path, dpi=150)
    print(f"Kurva training disimpan ke: {out_path}")
    plt.close()


def compute_confusion_and_report(model, test_ds, class_names, save_dir=None):
    """
    Menghitung confusion matrix dan classification report (precision,
    recall, F1-score per kelas) pada test set. Ini BELUM ada di notebook
    asli dan sangat disarankan untuk dilaporkan di naskah jurnal.
    """
    save_dir = save_dir or config.ARTIFACTS_DIR
    num_classes = len(class_names)

    print("\nMenghitung prediksi pada test set...")
    y_true, y_pred = [], []
    for images, labels in test_ds:
        preds = model.predict(images, verbose=0)
        y_pred.extend(np.argmax(preds, axis=1))
        y_true.extend(labels.numpy())

    y_true = np.array(y_true)
    y_pred = np.array(y_pred)

    # --- Classification Report ---
    report_text = classification_report(
        y_true, y_pred, labels=np.arange(len(class_names)), target_names=class_names, digits=4, zero_division=0
    )
    print("\nClassification Report:")
    print(report_text)

    report_dict = classification_report(
        y_true, y_pred, labels=np.arange(len(class_names)), target_names=class_names, output_dict=True, digits=4, zero_division=0
    )
    report_df = pd.DataFrame(report_dict).transpose()

    report_csv_path = save_dir / "classification_report.csv"
    report_df.to_csv(report_csv_path)
    print(f"Classification report disimpan ke: {report_csv_path}")

    # Simpan juga versi teks
    report_txt_path = save_dir / "classification_report.txt"
    with open(report_txt_path, "w") as f:
        f.write(report_text)
    print(f"Classification report (teks) disimpan ke: {report_txt_path}")

    # --- Confusion Matrix ---
    cm = confusion_matrix(y_true, y_pred)

    # Tentukan ukuran figure berdasarkan jumlah kelas
    fig_size = max(10, num_classes * 0.4)
    fig, ax = plt.subplots(figsize=(fig_size, fig_size * 0.85))

    im = ax.imshow(cm, cmap="Blues", interpolation="nearest")
    ax.set_title("Confusion Matrix (Test Set)", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Predicted Label", fontsize=11)
    ax.set_ylabel("True Label", fontsize=11)

    # Tambahkan tick labels (nama kelas)
    tick_fontsize = max(5, min(8, 300 // num_classes))
    ax.set_xticks(range(num_classes))
    ax.set_yticks(range(num_classes))
    ax.set_xticklabels(class_names, rotation=90, ha="center", fontsize=tick_fontsize)
    ax.set_yticklabels(class_names, fontsize=tick_fontsize)

    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

    cm_path = save_dir / "confusion_matrix.png"
    fig.savefig(cm_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Confusion matrix disimpan ke: {cm_path}")

    return cm, report_df


def main():
    print("=" * 60)
    print("  PLANT DISEASE CLASSIFIER — Evaluation")
    print("=" * 60)

    model = load_trained_model()
    datasets = data_module.get_datasets()

    metrics = evaluate_accuracy(model, datasets["train_ds"], datasets["val_ds"], datasets["test_ds"])
    plot_training_curves()
    compute_confusion_and_report(model, datasets["test_ds"], datasets["info"]["class_names"])

    print(f"\n{'=' * 60}")
    print("  Evaluasi selesai!")
    print(f"  Train: {metrics['train_acc']:.4f} | Val: {metrics['val_acc']:.4f} | Test: {metrics['test_acc']:.4f}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
