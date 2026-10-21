# Demosaicing methods here as functions. Each takes a single image as input and returns a single image as output.
import numpy as np
from scipy.ndimage import convolve
from split_into_color_channels import *


def bilinear(image, bayer_pattern = "RGGB"):
    
    # Split back into color channels
    channels = split_into_color_channels(image, bayer_pattern)
    channels = channels.astype(np.float64)
    
    height, width, _ = channels.shape

    # Build a mask for each color channel covering the locations of the original photosites.
    # Uses Bayer pattern so as to not miss valid null data. This is different between Bayer patterns.
    _BAYER_MASKS = {
        "RGGB": ([[[1, 0], [0, 0]], [[0, 1], [1, 0]], [[0, 0], [0, 1]]]),
        "BGGR": ([[[0, 0], [0, 1]], [[0, 1], [1, 0]], [[1, 0], [0, 0]]]),
        "GBRG": ([[[0, 0], [1, 0]], [[1, 0], [0, 1]], [[0, 1], [0, 0]]]),
        "GRBG": ([[[0, 1], [0, 0]], [[1, 0], [0, 1]], [[0, 0], [1, 0]]]),
    }

    # Sliding kernels for regenerating each missing slot in a given color channel
    _CROSS =      np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]], dtype=np.float64)
    _DIAGONAL =   np.array([[1, 0, 1], [0, 0, 0], [1, 0, 1]], dtype=np.float64)

    photosite_mask = np.empty_like(channels)
    for c, pattern in enumerate(_BAYER_MASKS[bayer_pattern]):
        photosite_mask[:, :, c] = np.tile(pattern, (height // 2 + 1, width // 2 + 1))[:height, :width]

    demosaiced_image = channels.copy()
    green_sites = photosite_mask[:, :, 1] == 1

    for c in range(3):
        mask = photosite_mask[:, :, c]
        source = channels[:, :, c] * mask

        def estimate(kernel):
            numerator = convolve(source, kernel, mode='constant', cval=0.0)
            denominator = convolve(mask, kernel, mode='constant', cval=0.0)

            return np.divide(numerator, denominator, out=np.zeros_like(numerator), where=denominator > 0)

        cross_estimate = estimate(_CROSS)
        diagonal_estimate = estimate(_DIAGONAL)

        missing = mask == 0

        
        if c == 1:
            # Green missing at red or blue sites
            demosaiced_image[:, :, c][missing] = cross_estimate[missing]

        else:

            # Red/blue is missing at a green or opposite-color site
            opposite_sites = missing & ~green_sites
            green_missing = missing & green_sites

            # Opposite color: diagonal interpolation
            demosaiced_image[:, :, c][opposite_sites] = diagonal_estimate[opposite_sites]

            # Green sites: cross interpolation
            demosaiced_image[:, :, c][green_missing] = cross_estimate[green_missing]

    return demosaiced_image



def improved_linear(image, bayer_pattern = "RGGB"):
    pass



import numpy as np
from PIL import Image
from pathlib import Path

# Path to the mosaic image
mosaic_path = Path(r"C:\Users\Ethan\Desktop\DSC06071-scaled-mosaic.jpg")

# Load as a single-channel (grayscale) NumPy array
mosaic = np.array(Image.open(mosaic_path).convert("L"))

print("Mosaic shape:", mosaic.shape)

# Demosaic the single image
demosaiced = bilinear(mosaic)

# Save with "-demosaiced" appended to the filename
output_path = mosaic_path.with_name(
    f"{mosaic_path.stem.removesuffix('-mosaic')}-demosaiced.png"
)

# Save the demosaiced RGB image
Image.fromarray(np.asarray(demosaiced).astype(np.uint8)).save(output_path)

print(f"Demosaiced image saved to: {output_path}")