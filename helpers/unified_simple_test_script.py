# For running exclusively previously-implemented color reconstruction methods

# GENERIC IMPORTS ====================================================================================================
import numpy as np
import os
import csv
from datetime import datetime
from PIL import Image

# MOSAICING
from colour_demosaicing import (
    demosaicing_CFA_Bayer_bilinear,
    demosaicing_CFA_Bayer_Malvar2004,
    demosaicing_CFA_Bayer_Menon2007,
    mosaicing_CFA_Bayer,
)

# METRICS
# MSE
from skimage.metrics import mean_squared_error as mse

# CPSNR
from skimage.metrics import peak_signal_noise_ratio as psnr

# SSIM
from skimage.metrics import structural_similarity as ssim




# CONFIGURATION ======================================================================================================
test_image_directory = ""       # Directory containing test images
demosaicing_method = ""         # Demosaicing method to evaluate. Should be a function defined in helpers/demosaicing_methods.py
bayer_pattern = "RGGB"          # Bayer pattern to use for mosaicing. Should be one of the supported patterns in helpers/generate_mosaic.py
generate_csv = True             # Generate CSV data for evaluated metrics
data_range = 0                  # Color depth (in steps) of input images. 8-bit = 255, 16-bit = 65535, etc. Set to 0 for automatic based on storage type.




# IMPORT TEST IMAGES ==================================================================================================
test_image_filenames = sorted([filename for filename in os.listdir(test_image_directory) if filename.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"))])

if not test_image_filenames:
    raise ValueError(f"No test images found in directory: {test_image_directory}")

test_images_raw = [np.array(Image.open(os.path.join(test_image_directory, filename))) for filename in test_image_filenames]

if data_range == 0:
    first_image = test_images_raw[0]

    if np.issubdtype(first_image.dtype, np.integer):
        data_range = np.iinfo(first_image.dtype).max - np.iinfo(first_image.dtype).min
    else:
        data_range = 1.0 if first_image.min() >= 0 and first_image.max() <= 1 else first_image.max() - first_image.min()

print(f"Using data_range: {data_range}")




# MOSAIC THE TEST IMAGES =============================================================================================
test_images_mosaiced = [mosaicing_CFA_Bayer(image, bayer_pattern) for image in test_images_raw]




# DEMOSAIC USING SELECTED METHOD =====================================================================================
DEMOSAICING_METHODS = {
    "bilinear": demosaicing_CFA_Bayer_bilinear,
    "Malvar2004": demosaicing_CFA_Bayer_Malvar2004,
    "Menon2007": demosaicing_CFA_Bayer_Menon2007
}

def process_image(image, demosaic):
    if demosaic not in DEMOSAICING_METHODS:
        raise ValueError(f"Unknown demosaicing method: {demosaic}")

    return DEMOSAICING_METHODS[demosaic](image, bayer_pattern)

test_images_processed = [process_image(image, demosaic=demosaicing_method) for image in test_images_mosaiced]




# EVALUATE METRICS ===================================================================================================
# MSE - Each Color Channel
mse_values_red = np.array([mse(original[..., 0], processed[..., 0]) for original, processed in zip(test_images_raw, test_images_processed)])
mse_values_green = np.array([mse(original[..., 1], processed[..., 1]) for original, processed in zip(test_images_raw, test_images_processed)])
mse_values_blue = np.array([mse(original[..., 2], processed[..., 2]) for original, processed in zip(test_images_raw, test_images_processed)])

# MSE - Whole Image
mse_values = np.array([mse(original, processed) for original, processed in zip(test_images_raw, test_images_processed)])

# CPSNR - Whole Image
cpsnr_values = np.array([psnr(original, processed, data_range=data_range) for original, processed in zip(test_images_raw, test_images_processed)])

# SSIM - Whole Image
ssim_values = np.array([ssim(original, processed, channel_axis=-1, data_range=data_range) for original, processed in zip(test_images_raw, test_images_processed)])




# METRIC AGGREGATION ================================================================================================
metric_values = {
    "MSE Red": mse_values_red,
    "MSE Green": mse_values_green,
    "MSE Blue": mse_values_blue,
    "MSE Full": mse_values,
    "CPSNR": cpsnr_values,
    "SSIM": ssim_values
}

metric_summary = {metric: {"mean": np.mean(values), "std": np.std(values, ddof=1)} for metric, values in metric_values.items()}

# Print summary
print("\nMetric Summary:")
print("-" * 55)

for metric, values in metric_summary.items():
    print(
        f"{metric:<15} "
        f"Mean: {values['mean']:.6f} | "
        f"Std: {values['std']:.6f}"
    )

print("-" * 55)




# SAVE ===============================================================================================================
if generate_csv:

    # Generate output filename
    date = datetime.now().strftime("%Y-%m-%d")
    image_directory_name = os.path.basename(os.path.normpath(test_image_directory))

    csv_filename = (
        f"{image_directory_name}_"
        f"{demosaicing_method}_"
        f"{date}_"
        f"{bayer_pattern}.csv"
    )

    # Create output directory
    output_directory = os.path.join(test_image_directory, "results")
    os.makedirs(output_directory, exist_ok=True)

    csv_path = os.path.join(output_directory, csv_filename)

    # Write CSV
    with open(csv_path, mode="w", newline="", encoding="utf-8") as csv_file:

        writer = csv.writer(csv_file)

        # Metadata / title
        writer.writerow(["Image Directory", test_image_directory])
        writer.writerow(["Demosaicing Method", demosaicing_method])
        writer.writerow(["Bayer Pattern", bayer_pattern])
        writer.writerow(["Date", date])
        writer.writerow(["Data Range", data_range])

        writer.writerow([])

        # Individual image results
        headers = ["Image", "MSE Red", "MSE Green", "MSE Blue", "MSE Full", "CPSNR", "SSIM"]
        writer.writerow(headers)

        # Write one row per image
        for filename, red, green, blue, mse_full, cpsnr, ssim_value in zip(test_image_filenames, mse_values_red, mse_values_green, mse_values_blue, mse_values, cpsnr_values, ssim_values):
            writer.writerow([filename, red, green, blue, mse_full, cpsnr, ssim_value])

        # Metric summary
        writer.writerow([])
        writer.writerow(["Metric Summary"])
        writer.writerow(["Metric", "Mean", "Standard Deviation"])

        for metric, values in metric_summary.items():
            writer.writerow([
                metric,
                values["mean"],
                values["std"]
            ])

    print(f"CSV successfully saved to: {csv_path}")