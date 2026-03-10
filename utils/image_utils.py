from io import BytesIO
from typing import Tuple

import numpy as np
from PIL import Image

from config.settings import IMG_SIZE


def pil_to_array(img: Image.Image) -> np.ndarray:
    """Convert PIL image to float32 numpy array in [0, 1] and resize to IMG_SIZE."""
    img = img.convert("RGB")
    img = img.resize((IMG_SIZE, IMG_SIZE), Image.Resampling.LANCZOS)
    arr = np.array(img).astype("float32") / 255.0
    return arr


def array_to_pil(arr: np.ndarray) -> Image.Image:
    """Convert float32 numpy array in [0, 1] to PIL RGB image."""
    arr = np.clip(arr, 0.0, 1.0)
    arr_uint8 = (arr * 255.0).round().astype("uint8")
    return Image.fromarray(arr_uint8, mode="RGB")


def encode_image_to_bytes(img: Image.Image, format: str = "PNG") -> bytes:
    """Encode PIL image to in-memory bytes (for download)."""
    buf = BytesIO()
    img.save(buf, format=format)
    buf.seek(0)
    return buf.read()


def preprocess_pair(cover: Image.Image, secret: Image.Image) -> Tuple[np.ndarray, np.ndarray]:
    """
    Preprocess a pair of images (cover, secret) to normalized numpy arrays.
    Returns arrays of shape (1, H, W, 3) in [0, 1].
    """
    c = pil_to_array(cover)
    s = pil_to_array(secret)
    c = np.expand_dims(c, axis=0)
    s = np.expand_dims(s, axis=0)
    return c, s


def preprocess_single(img: Image.Image) -> np.ndarray:
    """Preprocess a single image to shape (1, H, W, 3) float32 in [0, 1]."""
    arr = pil_to_array(img)
    arr = np.expand_dims(arr, axis=0)
    return arr

