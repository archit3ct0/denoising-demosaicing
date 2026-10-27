# Evaluation script for demosaicing methods. Runs a set of reference images through a single demosaicing method.
# Generates fake Bayer filtered images from the references, demosaics them, and records performance metrics for later use.



# Configuration ======================================================================================================
test_image_directory = ""       # Directory containing test images
demosaicing_method = ""         # Demosaicing method to evaluate. Should be a function defined in helpers/demosaicing_methods.py
pre_denoising_method = "None"   # Discrete denoising method to apply before demosaicing. If None, no denoising is applied.
post_denoising_method = "None"  # Discrete denoising method to apply after demosaicing. If None, no denoising is applied.
bayer_pattern = "RGGB"          # Bayer pattern to use for mosaicing. Should be one of the supported patterns in helpers/generate_mosaic.py
generate_csv = "True"           # Generate CSV data for evaluated metrics
generate_plots = "False"        # TODO: Not implemented


# Import everything (libraries, helper functions) ====================================================================
import demosaicing_methods
import denoising_methods
from generate_mosaic import generate_mosaic
import numpy as np
from scipy.ndimage import gaussian_filter
import os
from PIL import Image



# Import test images ==================================================================================================
test_images_raw = [np.array(Image.open(os.path.join(test_image_directory, filename)))
                   for filename in os.listdir(test_image_directory)
                   if filename.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"))]



# Mosaic the test images =============================================================================================
test_images_mosaiced = generate_mosaic(test_images_raw, bayer_pattern)



# Process the mosaiced test images ===================================================================================
def process_image(image, pre_denoise=None, demosaic=None, post_denoise=None):
    if pre_denoise:
        image = getattr(denoising_methods, pre_denoise)(image)

    if demosaic:
        image = getattr(demosaicing_methods, demosaic)(image, bayer_pattern)

    if post_denoise:
        image = getattr(denoising_methods, post_denoise)(image)

    return image

test_images_processed = [process_image(image, pre_denoise=pre_denoising_method, demosaic=demosaicing_method, post_denoise=post_denoising_method) for image in test_images_mosaiced]



# Collect metrics for each image (kinda part of demosaicing, too, for metrics like computational complexity) ========
# Metric 1: Compute color PSNR relative to source image.
def cpsnr(original, processed, peak=None):
    # Determine peak value for incoming images (255 for 8 bit, etc.)
    if peak is None:
        if np.issubdtype(original.dtype, np.integer):
            peak = np.iinfo(original.dtype).max
        else:
            raise ValueError(
                "Specify peak explicitly for floating-point images."
            )

    if not np.isfinite(peak) or peak <= 0:
        raise ValueError("Peak must be a positive finite number.")

    # Actually implement CPSNR
    original = np.asarray(original, dtype=np.float64)
    processed = np.asarray(processed, dtype=np.float64)

    mse = np.mean((original - processed) ** 2)

    if mse == 0:
        return float("inf")

    return 10 * np.log10((peak ** 2) / mse)

cpsnr_values = np.array([cpsnr(original, processed, 255) for original, processed in zip(test_images_raw, test_images_processed)])

# Metric 2: Compute color-averaged SSIM relative to source image.
def ssim(original, processed, data_range: float=255, sigma: float=1.5, K1: float=0.01, K2: float=0.03, return_map: bool=False):
    if data_range <= 0 or sigma <= 0:
        raise ValueError("data_range and sigma must be positive.")
    
    x = np.asarray(original, dtype=np.float64)
    y = np.asarray(processed, dtype=np.float64)

    # Apply a 2-D Gaussian filter independently to each RGB channel.
    # This avoids smoothing across the color-channel dimension.
    filter_args = dict(sigma=(sigma, sigma, 0), mode="reflect")

    mu_x = gaussian_filter(x, **filter_args)
    mu_y = gaussian_filter(y, **filter_args)

    mu_x_sq = mu_x*mu_x
    mu_y_sq = mu_y*mu_y
    mu_xy = mu_x*mu_y

    sigma_x_sq = (gaussian_filter(x*x, **filter_args) - mu_x_sq)
    sigma_y_sq = (gaussian_filter(y*y, **filter_args) - mu_y_sq)
    sigma_xy = (gaussian_filter(x*y, **filter_args) - mu_xy)

    # Suppress small negative variances caused by floating-point rounding.
    sigma_x_sq = np.maximum(sigma_x_sq, 0.0)
    sigma_y_sq = np.maximum(sigma_y_sq, 0.0)

    C1 = (K1*data_range)**2
    C2 = (K2*data_range)**2

    numerator = (2*mu_xy + C1)*(2*sigma_xy + C2)
    denominator = ((mu_x_sq + mu_y_sq + C1)*(sigma_x_sq + sigma_y_sq + C2))

    ssim_channels = numerator / denominator

    # Average the three channels at each pixel, then across the image.
    ssim_map = np.mean(ssim_channels, axis=2)
    score = float(np.mean(ssim_map))

    if return_map:
        return score, ssim_map

    return score

ssim_values = np.array([ssim(original, processed, 255) for original, processed in zip(test_images_raw, test_images_processed)])


# Make the results nice and export them to CSV, plots, etc. (easy to parse, so we can combine each method's results later)



# Easy said and done, right?