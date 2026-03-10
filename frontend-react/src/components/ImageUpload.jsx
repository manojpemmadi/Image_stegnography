import React, { useCallback, useRef } from "react";

function ImageUpload({
  label,
  description,
  file,
  setFile,
  previewUrl,
  setPreviewUrl,
}) {
  const inputRef = useRef(null);

  const handleFiles = useCallback(
    (files) => {
      if (!files || !files.length) return;
      const selected = files[0];
      if (!selected.type.startsWith("image/")) {
        return;
      }
      setFile(selected);
      const url = URL.createObjectURL(selected);
      setPreviewUrl(url);
    },
    [setFile, setPreviewUrl]
  );

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    handleFiles(e.dataTransfer.files);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleChange = (e) => {
    handleFiles(e.target.files);
  };

  const openFileDialog = () => {
    if (inputRef.current) {
      inputRef.current.click();
    }
  };

  return (
    <div className="card glass-card upload-card">
      <div className="card-header">
        <h3 className="card-title">{label}</h3>
        <p className="card-description">{description}</p>
      </div>
      <div
        className="upload-dropzone"
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onClick={openFileDialog}
      >
        {previewUrl ? (
          <img src={previewUrl} alt={label} className="upload-preview" />
        ) : (
          <div className="upload-placeholder">
            <span className="upload-icon">⬆</span>
            <p>Drag &amp; drop an image here, or click to browse</p>
            <p className="upload-hint">PNG or JPG, up to a few MB</p>
          </div>
        )}
        <input
          ref={inputRef}
          type="file"
          accept="image/png,image/jpeg"
          style={{ display: "none" }}
          onChange={handleChange}
        />
      </div>
      {file && <div className="file-name">Selected: {file.name}</div>}
    </div>
  );
}

export default ImageUpload;

