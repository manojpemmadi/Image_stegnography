## GAN–Based Image Steganography Web Application

This project implements a **deep learning based image steganography** system that securely hides a **secret image inside a cover image**. The goal is to enable safe transmission of **sensitive visual data** such as medical records, confidential documents, forensic evidence, or satellite images over digital networks without revealing the presence of **hidden information**.

The system uses a **Generative Adversarial Network (GAN)** architecture for **reversible image steganography**. Instead of modifying all **RGB channels**, the method converts images to the **YUV color space** and embeds secret information only in the **chrominance (U and V) channels**, while preserving the **luminance channel**. This approach reduces **visual distortion** and makes the hidden information **less detectable**.

The framework includes a **Secret Encoder**, **Generator (Embedding Network)**, **Decoder (Extraction Network)**, and **Discriminator**, which work together to generate **realistic stego images** and accurately recover both the **hidden secret image** and the **original cover image**. The system is implemented using **TensorFlow/Keras** for model training, **FastAPI** for the backend, and **React** for the frontend interface.

## 1. High‑Level Architecture

The system is organized into three main layers:

- **Model Layer (TensorFlow/Keras)**
  - Implements the **Chroma‑Warp GAN** for reversible image steganography.
  - Components:
    - **Secret Encoder** – compresses and encodes the secret image into a latent representation.
    - **Generator / Encoder (Embedding Network)** – embeds the latent secret into the **U and V chrominance channels** of the cover image (in YUV space), producing a **stego image** that looks visually like the original cover.
    - **Decoder (Extraction Network)** – recovers both the **secret image** and the **reconstructed cover image** from the stego image.
    - **Discriminator** – judges whether images are real or stego during training (loaded here for completeness; not used at inference time).

- **Backend Layer (FastAPI)**
  - Exposes a **REST API** for the hide/reveal pipeline.
  - Handles image uploads, preprocessing, model inference, and metric computation.
  - Returns images encoded as **Base64** alongside **PSNR/SSIM quality metrics**.

- **Frontend Layer (React SPA)**
  - **React SPA** – directory `frontend-react/`:
    - Modern single‑page UI (Vite + React 18) with glassmorphism styling.
    - Calls the FastAPI `/hide-reveal` endpoint.

---

## 2. Steganography Method: Chroma‑Warp GAN in YUV Space

- **Color‑space conversion**
  - The encoder network converts the cover image from **RGB → YUV**.
  - Y channel (luminance/brightness) is **preserved** to maintain visual appearance.
  - U and V channels (chrominance/color information) are used for embedding.

- **Secret embedding (Generator / Encoder)**
  - The **Secret Encoder** compresses the secret image into a latent feature map.
  - This latent representation is upsampled and concatenated with the **UV channels** of the cover image.
  - A learnable perturbation is generated and added only to the UV channels with a small scale factor (e.g. `UV_SCALE = 0.05`), producing stego‑UV.
  - The Y channel and modified UV channels are concatenated and converted back **YUV → RGB** to form the **stego image**.

- **Secret and cover recovery (Decoder)**
  - A dedicated **Decoder** network takes the stego image as input and outputs:
    - A **recovered secret image**.
    - A **reconstructed cover image**.
  - This makes the process **reversible steganography**, not just hidden‑message extraction.

- **Quality evaluation**
  - The backend computes **PSNR (Peak Signal‑to‑Noise Ratio)** and **SSIM (Structural Similarity Index)**:
    - Between **cover ↔ stego** (imperceptibility of embedding).
    - Between **secret ↔ recovered secret** (fidelity of recovery).

---

## 3. Project Structure

- **`config/`**
  - `settings.py` – global configuration:
    - `IMG_SIZE = 256` – working resolution for all images.
    - `MODEL_DIR` – absolute path to model files (`Model Files/`).
    - Paths for `.keras` models and `.weights.h5` weights.

- **`models/`**
  - `loader.py`
    - Rebuilds the four Keras networks to **match the training notebook**:
      - `SecretEncoder`
      - `Encoder` (YUV chrominance embedding)
      - `Decoder` (recovers secret + reconstructed cover)
      - `Discriminator`
    - Loads pre‑trained weights from `Model Files/`.
    - Provides a singleton `stego_models` with:
      - `hide(cover, secret)` → stego tensor.
      - `reveal(stego)` → `(recovered_secret, reconstructed_cover)`.

- **`utils/`**
  - `image_utils.py`
    - `pil_to_array` – converts and resizes images to `IMG_SIZE × IMG_SIZE`, normalizes to `[0, 1]`.
    - `array_to_pil` – converts `[0, 1]` float arrays back to RGB `PIL.Image`.
    - `preprocess_pair`, `preprocess_single` – convenience methods for model inputs.
  - `metrics.py`
    - `compute_psnr_ssim` – uses **scikit‑image** to compute PSNR and SSIM on `(H, W, 3)` arrays.

- **`backend/`**
  - `main.py`
    - Creates the **FastAPI** app.
    - Adds permissive CORS middleware for local dev (`allow_origins=["*"]`).
    - Endpoints:
      - `GET /health` – simple health check.
      - `POST /hide-reveal` – main pipeline:
        1. Accepts `cover_image` and `secret_image` as file uploads.
        2. Preprocesses and normalizes images.
        3. Calls `stego_models.hide` to generate the **stego image**.
        4. Calls `stego_models.reveal` to recover the **secret** and **cover**.
        5. Computes PSNR/SSIM for both relevant pairs.
        6. Encodes images to **Base64 PNG strings** for JSON transport.
  - `schemas.py`
    - Pydantic models describing the API responses (`HideRevealResponse`, `Metrics`, `ErrorResponse`).

- **`Model Files/`**
  - Contains the saved **Keras models** and **weight files**:
    - `SecretEncoder.keras`, `Encoder.keras`, `Decoder.keras`, `Discriminator.keras`
    - `SE.weights.h5`, `E.weights.h5`, `D.weights.h5`, `C.weights.h5`
    - `model_config.json`, `data_split.json`, etc.

- **`frontend-react/`**
  - React + Vite single‑page app:
    - `src/App.jsx` – orchestrates the UI flow and handles API calls.
    - Components:
      - `Header` – project title/description.
      - `ImageUpload` – cover/secret file upload with previews.
      - `ActionPanel` – “Run” button and loading state.
      - `ResultsGrid` – shows stego, recovered secret, reconstructed cover.
      - `MetricsPanel` – displays PSNR/SSIM values.
    - Uses `fetch` to call `POST http://localhost:8000/hide-reveal` with `FormData`.

- **Root files**
  - `requirements.txt` – Python dependencies (FastAPI, TensorFlow/Keras, PIL, NumPy, scikit‑image, etc.).
  - `Major_project_manoj.ipynb` – original training/experiment notebook.

---

## 4. Technologies Used

- **Deep Learning / Computer Vision**
  - **TensorFlow / Keras** – model definitions and inference.
  - **GAN‑based architecture** with Secret Encoder, Encoder (Generator), Decoder, Discriminator.
  - **YUV color space** operations using `tf.image.rgb_to_yuv` and `tf.image.yuv_to_rgb`.

- **Backend**
  - **FastAPI** – high‑performance web framework for the API.
  - **Uvicorn** – ASGI server.
  - **Pydantic** – data validation and response models.

- **Frontend**
  - **React 18** – component‑based SPA front‑end.
  - **Vite** – fast dev server and bundler for the React app.
  - Custom **CSS** with glassmorphism styling.

- **Utilities**
  - **Pillow (PIL)** – image loading, conversion, and saving.
  - **NumPy** – array manipulation.
  - **scikit‑image** – PSNR and SSIM computation.

---

## 5. Installation

### 5.1. Python Environment

1. Create and activate a virtual environment (optional but recommended):

   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows PowerShell
   ```

2. Install Python dependencies from the project root (`D:\Image stegnography Web`):

   ```bash
   pip install -r requirements.txt
   ```

3. Ensure the **model files** are present in `Model Files/` with the expected names from `config/settings.py`.

### 5.2. React Frontend Dependencies

From `D:\Image stegnography Web\frontend-react`:

```bash
npm install
```

This installs React, Vite, and other front‑end dependencies.

---

## 6. Running the Application

### 6.1. Start the FastAPI Backend

From the project root (`D:\Image stegnography Web`):

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

This will:

- Construct all four Keras models and load their weights from `Model Files/`.
- Start the API at `http://localhost:8000`.
- Expose:
  - `GET /health` – health check (`{"status": "ok"}` on success).
  - `POST /hide-reveal` – main steganography endpoint.

### 6.2. Run the React Frontend

In a **second terminal**, from `D:\Image stegnography Web\frontend-react`:

```bash
npm run dev
```

Then open the URL printed by Vite (typically `http://localhost:5173/`) in your browser.

The React app will:

- Talk to the FastAPI backend at `http://localhost:8000` (`API_BASE` in `App.jsx`).
- Provide:
  - Two upload panels for **cover** and **secret** images.
  - A **“Hide Secret & Reveal”** style action button.
  - A responsive results grid for stego/recovered/reconstructed images.
  - A metrics panel showing PSNR and SSIM values.

> **Note:** Make sure the **FastAPI backend is running first**, otherwise the React app will show an error when calling `/hide-reveal`.

---

## 7. API Overview

- **`GET /health`**
  - **Purpose**: Quick health check.
  - **Response**: `{"status": "ok"}` when the service is healthy.

- **`POST /hide-reveal`**
  - **Inputs (multipart/form-data)**:
    - `cover_image` – uploaded cover image file (PNG/JPG).
    - `secret_image` – uploaded secret image file (PNG/JPG).
  - **Processing**:
    1. Converts both images to RGB, resizes to 256×256, normalizes to `[0, 1]`.
    2. Runs the **Secret Encoder + Encoder** to produce a **stego image**.
    3. Runs the **Decoder** to get the **recovered secret** and **reconstructed cover**.
    4. Computes **PSNR** and **SSIM** for both relevant pairs.
  - **Response JSON (`HideRevealResponse`)**:
    - `stego_image_base64` – Base64 PNG string of stego image.
    - `recovered_secret_base64` – Base64 PNG string of recovered secret.
    - `reconstructed_cover_base64` – Base64 PNG string of reconstructed cover.
    - `metrics`:
      - `psnr_cover_stego`
      - `ssim_cover_stego`
      - `psnr_secret_recovered`
      - `ssim_secret_recovered`

Both the backend and the React frontend use this same endpoint.

---

## 8. Intended Use‑Cases and Notes

- **Intended use‑cases**
  - Privacy‑preserving sharing of **medical images** or diagnostics.
  - Secure embedding of **confidential document scans** into benign covers.
  - Protecting **forensic evidence** or **surveillance imagery** against interception.
  - Covert transmission of **satellite images** or sensitive remote‑sensing data.

- **Important notes**
  - This is a **research / educational implementation** of an image steganography system.
  - Real‑world deployment should consider:
    - Strong access control and encryption of stored model weights.
    - Network security, logging, and auditing.
    - Legal and ethical constraints around hiding information in media.

---

## 9. Quick Start Summary

- **Step 1**: Install Python dependencies – `pip install -r requirements.txt`.
- **Step 2**: Ensure the model files are in `Model Files/` as configured in `config/settings.py`.
- **Step 3**: Start the backend – `uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000`.
- **Step 4**: From `frontend-react/`, run `npm install` (once) then `npm run dev` to use the React UI.
- **Step 5**: Upload a **cover** and **secret** image, run the pipeline, and inspect the stego image, recovered secret, reconstructed cover, and quality metrics.

