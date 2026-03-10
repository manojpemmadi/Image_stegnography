from typing import Dict

import numpy as np
from skimage.metrics import peak_signal_noise_ratio, structural_similarity


def compute_psnr_ssim(
    ref: np.ndarray, test: np.ndarray, data_range: float = 1.0
) -> Dict[str, float]:
    """
    Compute PSNR and SSIM between two images.

    Both inputs should be numpy arrays in [0, data_range] with shape (H, W, 3).
    """
    ref = np.clip(ref, 0.0, data_range)
    test = np.clip(test, 0.0, data_range)

    # Remove any leading singleton dimensions (e.g., batch)
    ref = np.squeeze(ref)
    test = np.squeeze(test)

    # Ensure shape is (H, W, C)
    if ref.ndim != 3 or test.ndim != 3:
        raise ValueError(
            f"Expected images with shape (H, W, C), got {ref.shape} and {test.shape}"
        )

    psnr_val = float(peak_signal_noise_ratio(ref, test, data_range=data_range))
    ssim_val = float(
        structural_similarity(
            ref,
            test,
            channel_axis=2,
            data_range=data_range,
        )
    )
    return {"psnr": psnr_val, "ssim": ssim_val}

