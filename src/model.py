"""
src/model.py
Definisi arsitektur CNN (4 blok konvolusi) untuk klasifikasi
penyakit daun tanaman, identik secara konsep dengan notebook asli.
"""

import tensorflow as tf

import config


def build_augmentation_layer():
    return tf.keras.Sequential(
        [
            tf.keras.layers.RandomFlip("horizontal"),
            tf.keras.layers.RandomRotation(0.08),
            tf.keras.layers.RandomZoom(0.1),
        ],
        name="augmentation",
    )


def build_model(num_classes, img_size=None, learning_rate=None):
    """Membangun dan mengompilasi model CNN."""
    img_size = img_size or config.IMG_SIZE
    learning_rate = learning_rate or config.LEARNING_RATE

    augmentation = build_augmentation_layer()

    model = tf.keras.Sequential(
        [
            tf.keras.layers.Input(shape=(img_size[0], img_size[1], 3)),
            augmentation,
            tf.keras.layers.Conv2D(32, 3, activation="relu", padding="same"),
            tf.keras.layers.MaxPooling2D(),
            tf.keras.layers.Conv2D(64, 3, activation="relu", padding="same"),
            tf.keras.layers.MaxPooling2D(),
            tf.keras.layers.Conv2D(128, 3, activation="relu", padding="same"),
            tf.keras.layers.MaxPooling2D(),
            tf.keras.layers.Conv2D(256, 3, activation="relu", padding="same"),
            tf.keras.layers.MaxPooling2D(),
            tf.keras.layers.Dropout(0.3),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(256, activation="relu"),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(num_classes, activation="softmax", dtype="float32"),
        ]
    )

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


def build_inference_model(trained_model, img_size=None):
    """
    Membangun ulang model tanpa layer augmentasi (augmentasi hanya
    relevan saat training). Diperlukan agar konversi ke TFLite mulus.
    """
    img_size = img_size or config.IMG_SIZE
    inputs = tf.keras.Input(shape=(img_size[0], img_size[1], 3), dtype=tf.float32)
    x = inputs
    for layer in trained_model.layers:
        # Skip layer augmentasi (Sequential berisi RandomFlip/Rotation/Zoom)
        if getattr(layer, "name", "").lower().startswith("augmentation"):
            continue
        # Skip InputLayer karena kita sudah buat Input baru di atas
        if isinstance(layer, tf.keras.layers.InputLayer):
            continue
        x = layer(x)
    inference_model = tf.keras.Model(inputs, x, name="inference_model")
    print(f"Inference model berhasil dibuat: {inference_model.count_params():,} parameter")
    return inference_model
