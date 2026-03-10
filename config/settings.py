import os
from pathlib import Path

# Base project directory (where this file lives)
BASE_DIR = Path(__file__).resolve().parent.parent

# Image settings
IMG_SIZE = 256

# Model directory (user-provided absolute path)
MODEL_DIR = Path(r"D:\Image stegnography Web\Model Files")

# Model file paths
SECRET_ENCODER_PATH = MODEL_DIR / "SecretEncoder.keras"
ENCODER_PATH = MODEL_DIR / "Encoder.keras"
DECODER_PATH = MODEL_DIR / "Decoder.keras"
DISCRIMINATOR_PATH = MODEL_DIR / "Discriminator.keras"

# Optional: weights (not strictly needed if full models are loaded)
SE_WEIGHTS_PATH = MODEL_DIR / "SE.weights.h5"
E_WEIGHTS_PATH = MODEL_DIR / "E.weights.h5"
D_WEIGHTS_PATH = MODEL_DIR / "D.weights.h5"
C_WEIGHTS_PATH = MODEL_DIR / "C.weights.h5"

