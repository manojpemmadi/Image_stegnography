import React from "react";

function ResultsGrid({ stegoUrl, recoveredSecretUrl, reconstructedCoverUrl }) {
  const cards = [
    {
      title: "Stego Image",
      description:
        "Visually similar to the cover, but contains the embedded secret.",
      url: stegoUrl,
    },
    {
      title: "Recovered Secret Image",
      description: "Secret reconstructed from the stego image.",
      url: recoveredSecretUrl,
    },
    {
      title: "Reconstructed Cover Image",
      description: "Model's reconstruction of the original cover image.",
      url: reconstructedCoverUrl,
    },
  ];

  return (
    <div className="three-column-grid">
      {cards.map((card) => (
        <div key={card.title} className="card glass-card result-card">
          <h3 className="card-title">{card.title}</h3>
          <p className="card-description">{card.description}</p>
          <div className="result-image-wrapper">
            {card.url ? (
              <img
                src={card.url}
                alt={card.title}
                className="result-image"
              />
            ) : (
              <div className="result-placeholder">
                <span>No result yet</span>
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

export default ResultsGrid;

