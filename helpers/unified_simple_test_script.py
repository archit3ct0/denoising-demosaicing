# For running exclusively previously-implemented color reconstruction methods

# GENERIC IMPORTS ====================================================================================================
from email.mime import image

import numpy as np
import os
import csv
from datetime import datetime
from PIL import Image

import torch as th

# MOSAICING (pip install -U colour-demosaicing)
from colour_demosaicing import (
    demosaicing_CFA_Bayer_bilinear,
    demosaicing_CFA_Bayer_Malvar2004, 
    demosaicing_CFA_Bayer_Menon2007, 
    mosaicing_CFA_Bayer,
)
import demosaicnet # installed externally, DJDD. Can comment out this and DJDD section in/before process_image if you don't need it.

# METRICS (pip install -U scikit-image)
from skimage.metrics import mean_squared_error as mse
from skimage.metrics import peak_signal_noise_ratio as psnr
from skimage.metrics import structural_similarity as ssim




# CONFIGURATION ======================================================================================================
test_image_directory = r"C:\Users\Ethan\Documents\0_repositories\denoising-demosaicing\test data\kodak"       # Directory containing test images
output_directory = (r"C:\Users\Ethan\Documents\0_repositories\denoising-demosaicing\results")
image_id = "19"  # Export a particular example image from the input directory
demosaicing_method = "DJDD-bayer"         # Demosaicing method to evaluate
bayer_pattern = "GRBG"          # Bayer pattern to use for mosaicing
generate_csv = True             # Generate CSV data for evaluated metrics
data_range = 0                  # Color depth (in steps) of input images. 8-bit = 255, 16-bit = 65535, etc. Set to 0 for automatic based on storage type.




# IMPORT TEST IMAGES ==================================================================================================
valid_extensions = (".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif", ".webp")
test_image_filenames = sorted([filename for filename in os.listdir(test_image_directory) if filename.lower().endswith(valid_extensions)])

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



# SELECT IMAGE FOR EXPORT ================================================================================
image_id = os.path.splitext(image_id)[0].lower()  # Remove extension if one was supplied

matching_images = [filename for filename in test_image_filenames if os.path.splitext(filename)[0].lower() == image_id]
if not matching_images:
    matching_images = [filename for filename in test_image_filenames if os.path.splitext(filename)[0].lower().endswith(image_id)]
if not matching_images:
    raise ValueError(f"Could not find image '{image_id}' in {test_image_directory}")

if len(matching_images) > 1:
    raise ValueError(f"Image identifier '{image_id}' is ambiguous. " f"Matches: {matching_images}")

selected_image_filename = matching_images[0]
selected_image_index = test_image_filenames.index(
    selected_image_filename
)

selected_image_raw = test_images_raw[selected_image_index]

print(f"Selected example image for export: {selected_image_filename}")



# MOSAIC THE TEST IMAGES =============================================================================================
test_images_mosaiced = [mosaicing_CFA_Bayer(image, bayer_pattern) for image in test_images_raw]




# DEMOSAIC USING SELECTED METHOD =====================================================================================
if demosaicing_method == "DJDD-bayer":
    try:
        djdd_model = demosaicnet.BayerDemosaick(pad=True)
        djdd_model.eval()
    except ImportError:
        print("DJDD model not available. Please install the external implementation.")
        djdd_model = None

else:
    djdd_model = None

DEMOSAICING_METHODS = {
    "bilinear": demosaicing_CFA_Bayer_bilinear,       # Bilinear     -
    "MHC-HQLI": demosaicing_CFA_Bayer_Malvar2004,     # HQLI         -
    "DDFAPD": demosaicing_CFA_Bayer_Menon2007,        # DDFAPD       -
}

def process_image(image, demosaic):

    # Traditional Bayer methods
    if demosaic in DEMOSAICING_METHODS:

        return DEMOSAICING_METHODS[demosaic](
            image, bayer_pattern
        )

    # DJDD Bayer
    elif demosaic == "DJDD-bayer":

        # Retrieve original RGB image using the corresponding
        # image index (the input argument is otherwise ignored).
        image_index = process_image.counter
        original_image = test_images_raw[image_index]
        process_image.counter += 1

        # HWC -> CHW
        image = np.transpose(original_image, (2, 0, 1)).astype(np.float32)

        # Create three-channel Bayer mask (GRBG)
        mask = np.ones_like(image)

        # Red
        mask[0, ::2, ::2] = 0
        mask[0, 1::2, :] = 0

        # Green
        mask[1, ::2, 1::2] = 0
        mask[1, 1::2, ::2] = 0

        # Blue
        mask[2, ::2, :] = 0
        mask[2, 1::2, 1::2] = 0

        # Apply Bayer mask
        image = image * mask

        # Normalize to [0, 1]
        image = image / data_range

        # CHW -> BCHW
        image_tensor = th.from_numpy(image).unsqueeze(0)

        # Run neural network
        with th.no_grad():
            output = djdd_model(image_tensor)

        # BCHW -> HWC
        output = output.squeeze(0).cpu().numpy()
        output = np.transpose(output, (1, 2, 0))

        # Restore original intensity range
        output = np.clip(output, 0, 1) * data_range

        return output

    else:
        raise ValueError(f"Unknown demosaicing method: {demosaic}")

# Initialise DJDD image counter
process_image.counter = 0


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




# OUTPUT DIRECTORY ========================================================================================

# Create a separate folder for the selected demosaicing method
method_output_directory = os.path.join(output_directory, demosaicing_method)
os.makedirs(method_output_directory, exist_ok=True)
print(f"\nMethod output directory: {method_output_directory}")




# EXPORT SELECTED IMAGE ==================================================================================

# Retrieve the corresponding mosaiced and demosaiced images
selected_image_mosaiced = test_images_mosaiced[selected_image_index]
selected_image_demosaiced = test_images_processed[selected_image_index]


def prepare_image_for_saving(image, reference_dtype):
    image = np.asarray(image)

    if np.issubdtype(reference_dtype, np.integer):
        dtype_info = np.iinfo(reference_dtype)
        image = np.clip(np.rint(image), dtype_info.min, dtype_info.max).astype(reference_dtype)

    else:
        image = image.astype(np.float32)

    return image


# Match the original image's numeric representation
selected_image_mosaiced = prepare_image_for_saving(selected_image_mosaiced, selected_image_raw.dtype)

selected_image_demosaiced = prepare_image_for_saving(selected_image_demosaiced, selected_image_raw.dtype)

# Save all three versions as TIFF files
# TIFF avoids introducing JPEG compression artifacts.
image_name = os.path.splitext(selected_image_filename)[0]

raw_image_path = os.path.join(method_output_directory, f"{image_name}_raw.tiff")
mosaiced_image_path = os.path.join(method_output_directory, f"{image_name}_mosaiced.tiff")
demosaiced_image_path = os.path.join(method_output_directory, f"{image_name}_demosaiced.tiff")

Image.fromarray(selected_image_raw).save(raw_image_path)
Image.fromarray(selected_image_mosaiced).save(mosaiced_image_path)
Image.fromarray(selected_image_demosaiced).save(demosaiced_image_path)

print("\nSelected image successfully exported:")
print(f"Raw:        {raw_image_path}")
print(f"Mosaiced:   {mosaiced_image_path}")
print(f"Demosaiced: {demosaiced_image_path}")




# SAVE CSV ================================================================================================

if generate_csv:

    date = datetime.now().strftime("%Y-%m-%d")
    image_directory_name = os.path.basename(os.path.normpath(test_image_directory))

    csv_filename = (f"{image_directory_name}_" f"{demosaicing_method}_" f"{date}_" f"{bayer_pattern}.csv")

    csv_path = os.path.join(method_output_directory, csv_filename)

    with open(csv_path, mode="w", newline="", encoding="utf-8") as csv_file:

        writer = csv.writer(csv_file)

        # Metadata
        writer.writerow(["Image Directory", test_image_directory])
        writer.writerow(["Demosaicing Method", demosaicing_method])
        writer.writerow(["Bayer Pattern", bayer_pattern])
        writer.writerow(["Date", date])
        writer.writerow(["Data Range", data_range])
        writer.writerow(["Exported Image", selected_image_filename])

        writer.writerow([])

        # Individual image results
        headers = ["Image", "MSE Red", "MSE Green", "MSE Blue", "MSE Full", "CPSNR", "SSIM"]

        writer.writerow(headers)

        for filename, red, green, blue, mse_full, cpsnr, ssim_value in zip(
            test_image_filenames,
            mse_values_red,
            mse_values_green,
            mse_values_blue,
            mse_values,
            cpsnr_values,
            ssim_values
        ):

            writer.writerow([filename, red, green, blue, mse_full, cpsnr, ssim_value])

        # Metric summary
        writer.writerow([])
        writer.writerow(["Metric Summary"])
        writer.writerow(["Metric", "Mean", "Standard Deviation"])

        for metric, values in metric_summary.items():

            writer.writerow([metric, values["mean"], values["std"]])

    print(f"\nCSV successfully saved to: {csv_path}")


print("\nProcessing complete.")