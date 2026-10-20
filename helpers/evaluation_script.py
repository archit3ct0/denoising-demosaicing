# Evaluation script for demosaicing methods. Runs a set of reference images through a single demosaicing method.
# Generates fake Bayer filtered images from the references, demosaics them, and records performance metrics for later use.

# Configuration
test_image_directory = ""  # Directory containing test images
demosaicing_method = ""  # Demosaicing method to evaluate. Should be a function defined in helpers/demosaicing_methods.py
pre_denoising_method = "None"  # Optional denoising method to apply before demosaicing. If None, no denoising is applied.
post_denoising_method = "None"  # Optional denoising method to apply after demosaicing. If None, no denoising is applied.

# Import everything (libraries, helper functions)
from demosaicing_methods import *


# Import test images (per above, dynamic amount)

# Mosaic the test images

# Demosaic images with selected method

# Collect metrics for each image (kinda part of dmemosaicing, too, for metrics like computational complexity)

# Make the results nice and export them to CSV, plots, etc. (easy to parse, so we can combine each method's results later)

# Easy said and done, right?