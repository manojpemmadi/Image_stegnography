import React from "react";

function ActionPanel({ onRun, loading }) {
  return (
    <section className="section-block">
      <div className="card glass-card action-card">
        <h2 className="section-title">Action Panel</h2>
        <p className="card-description">
          Once both images are uploaded, start the GAN steganography pipeline to
          generate the stego image and recover the secret.
        </p>
        <button
          type="button"
          className="primary-button"
          onClick={onRun}
          disabled={loading}
        >
          {loading ? (
            <span className="spinner">
              <span className="spinner-dot" />
              <span className="spinner-dot" />
              <span className="spinner-dot" />
            </span>
          ) : (
            "Hide Secret & Reveal"
          )}
        </button>
      </div>
    </section>
  );
}

export default ActionPanel;

