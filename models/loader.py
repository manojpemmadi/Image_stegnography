from typing import Tuple

import tensorflow as tf
from tensorflow.keras import Model, layers

from config.settings import (
    IMG_SIZE,
    SE_WEIGHTS_PATH,
    E_WEIGHTS_PATH,
    D_WEIGHTS_PATH,
    C_WEIGHTS_PATH,
)


def build_secret_encoder() -> Model:
    """
    SecretEncoder architecture copied from the training notebook.
    """
    inp = layers.Input((IMG_SIZE, IMG_SIZE, 3))
    x = layers.Conv2D(64, 3, strides=2, padding="same", activation="relu")(inp)
    x = layers.Conv2D(128, 3, strides=2, padding="same", activation="relu")(x)
    x = layers.Conv2D(64, 3, padding="same", activation="relu")(x)
    return Model(inp, x, name="SecretEncoder")


def build_encoder() -> Model:
    """
    Encoder architecture copied from the training notebook.
    Uses YUV color space and hides information in UV channels.
    """
    cover_in = layers.Input((IMG_SIZE, IMG_SIZE, 3), name="cover_input")
    secret_latent = layers.Input((IMG_SIZE // 4, IMG_SIZE // 4, 64), name="secret_latent")

    x = layers.Conv2DTranspose(
        64, 3, strides=2, padding="same", activation="relu"
    )(secret_latent)
    x = layers.Conv2DTranspose(
        32, 3, strides=2, padding="same", activation="relu"
    )(x)

    cover_yuv = layers.Lambda(lambda t: tf.image.rgb_to_yuv(t), name="rgb_to_yuv")(
        cover_in
    )
    cover_y = layers.Lambda(lambda t: t[:, :, :, 0:1], name="y_channel")(cover_yuv)
    cover_uv = layers.Lambda(lambda t: t[:, :, :, 1:3], name="uv_channels")(cover_yuv)

    combined = layers.Concatenate(name="concat_uv_latent")([cover_uv, x])
    r = layers.Conv2D(64, 3, padding="same", activation="relu")(combined)
    r = layers.Conv2D(2, 3, padding="same", activation="tanh")(r)

    UV_SCALE = 0.05
    uv_stego = layers.Lambda(
        lambda inputs: inputs[0] + UV_SCALE * inputs[1],
        name="uv_embed",
    )([cover_uv, r])

    stego_yuv = layers.Concatenate(name="stego_yuv")([cover_y, uv_stego])
    stego_rgb = layers.Lambda(lambda t: tf.image.yuv_to_rgb(t), name="yuv_to_rgb")(
        stego_yuv
    )

    return Model([cover_in, secret_latent], stego_rgb, name="Encoder")


def build_decoder() -> Model:
    """
    Decoder architecture copied from the training notebook.
    """
    inp = layers.Input((IMG_SIZE, IMG_SIZE, 3), name="stego_input")

    x = layers.Conv2D(64, 3, padding="same", activation="relu")(inp)
    x = layers.Conv2D(128, 3, strides=2, padding="same", activation="relu")(x)
    x = layers.Conv2D(128, 3, strides=2, padding="same", activation="relu")(x)

    latent = layers.Conv2D(64, 3, padding="same", activation="relu")(x)

    s = layers.Conv2DTranspose(
        128, 3, strides=2, padding="same", activation="relu"
    )(latent)
    s = layers.Conv2DTranspose(
        64, 3, strides=2, padding="same", activation="relu"
    )(s)
    secret_rec = layers.Conv2D(3, 3, padding="same", activation="sigmoid", name="secret_rec")(
        s
    )

    c = layers.Conv2DTranspose(
        128, 3, strides=2, padding="same", activation="relu"
    )(latent)
    c = layers.Conv2DTranspose(
        64, 3, strides=2, padding="same", activation="relu"
    )(c)
    cover_rec = layers.Conv2D(3, 3, padding="same", activation="sigmoid", name="cover_rec")(
        c
    )

    return Model(inp, [secret_rec, cover_rec], name="Decoder")


def build_discriminator() -> Model:
    """
    Discriminator architecture copied from the training notebook.
    (Not used during inference but loaded for completeness.)
    """
    inp = layers.Input((IMG_SIZE, IMG_SIZE, 3), name="disc_input")
    x = layers.Conv2D(64, 4, strides=2, padding="same", activation="relu")(inp)
    x = layers.Conv2D(128, 4, strides=2, padding="same", activation="relu")(x)
    x = layers.Conv2D(256, 4, strides=2, padding="same", activation="relu")(x)
    out = layers.Conv2D(1, 4, padding="same", activation="sigmoid")(x)
    return Model(inp, out, name="Discriminator")


class StegoModels:
    """
    Container that rebuilds the four networks and loads their trained weights.
    Models are constructed to match the original training notebook exactly.
    """

    def __init__(self) -> None:
        self.secret_encoder: Model
        self.encoder: Model
        self.decoder: Model
        self.discriminator: Model
        self._load_models()

    def _load_models(self) -> None:
        # Rebuild architectures
        self.secret_encoder = build_secret_encoder()
        self.encoder = build_encoder()
        self.decoder = build_decoder()
        self.discriminator = build_discriminator()

        # Load weights (from Keras 3–compatible .weights.h5 files)
        self.secret_encoder.load_weights(str(SE_WEIGHTS_PATH))
        self.encoder.load_weights(str(E_WEIGHTS_PATH))
        self.decoder.load_weights(str(D_WEIGHTS_PATH))
        self.discriminator.load_weights(str(C_WEIGHTS_PATH))

    def hide(self, cover: tf.Tensor, secret: tf.Tensor) -> tf.Tensor:
        """
        Hide `secret` inside `cover` and return stego image tensor.
        Both inputs must be float32 tensors in [0, 1] with shape (1, IMG_SIZE, IMG_SIZE, 3).
        """
        cover_t = tf.convert_to_tensor(cover, dtype=tf.float32)
        secret_t = tf.convert_to_tensor(secret, dtype=tf.float32)
        latent = self.secret_encoder(secret_t, training=False)
        stego = self.encoder([cover_t, latent], training=False)
        return stego

    def reveal(self, stego: tf.Tensor) -> Tuple[tf.Tensor, tf.Tensor]:
        """
        Reveal secret and reconstructed cover from a stego image.
        Input must be float32 tensor in [0, 1] with shape (1, IMG_SIZE, IMG_SIZE, 3).
        Returns (recovered_secret, reconstructed_cover).
        """
        stego_t = tf.convert_to_tensor(stego, dtype=tf.float32)
        secret_rec, cover_rec = self.decoder(stego_t, training=False)
        return secret_rec, cover_rec


# Singleton instance used by the FastAPI app
stego_models = StegoModels()

