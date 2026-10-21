# Evaluation script for demosaicing methods. Runs a set of reference images through a single demosaicing method.
# Generates fake Bayer filtered images from the references, demosaics them, and records performance metrics for later use.



# Configuration ======================================================================================================
test_image_directory = ""       # Directory containing test images
demosaicing_method = ""         # Demosaicing method to evaluate. Should be a function defined in helpers/demosaicing_methods.py
pre_denoising_method = "None"   # Discrete denoising method to apply before demosaicing. If None, no denoising is applied.
post_denoising_method = "None"  # Discrete denoising method to apply after demosaicing. If None, no denoising is applied.
bayer_pattern = "RGGB"          # Bayer pattern to use for mosaicing. Should be one of the supported patterns in helpers/generate_mosaic.py



# Import everything (libraries, helper functions) ====================================================================
import demosaicing_methods
import denoising_methods
from generate_mosaic import generate_mosaic
import numpy as np
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

test_images_demosaiced = [process_image(image, pre_denoise=pre_denoising_method, demosaic=demosaicing_method, post_denoise=post_denoising_method) for image in test_images_mosaiced]



# Collect metrics for each image (kinda part of demosaicing, too, for metrics like computational complexity) ========



# Make the results nice and export them to CSV, plots, etc. (easy to parse, so we can combine each method's results later)



# Easy said and done, right?