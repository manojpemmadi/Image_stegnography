import React from "react";

function Header() {
  return (
    <header className="header">
      <div className="badge">Deep Learning · GAN Steganography</div>
      <h1 className="header-title">AI Image Steganography System</h1>
      <p className="header-subtitle">
        Hide a <strong>secret image</strong> inside a <strong>cover image</strong>{" "}
        using a GAN-based deep learning model, then recover it with high
        fidelity. Inspect imperceptibility using PSNR and SSIM metrics.
      </p>
    </header>
  );
}

export default Header;

