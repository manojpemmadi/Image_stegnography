import React from "react";

function MetricCard({ label, value, suffix }) {
  return (
    <div className="metric-card glass-card">
      <div className="metric-label">{label}</div>
      <div className="metric-value">
        {value !== null && value !== undefined ? value.toFixed(3) : "--"}
        {suffix && <span className="metric-suffix">{suffix}</span>}
      </div>
    </div>
  );
}

function MetricsPanel({ metrics }) {
  const {
    psnrCoverStego,
    ssimCoverStego,
    psnrSecretRecovered,
    ssimSecretRecovered,
  } = metrics || {};

  return (
    <div className="metrics-grid">
      <MetricCard
        label="PSNR (Cover → Stego)"
        value={psnrCoverStego}
        suffix=" dB"
      />
      <MetricCard
        label="SSIM (Cover → Stego)"
        value={ssimCoverStego}
        suffix=""
      />
      <MetricCard
        label="PSNR (Secret → Recovered)"
        value={psnrSecretRecovered}
        suffix=" dB"
      />
      <MetricCard
        label="SSIM (Secret → Recovered)"
        value={ssimSecretRecovered}
        suffix=""
      />
    </div>
  );
}

export default MetricsPanel;

