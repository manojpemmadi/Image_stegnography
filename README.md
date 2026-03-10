## GAN Image Steganography – FastAPI + Gradio Demo

This project exposes your trained GAN-based image steganography models (SecretEncoder, Encoder, Decoder, Discriminator) through a FastAPI backend and a Gradio web UI.

### Project Layout

- `config/` – global configuration (paths, image size)
- `models/` – model loader that initializes TensorFlow/Keras models once
- `utils/` – image preprocessing and evaluation metrics
- `backend/` – FastAPI application and API endpoints
- `frontend/` – Gradio UI that talks to the backend
- `Model Files/` – your saved `.keras` models and weights

### Prerequisites

1. Python 3.10+ recommended  
2. Install dependencies:

```bash
pip install -r requirements.txt
```

### Running the Backend (FastAPI)

From the project root (`D:\Image stegnography Web`):

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

This will:

- Load the four Keras models from `Model Files/`
- Start the API at `http://localhost:8000`
- Provide a health check at `GET /health`

### Running the Frontend (Gradio)

In a separate terminal, from the same project root:

```bash
python -m frontend.ui
```

This will open a browser window with a Gradio interface where you can:

- Upload a **cover image** and **secret image**
- Generate and visualize the **stego image**
- See the **recovered secret** and **reconstructed cover**
- View PSNR and SSIM metrics for:
  - Cover ↔ Stego
  - Secret ↔ Recovered Secret

### Notes

- The models are assumed to be saved in Keras 3 `.keras` format in `Model Files/` with the exact filenames:
  - `SecretEncoder.keras`, `Encoder.keras`, `Decoder.keras`, `Discriminator.keras`
- All images are internally resized to 256×256 and normalized to the [0, 1] range, matching your training setup.

