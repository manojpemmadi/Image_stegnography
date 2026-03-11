import base64
from io import BytesIO
from typing import Dict, Tuple

import gradio as gr
import requests
from PIL import Image


API_BASE = "http://localhost:8000"


# ======================
# Backend interaction
# ======================
def _post_hide_reveal(cover: Image.Image, secret: Image.Image) -> Dict:
    """Send images to FastAPI backend and return JSON response."""
    buf_cover = BytesIO()
    buf_secret = BytesIO()
    cover.save(buf_cover, format="PNG")
    secret.save(buf_secret, format="PNG")
    buf_cover.seek(0)
    buf_secret.seek(0)

    files = {
        "cover_image": ("cover.png", buf_cover, "image/png"),
        "secret_image": ("secret.png", buf_secret, "image/png"),
    }
    resp = requests.post(f"{API_BASE}/hide-reveal", files=files, timeout=120)
    resp.raise_for_status()
    return resp.json()


def _decode_image_from_base64(b64_str: str) -> Image.Image:
    data = base64.b64decode(b64_str)
    return Image.open(BytesIO(data)).convert("RGB")


def hide_reveal_interface(
    cover: Image.Image, secret: Image.Image
) -> Tuple[
    Image.Image,
    Image.Image,
    Image.Image,
    str,
    float,
    float,
    float,
    float,
]:
    """
    Wrapper for Gradio: calls backend and returns displayable results + metrics.
    """
    if cover is None or secret is None:
        raise gr.Error("Please upload both a cover image and a secret image.")

    data = _post_hide_reveal(cover, secret)

    stego_img = _decode_image_from_base64(data["stego_image_base64"])
    recovered_secret_img = _decode_image_from_base64(
        data["recovered_secret_base64"]
    )
    reconstructed_cover_img = _decode_image_from_base64(
        data["reconstructed_cover_base64"]
    )

    m = data["metrics"]
    metrics_summary = (
        f"Cover ↔ Stego  |  PSNR: {m['psnr_cover_stego']:.2f} dB, "
        f"SSIM: {m['ssim_cover_stego']:.4f}\n"
        f"Secret ↔ Recovered  |  PSNR: {m['psnr_secret_recovered']:.2f} dB, "
        f"SSIM: {m['ssim_secret_recovered']:.4f}"
    )

    return (
        stego_img,
        recovered_secret_img,
        reconstructed_cover_img,
        metrics_summary,
        float(m["psnr_cover_stego"]),
        float(m["ssim_cover_stego"]),
        float(m["psnr_secret_recovered"]),
        float(m["ssim_secret_recovered"]),
    )


# ======================
# Styling (Glassmorphism)
# ======================
GLASSMORPHISM_CSS = """
body {
    background: radial-gradient(circle at top left, #1f2937, #020617);
    font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.main-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem 1rem 3rem 1rem;
}

.glass-card {
    background: rgba(15, 23, 42, 0.75);
    border-radius: 18px;
    border: 1px solid rgba(148, 163, 184, 0.35);
    box-shadow: 0 20px 40px rgba(15, 23, 42, 0.6);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    padding: 1.25rem;
}

.glass-card-light {
    background: rgba(15, 23, 42, 0.55);
}

.title-text {
    text-align: center;
    color: #e5e7eb;
    margin-bottom: 0.25rem;
    font-size: 2.0rem;
    font-weight: 700;
    letter-spacing: 0.03em;
}

.subtitle-text {
    text-align: center;
    color: #9ca3af;
    font-size: 0.95rem;
    max-width: 720px;
    margin: 0 auto 1.5rem auto;
}

.section-title {
    color: #e5e7eb;
    font-size: 1.05rem;
    font-weight: 600;
    margin-bottom: 0.75rem;
    letter-spacing: 0.03em;
    text-transform: uppercase;
}

.metric-value {
    font-size: 1.4rem;
    font-weight: 600;
    color: #e5e7eb;
}

.metric-label {
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #9ca3af;
}

.gr-button.primary {
    background: linear-gradient(135deg, #4f46e5, #06b6d4);
    border: none;
    color: white;
    font-weight: 600;
    border-radius: 999px;
    box-shadow: 0 12px 25px rgba(37, 99, 235, 0.4);
}

.gr-button.primary:hover {
    filter: brightness(1.08);
    box-shadow: 0 18px 40px rgba(37, 99, 235, 0.6);
}

.gradio-container {
    background: transparent !important;
}

.input-card, .output-card {
    min-height: 260px;
}

@media (max-width: 900px) {
    .main-container {
        padding: 1.5rem 0.75rem 2.5rem 0.75rem;
    }
}
"""


# ======================
# UI Construction
# ======================
def build_interface() -> gr.Blocks:
    with gr.Blocks(
        title="GAN Based Image Steganography System",
    ) as demo:
        with gr.Row(elem_classes=["main-container"]):
            # Header
            gr.Markdown(
                """
                <div class="glass-card glass-card-light" style="padding: 1.5rem 1.75rem; margin-bottom: 1.75rem;">
                  <div class="title-text">GAN Based Image Steganography System</div>
                  <div class="subtitle-text">
                    Hide a <strong>secret image</strong> inside a <strong>cover image</strong> using a GAN-based deep learning model,
                    then recover it with high fidelity. Explore how imperceptible steganography can be using PSNR and SSIM metrics.
                  </div>
                </div>
                """,
                elem_id="header-card",
            )

            # Inputs section
            with gr.Row(equal_height=True):
                with gr.Column(scale=1):
                    gr.Markdown(
                        '<div class="section-title">Input Images</div>',
                        elem_id="inputs-title",
                    )
                    with gr.Row():
                        with gr.Column(elem_classes=["glass-card", "input-card"]):
                            gr.Markdown(
                                "##### Cover Image\n"
                                "<span style='color:#9ca3af;font-size:0.85rem;'>"
                                "Upload the visible carrier image (PNG / JPG).</span>"
                            )
                            cover_in = gr.Image(
                                type="pil",
                                image_mode="RGB",
                                sources=["upload"],
                                label=None,
                            )
                        with gr.Column(elem_classes=["glass-card", "input-card"]):
                            gr.Markdown(
                                "##### Secret Image\n"
                                "<span style='color:#9ca3af;font-size:0.85rem;'>"
                                "Upload the hidden content image (PNG / JPG).</span>"
                            )
                            secret_in = gr.Image(
                                type="pil",
                                image_mode="RGB",
                                sources=["upload"],
                                label=None,
                            )

            # Action panel
            with gr.Row():
                with gr.Column(elem_classes=["glass-card", "glass-card-light"]):
                    gr.Markdown(
                        '<div class="section-title">Action Panel</div>',
                    )
                    run_btn = gr.Button(
                        "Hide Secret & Reveal",
                        variant="primary",
                        size="lg",
                    )

            # Results section
            with gr.Row(equal_height=True):
                with gr.Column():
                    gr.Markdown(
                        '<div class="section-title">Results</div>',
                        elem_id="results-title",
                    )
                    with gr.Row():
                        with gr.Column(elem_classes=["glass-card", "output-card"]):
                            gr.Markdown(
                                "##### Stego Image\n"
                                "<span style='color:#9ca3af;font-size:0.8rem;'>"
                                "Visually similar to the cover, but contains the hidden secret.</span>"
                            )
                            stego_out = gr.Image(
                                type="pil",
                                interactive=False,
                                label=None,
                            )
                        with gr.Column(elem_classes=["glass-card", "output-card"]):
                            gr.Markdown(
                                "##### Recovered Secret Image\n"
                                "<span style='color:#9ca3af;font-size:0.8rem;'>"
                                "Secret reconstructed from the stego image.</span>"
                            )
                            recovered_secret_out = gr.Image(
                                type="pil",
                                interactive=False,
                                label=None,
                            )
                        with gr.Column(elem_classes=["glass-card", "output-card"]):
                            gr.Markdown(
                                "##### Reconstructed Cover Image\n"
                                "<span style='color:#9ca3af;font-size:0.8rem;'>"
                                "Model's reconstruction of the original cover.</span>"
                            )
                            reconstructed_cover_out = gr.Image(
                                type="pil",
                                interactive=False,
                                label=None,
                            )

            # Metrics section
            with gr.Row():
                with gr.Column(elem_classes=["glass-card", "glass-card-light"]):
                    gr.Markdown(
                        '<div class="section-title">Quality Metrics</div>',
                    )
                    with gr.Row():
                        with gr.Column(elem_classes=["glass-card"]):
                            gr.Markdown(
                                '<div class="metric-label">Cover → Stego (PSNR)</div>',
                                elem_id="psnr_cs_label",
                            )
                            psnr_cover_stego = gr.Number(
                                show_label=False,
                                precision=2,
                                elem_classes=["metric-value"],
                            )
                        with gr.Column(elem_classes=["glass-card"]):
                            gr.Markdown(
                                '<div class="metric-label">Cover → Stego (SSIM)</div>',
                                elem_id="ssim_cs_label",
                            )
                            ssim_cover_stego = gr.Number(
                                show_label=False,
                                precision=4,
                                elem_classes=["metric-value"],
                            )
                    with gr.Row():
                        with gr.Column(elem_classes=["glass-card"]):
                            gr.Markdown(
                                '<div class="metric-label">Secret → Recovered (PSNR)</div>',
                                elem_id="psnr_sr_label",
                            )
                            psnr_secret_rec = gr.Number(
                                show_label=False,
                                precision=2,
                                elem_classes=["metric-value"],
                            )
                        with gr.Column(elem_classes=["glass-card"]):
                            gr.Markdown(
                                '<div class="metric-label">Secret → Recovered (SSIM)</div>',
                                elem_id="ssim_sr_label",
                            )
                            ssim_secret_rec = gr.Number(
                                show_label=False,
                                precision=4,
                                elem_classes=["metric-value"],
                            )

                    metrics_summary_box = gr.Textbox(
                        label="Summary",
                        lines=2,
                        interactive=False,
                    )

            # Wiring
            run_btn.click(
                fn=hide_reveal_interface,
                inputs=[cover_in, secret_in],
                outputs=[
                    stego_out,
                    recovered_secret_out,
                    reconstructed_cover_out,
                    metrics_summary_box,
                    psnr_cover_stego,
                    ssim_cover_stego,
                    psnr_secret_rec,
                    ssim_secret_rec,
                ],
                api_name="hide_reveal",
            )

    return demo


if __name__ == "__main__":
    demo = build_interface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        css=GLASSMORPHISM_CSS,
        theme=gr.themes.Soft(primary_hue="indigo", neutral_hue="slate"),
    )

