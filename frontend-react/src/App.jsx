import React, { useState } from "react";
import Header from "./components/Header.jsx";
import ImageUpload from "./components/ImageUpload.jsx";
import ActionPanel from "./components/ActionPanel.jsx";
import ResultsGrid from "./components/ResultsGrid.jsx";
import MetricsPanel from "./components/MetricsPanel.jsx";

const API_BASE = "http://localhost:8000";

function App() {
  const [coverFile, setCoverFile] = useState(null);
  const [secretFile, setSecretFile] = useState(null);
  const [coverPreview, setCoverPreview] = useState(null);
  const [secretPreview, setSecretPreview] = useState(null);

  const [stegoUrl, setStegoUrl] = useState(null);
  const [recoveredSecretUrl, setRecoveredSecretUrl] = useState(null);
  const [reconstructedCoverUrl, setReconstructedCoverUrl] = useState(null);

  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleRun = async () => {
    setError("");
    if (!coverFile || !secretFile) {
      setError("Please upload both a cover image and a secret image.");
      return;
    }
    try {
      setLoading(true);

      const formData = new FormData();
      formData.append("cover_image", coverFile);
      formData.append("secret_image", secretFile);

      const resp = await fetch(`${API_BASE}/hide-reveal`, {
        method: "POST",
        body: formData,
      });

      if (!resp.ok) {
        const errJson = await resp.json().catch(() => ({}));
        throw new Error(errJson.detail || "Backend error");
      }

      const data = await resp.json();

      const toObjectUrl = (b64) => {
        const binary = atob(b64);
        const len = binary.length;
        const bytes = new Uint8Array(len);
        for (let i = 0; i < len; i += 1) {
          bytes[i] = binary.charCodeAt(i);
        }
        const blob = new Blob([bytes], { type: "image/png" });
        return URL.createObjectURL(blob);
      };

      setStegoUrl(toObjectUrl(data.stego_image_base64));
      setRecoveredSecretUrl(toObjectUrl(data.recovered_secret_base64));
      setReconstructedCoverUrl(toObjectUrl(data.reconstructed_cover_base64));

      setMetrics({
        psnrCoverStego: data.metrics.psnr_cover_stego,
        ssimCoverStego: data.metrics.ssim_cover_stego,
        psnrSecretRecovered: data.metrics.psnr_secret_recovered,
        ssimSecretRecovered: data.metrics.ssim_secret_recovered,
      });
    } catch (e) {
      console.error(e);
      setError(e.message || "Unexpected error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-root">
      <div className="app-overlay-gradient" />
      <div className="app-container glass-panel">
        <Header />

        {error && <div className="error-banner">{error}</div>}

        <section className="section-block">
          <h2 className="section-title">Input Images</h2>
          <div className="two-column-grid">
            <ImageUpload
              label="Cover Image"
              description="Upload the visible carrier image (PNG / JPG)."
              file={coverFile}
              setFile={setCoverFile}
              previewUrl={coverPreview}
              setPreviewUrl={setCoverPreview}
            />
            <ImageUpload
              label="Secret Image"
              description="Upload the hidden content image (PNG / JPG)."
              file={secretFile}
              setFile={setSecretFile}
              previewUrl={secretPreview}
              setPreviewUrl={setSecretPreview}
            />
          </div>
        </section>

        <ActionPanel onRun={handleRun} loading={loading} />

        <section className="section-block">
          <h2 className="section-title">Results</h2>
          <ResultsGrid
            stegoUrl={stegoUrl}
            recoveredSecretUrl={recoveredSecretUrl}
            reconstructedCoverUrl={reconstructedCoverUrl}
          />
        </section>

        <section className="section-block">
          <h2 className="section-title">Quality Metrics</h2>
          <MetricsPanel metrics={metrics} />
        </section>
      </div>
    </div>
  );
}

export default App;

