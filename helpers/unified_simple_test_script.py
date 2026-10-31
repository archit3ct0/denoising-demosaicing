# For running exclusively previously-implemented color reconstruction methods

# GENERIC IMPORTS
import numpy as np
import matplotlib.pyplot as plt

# MOSAICING
import colour

from colour_demosaicing import (
    ROOT_RESOURCES_EXAMPLES,
    demosaicing_CFA_Bayer_bilinear,
    demosaicing_CFA_Bayer_Malvar2004,
    demosaicing_CFA_Bayer_Menon2007,
    mosaicing_CFA_Bayer,
)

# METRICS
# CPSNR
from skimage.metrics import peak_signal_noise_ratio as psnr

# SSIM
from skimage.metrics import structural_similarity as ssim



# CONFIGURATION ======================================================================================================
test_image_directory = ""       # Directory containing test images
demosaicing_method = ""         # Demosaicing method to evaluate. Should be a function defined in helpers/demosaicing_methods.py
bayer_pattern = "RGGB"          # Bayer pattern to use for mosaicing. Should be one of the supported patterns in helpers/generate_mosaic.py
generate_csv = "True"           # Generate CSV data for evaluated metrics
data_range = 0                  # Color depth (in steps) of input images. 8-bit = 255, 16-bit = 65535, etc. Set to 0 for automatic based on storage type.


# IMPORT TEST IMAGES ==================================================================================================
test_images_raw = [np.array(Image.open(os.path.join(test_image_directory, filename)))
                   for filename in os.listdir(test_image_directory)
                   if filename.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"))]

if data_range == 0:
    first_image = test_images_raw[0]

    if np.issubdtype(first_image.dtype, np.integer):
        data_range = np.iinfo(first_image.dtype).max - np.iinfo(first_image.dtype).min
    else:
        data_range = 1.0 if first_image.min() >= 0 and first_image.max() <= 1 else first_image.max() - first_image.min()

print(f"Using data_range: {data_range}")


# MOSAIC THE TEST IMAGES =============================================================================================
test_images_mosaiced = [mosaicing_CFA_Bayer(image) for image in test_images_raw]


# DEMOSAIC USING SELECTED METHOD =====================================================================================
def process_image(image, demosaic=None):
    match demosaic:
        case "bilinear":
            image = demosaicing_CFA_Bayer_bilinear(image, bayer_pattern)
        case "Malvar2004":
            image = demosaicing_CFA_Bayer_Malvar2004(image, bayer_pattern)
        case "Menon2007":
            image = demosaicing_CFA_Bayer_Menon2007(image, bayer_pattern)

    return image

test_images_processed = [process_image(image, demosaic=demosaicing_method) for image in test_images_mosaiced]


# EVALUATE METRICS ===================================================================================================
# MSE - Each Color Channel
mse_values_red = np.array([psnr(original[..., 0], processed[..., 0]) for original, processed in zip(test_images_raw, test_images_processed)])
mse_values_green = np.array([psnr(original[..., 1], processed[..., 1]) for original, processed in zip(test_images_raw, test_images_processed)])
mse_values_blue = np.array([psnr(original[..., 2], processed[..., 2]) for original, processed in zip(test_images_raw, test_images_processed)])

# CPSNR - Whole Image
cpsnr_values = np.array([psnr(original, processed, data_range) for original, processed in zip(test_images_raw, test_images_processed)])

# SSIM - Whole Image
ssim_values = np.array([ssim(original, processed, -1, data_range) for original, processed in zip(test_images_raw, test_images_processed)])

