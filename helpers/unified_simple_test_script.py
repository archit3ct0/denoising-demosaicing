# For running exclusively previously-implemented color reconstruction methods



# GENERIC IMPORTS ====================================================================================================

import numpy as np
import os
import csv
from datetime import datetime
from PIL import Image

import torch as th

# MOSAICING / DEMOSAICING
from colour_demosaicing import (
    demosaicing_CFA_Bayer_bilinear,
    demosaicing_CFA_Bayer_Malvar2004,
    demosaicing_CFA_Bayer_Menon2007,
    mosaicing_CFA_Bayer,
)

# METRICS
from skimage.metrics import mean_squared_error as mse
from skimage.metrics import peak_signal_noise_ratio as psnr
from skimage.metrics import structural_similarity as ssim



# CONFIGURATION ======================================================================================================

test_image_directory = r"C:\Users\Ethan\Documents\0_repositories\denoising-demosaicing\test data\kodak"
output_directory = r"C:\Users\Ethan\Documents\0_repositories\denoising-demosaicing\results"

image_id = "19"

# Processing mode:
# "demosaic", "denoise", or "demosaic+denoise"

processing_mode = "denoise"

uses_demosaicing = processing_mode in ("demosaic", "demosaic+denoise")
uses_denoising = processing_mode in ("denoise", "demosaic+denoise")

if processing_mode not in ("demosaic", "denoise", "demosaic+denoise"):
    raise ValueError(f"Unknown processing mode: {processing_mode}")

# Demosaicing
# "bilinear", "MHC-HQLI", "DDFAPD", "VNG", "EdgeAware", "DJDD-bayer"

demosaicing_method = "EdgeAware"
bayer_pattern = "GRBG"

generate_csv = True
data_range = 0

# Noise
noise_sigma = 25
noise_seed = 0

# Denoising
# "NLM", "AnisotropicDiffusion", "TV", "Wavelet",
# "Bregman", "Bilateral", "Gaussian", "Median", "BM3D",
# "FFDNet", "DRUNet", "SCUNet"

denoising_method = "BM3D"
denoiser_sigma = None

# SCUNet weights
scunet_weights = "download"

# Validate processing mode
if noise_sigma < 0:
    raise ValueError("noise_sigma cannot be negative.")

if denoiser_sigma is not None and denoiser_sigma < 0:
    raise ValueError("denoiser_sigma cannot be negative.")

if uses_demosaicing:
    if bayer_pattern not in ("RGGB", "BGGR", "GRBG", "GBRG"):
        raise ValueError(f"Invalid Bayer pattern: {bayer_pattern}")

    if demosaicing_method == "DJDD-bayer" and bayer_pattern != "GRBG":
        raise ValueError("DJDD-bayer currently uses a fixed GRBG Bayer mask.")



# IMPORT TEST IMAGES ==================================================================================================

valid_extensions = (".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif", ".webp")

if not os.path.isdir(test_image_directory):
    raise FileNotFoundError(f"Directory not found: {test_image_directory}")

test_image_filenames = sorted([
    filename
    for filename in os.listdir(test_image_directory)
    if filename.lower().endswith(valid_extensions)
])

if not test_image_filenames:
    raise ValueError(f"No test images found in directory: {test_image_directory}")

test_images_raw = [
    np.array(Image.open(os.path.join(test_image_directory, filename))
             .convert("RGB"))
    for filename in test_image_filenames
]

if data_range == 0:
    first_image = test_images_raw[0]

    if np.issubdtype(first_image.dtype, np.integer):
        data_range = np.iinfo(first_image.dtype).max - np.iinfo(first_image.dtype).min
    else:
        data_range = 1.0 if first_image.min() >= 0 and first_image.max() <= 1 else first_image.max() - first_image.min()

print(f"Using data_range: {data_range}")



# SELECT IMAGE FOR EXPORT ============================================================================================

image_id = os.path.splitext(image_id)[0].lower()

matching_images = [
    filename for filename in test_image_filenames
    if os.path.splitext(filename)[0].lower() == image_id
]

if not matching_images:
    matching_images = [
        filename for filename in test_image_filenames
        if os.path.splitext(filename)[0].lower().endswith(image_id)
    ]

if not matching_images:
    raise ValueError(f"Could not find image '{image_id}' in {test_image_directory}")

if len(matching_images) > 1:
    raise ValueError(f"Image identifier '{image_id}' is ambiguous. Matches: {matching_images}")

selected_image_filename = matching_images[0]
selected_image_index = test_image_filenames.index(selected_image_filename)
selected_image_raw = test_images_raw[selected_image_index]

print(f"Selected example image for export: {selected_image_filename}")



# GAUSSIAN NOISE ======================================================================================================

def add_gaussian_noise(image, sigma, rng):

    noisy = (
        np.asarray(image, dtype=np.float64)
        + rng.normal(0.0, sigma * data_range / 255.0, np.shape(image))
    )

    noisy = np.clip(noisy, 0, data_range)

    if np.issubdtype(test_images_raw[0].dtype, np.integer):
        noisy = np.rint(noisy)

    return noisy



# DENOISING METHODS ================================================================================================

def denoise_nlm(x, sigma):
    from skimage.restoration import denoise_nl_means
    return denoise_nl_means(x, patch_size=5, patch_distance=6, h=0.6 * sigma, sigma=sigma, fast_mode=True, channel_axis=-1)


def denoise_anisotropic_diffusion(x, sigma):
    from medpy.filter.smoothing import anisotropic_diffusion
    return np.stack([
        anisotropic_diffusion(x[..., c], niter=10, kappa=2.0 * sigma, gamma=0.1, option=1)
        for c in range(3)
    ], axis=-1)


def denoise_tv(x, sigma):
    from skimage.restoration import denoise_tv_chambolle
    return denoise_tv_chambolle(x, weight=0.75 * sigma, channel_axis=-1)


def denoise_wavelet_bayes(x, sigma):
    from skimage.restoration import denoise_wavelet
    return denoise_wavelet(x, sigma=sigma, wavelet="db4", mode="soft", method="BayesShrink", convert2ycbcr=True, rescale_sigma=True, channel_axis=-1)


def denoise_bregman(x, sigma):
    from skimage.restoration import denoise_tv_bregman
    return denoise_tv_bregman(x, weight=0.75 * sigma, channel_axis=-1)


def denoise_bilateral(x, sigma):
    from skimage.restoration import denoise_bilateral
    return denoise_bilateral(x, sigma_color=sigma, channel_axis=-1)


def denoise_gaussian(x, sigma):
    import cv2
    return cv2.GaussianBlur(x, (0, 0), sigmaX=sigma, sigmaY=sigma, borderType=cv2.BORDER_REFLECT)


def denoise_median(x, sigma):
    import cv2
    return cv2.medianBlur((x * 255).astype(np.uint8), ksize=3) / 255.0


def denoise_bm3d(x, sigma):
    import bm3d
    return bm3d.bm3d(x.astype(np.float64), sigma_psd=sigma)


# Pretrained networks through deepinv

network_cache = {}


def get_network(name):

    if name not in network_cache:

        import deepinv as dinv

        device = "cuda" if th.cuda.is_available() else "cpu"

        if name == "FFDNet":
            model = dinv.models.FFDNet(
                n_conv_layers=12, nf=96, img_channels=3,
                pretrained="download", device=device
            )

        elif name == "DRUNet":
            model = dinv.models.DRUNet(
                in_channels=3, out_channels=3,
                pretrained="download", device=device
            )

        elif name == "SCUNet":
            model = dinv.models.SCUNet(
                in_nc=3, pretrained=scunet_weights, device=device
            )

        else:
            raise ValueError(f"Unknown network: {name}")

        network_cache[name] = model.eval()

    return network_cache[name]


def denoise_network(x, sigma, name):

    model = get_network(name)
    device = next(model.parameters()).device

    height, width, _ = x.shape

    x = np.pad(
        x,
        ((0, height % 2), (0, width % 2), (0, 0)),
        mode="reflect"
    )

    tensor = th.from_numpy(
        np.ascontiguousarray(x.transpose(2, 0, 1))
    ).float().unsqueeze(0).to(device)

    with th.no_grad():
        output = model(tensor) if name == "SCUNet" else model(tensor, sigma)

    return output.squeeze(0).cpu().numpy().transpose(1, 2, 0)[:height, :width]


DENOISING_METHODS = {
    "NLM": denoise_nlm,
    "AnisotropicDiffusion": denoise_anisotropic_diffusion,
    "TV": denoise_tv,
    "Wavelet": denoise_wavelet_bayes,
    "Bregman": denoise_bregman,
    "Bilateral": denoise_bilateral,
    "Gaussian": denoise_gaussian,
    "Median": denoise_median,
    "BM3D": denoise_bm3d,
    "FFDNet": lambda x, sigma: denoise_network(x, sigma, "FFDNet"),
    "DRUNet": lambda x, sigma: denoise_network(x, sigma, "DRUNet"),
    "SCUNet": lambda x, sigma: denoise_network(x, sigma, "SCUNet"),
}


def denoise_image(image, method, sigma):

    x = np.clip(np.asarray(image, dtype=np.float64), 0, data_range) / data_range

    output = np.asarray(
        DENOISING_METHODS[method](x, sigma / 255.0),
        dtype=np.float64
    )

    return np.clip(output, 0, 1) * data_range


# Validate denoising settings

if uses_denoising:

    if denoising_method is None:
        raise ValueError("Set denoising_method when processing_mode includes denoising.")

    if denoising_method not in DENOISING_METHODS:
        raise ValueError(f"Unknown denoising method: {denoising_method}. Options: {list(DENOISING_METHODS)}")

    assumed_denoiser_sigma = noise_sigma if denoiser_sigma is None else denoiser_sigma

    if assumed_denoiser_sigma <= 0 and denoising_method != "SCUNet":
        raise ValueError(f"{denoising_method} needs a noise level above 0.")



# DEMOSAICING METHODS ================================================================================================

DEMOSAICING_METHODS = {
    "bilinear": demosaicing_CFA_Bayer_bilinear,
    "MHC-HQLI": demosaicing_CFA_Bayer_Malvar2004,
    "DDFAPD": demosaicing_CFA_Bayer_Menon2007,
}


OPENCV_BAYER_NAMES = {
    "RGGB": "BG",
    "BGGR": "RG",
    "GRBG": "GB",
    "GBRG": "GR",
}


def opencv_demosaic(image, pattern, algorithm):

    import cv2

    if pattern not in OPENCV_BAYER_NAMES:
        raise ValueError(f"Invalid Bayer pattern: {pattern}")

    if data_range == 255:
        cfa_dtype = np.uint8

    elif data_range == 65535 and algorithm != "VNG":
        cfa_dtype = np.uint16

    else:
        raise ValueError(
            f"OpenCV {algorithm} requires data_range 255"
            + ("" if algorithm == "VNG" else " or 65535")
            + f", got {data_range}."
        )

    cfa = np.clip(np.rint(image), 0, data_range).astype(cfa_dtype)

    code = getattr(
        cv2,
        f"COLOR_Bayer{OPENCV_BAYER_NAMES[pattern]}2RGB_{algorithm}"
    )

    return cv2.cvtColor(cfa, code).astype(np.float64)


DEMOSAICING_METHODS["VNG"] = lambda image, pattern: opencv_demosaic(image, pattern, "VNG")
DEMOSAICING_METHODS["EdgeAware"] = lambda image, pattern: opencv_demosaic(image, pattern, "EA")



# INITIALISE DJDD ================================================================================================

djdd_model = None

if uses_demosaicing and demosaicing_method == "DJDD-bayer":

    try:
        import demosaicnet
        djdd_model = demosaicnet.BayerDemosaick(pad=True)
        djdd_model.eval()

    except ImportError as error:
        raise ImportError(
            "DJDD model not available. Please install the external implementation."
        ) from error



# PROCESS IMAGE FUNCTION ============================================================================================

def process_image(image, demosaic, image_index=None):

    if demosaic in DEMOSAICING_METHODS:

        return DEMOSAICING_METHODS[demosaic](
            image, bayer_pattern
        )

    elif demosaic == "DJDD-bayer":

        original_image = test_images_raw[image_index]

        image = np.transpose(original_image, (2, 0, 1)).astype(np.float32)

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

        image = image * mask

        image = image / data_range

        image_tensor = th.from_numpy(image).unsqueeze(0)

        with th.no_grad():
            output = djdd_model(image_tensor)

        output = output.squeeze(0).cpu().numpy()
        output = np.transpose(output, (1, 2, 0))

        output = np.clip(output, 0, 1) * data_range

        return output

    else:
        raise ValueError(f"Unknown demosaicing method: {demosaic}")



# PROCESS IMAGES =====================================================================================================

if uses_demosaicing:

    test_images_mosaiced = [
        mosaicing_CFA_Bayer(image, bayer_pattern)
        for image in test_images_raw
    ]

    if noise_sigma > 0:

        if demosaicing_method == "DJDD-bayer":
            raise ValueError(
                "DJDD-bayer re-mosaics the original images, "
                "so noise cannot reach it."
            )

        noise_rng = np.random.default_rng(noise_seed)

        test_images_mosaiced = [
            add_gaussian_noise(image, noise_sigma, noise_rng)
            for image in test_images_mosaiced
        ]

    test_images_demosaiced = [
        process_image(image, demosaicing_method, index)
        for index, image in enumerate(test_images_mosaiced)
    ]

    test_images_processed = test_images_demosaiced.copy()

else:

    if noise_sigma > 0:

        noise_rng = np.random.default_rng(noise_seed)

        test_images_noisy = [
            add_gaussian_noise(image, noise_sigma, noise_rng)
            for image in test_images_raw
        ]

    else:

        test_images_noisy = [
            image.copy()
            for image in test_images_raw
        ]

    test_images_processed = test_images_noisy.copy()


# Apply denoising if selected

if uses_denoising:

    test_images_processed = [
        denoise_image(image, denoising_method, assumed_denoiser_sigma)
        for image in test_images_processed
    ]



# EVALUATE METRICS ===================================================================================================

# MSE - Each Color Channel

mse_values_red = np.array([
    mse(original[..., 0], processed[..., 0])
    for original, processed in zip(test_images_raw, test_images_processed)
])

mse_values_green = np.array([
    mse(original[..., 1], processed[..., 1])
    for original, processed in zip(test_images_raw, test_images_processed)
])

mse_values_blue = np.array([
    mse(original[..., 2], processed[..., 2])
    for original, processed in zip(test_images_raw, test_images_processed)
])


# MSE - Whole Image

mse_values = np.array([
    mse(original, processed)
    for original, processed in zip(test_images_raw, test_images_processed)
])


# CPSNR - Whole Image

cpsnr_values = np.array([
    psnr(original, processed, data_range=data_range)
    for original, processed in zip(test_images_raw, test_images_processed)
])


# SSIM - Whole Image

ssim_values = np.array([
    ssim(original, processed, channel_axis=-1, data_range=data_range)
    for original, processed in zip(test_images_raw, test_images_processed)
])



# METRIC AGGREGATION ================================================================================================

metric_values = {
    "MSE Red": mse_values_red,
    "MSE Green": mse_values_green,
    "MSE Blue": mse_values_blue,
    "MSE Full": mse_values,
    "CPSNR": cpsnr_values,
    "SSIM": ssim_values
}

metric_summary = {
    metric: {
        "mean": np.mean(values),
        "std": np.std(values, ddof=1 if len(values) > 1 else 0)
    }
    for metric, values in metric_values.items()
}

print("\nMetric Summary:")
print("-" * 55)

for metric, values in metric_summary.items():
    print(
        f"{metric:<15} "
        f"Mean: {values['mean']:.6f} | "
        f"Std: {values['std']:.6f}"
    )

print("-" * 55)



# OUTPUT DIRECTORY ================================================================================================

run_name = demosaicing_method if uses_demosaicing else "RGB"

if uses_denoising:
    run_name += f"+{denoising_method}"

if noise_sigma > 0:
    run_name += f"_noise{noise_sigma:g}"

method_output_directory = os.path.join(output_directory, run_name)

os.makedirs(method_output_directory, exist_ok=True)

print(f"\nMethod output directory: {method_output_directory}")



# EXPORT SELECTED IMAGE ============================================================================================

if uses_demosaicing:

    selected_image_mosaiced = test_images_mosaiced[selected_image_index]

    selected_image_demosaiced = test_images_demosaiced[selected_image_index]

else:

    selected_image_noisy = test_images_noisy[selected_image_index]


def prepare_image_for_saving(image, reference_dtype):

    image = np.asarray(image)

    if np.issubdtype(reference_dtype, np.integer):

        dtype_info = np.iinfo(reference_dtype)

        image = np.clip(
            np.rint(image),
            dtype_info.min,
            dtype_info.max
        ).astype(reference_dtype)

    else:

        image = image.astype(np.float32)

    return image


image_name = os.path.splitext(selected_image_filename)[0]

raw_image_path = os.path.join(
    method_output_directory,
    f"{image_name}_raw.tiff"
)

Image.fromarray(selected_image_raw).save(raw_image_path)


if uses_demosaicing:

    selected_image_mosaiced = prepare_image_for_saving(
        selected_image_mosaiced,
        selected_image_raw.dtype
    )

    selected_image_demosaiced = prepare_image_for_saving(
        selected_image_demosaiced,
        selected_image_raw.dtype
    )

    mosaiced_image_path = os.path.join(
        method_output_directory,
        f"{image_name}_mosaiced.tiff"
    )

    Image.fromarray(selected_image_mosaiced).save(mosaiced_image_path)

    if uses_denoising:

        demosaiced_image_path = os.path.join(
            method_output_directory,
            f"{image_name}_demosaiced.tiff"
        )

        Image.fromarray(selected_image_demosaiced).save(demosaiced_image_path)


else:

    selected_image_noisy = prepare_image_for_saving(
        selected_image_noisy,
        selected_image_raw.dtype
    )

    noisy_image_path = os.path.join(
        method_output_directory,
        f"{image_name}_noisy.tiff"
    )

    Image.fromarray(selected_image_noisy).save(noisy_image_path)


selected_image_processed = prepare_image_for_saving(
    test_images_processed[selected_image_index],
    selected_image_raw.dtype
)

output_suffix = "denoised" if uses_denoising else "demosaiced"

processed_image_path = os.path.join(
    method_output_directory,
    f"{image_name}_{output_suffix}.tiff"
)

Image.fromarray(selected_image_processed).save(processed_image_path)


print("\nSelected image successfully exported:")
print(f"Raw:        {raw_image_path}")

if uses_demosaicing:

    print(f"Mosaiced:   {mosaiced_image_path}")

    if uses_denoising:
        print(f"Demosaiced: {demosaiced_image_path}")

else:

    print(f"Noisy:      {noisy_image_path}")

print(f"Processed:  {processed_image_path}")



# SAVE CSV ==========================================================================================================

if generate_csv:

    date = datetime.now().strftime("%Y-%m-%d")

    image_directory_name = os.path.basename(
        os.path.normpath(test_image_directory)
    )

    csv_filename = f"{image_directory_name}_{run_name}_{date}"

    if uses_demosaicing:
        csv_filename += f"_{bayer_pattern}"

    csv_filename += ".csv"

    csv_path = os.path.join(
        method_output_directory,
        csv_filename
    )

    with open(csv_path, mode="w", newline="", encoding="utf-8") as csv_file:

        writer = csv.writer(csv_file)

        # Metadata
        writer.writerow(["Image Directory", test_image_directory])
        writer.writerow(["Processing Mode", processing_mode])

        writer.writerow([
            "Demosaicing Method",
            demosaicing_method if uses_demosaicing else None
        ])

        writer.writerow([
            "Bayer Pattern",
            bayer_pattern if uses_demosaicing else None
        ])

        writer.writerow(["Date", date])
        writer.writerow(["Data Range", data_range])
        writer.writerow(["Exported Image", selected_image_filename])

        # Noise and denoising metadata
        if noise_sigma > 0 or uses_denoising:

            writer.writerow(["Noise Sigma (0-255 scale)", noise_sigma])
            writer.writerow(["Noise Seed", noise_seed])

            writer.writerow([
                "Denoising Method",
                denoising_method if uses_denoising else None
            ])

            if uses_denoising:
                writer.writerow([
                    "Denoiser Sigma (0-255 scale)",
                    assumed_denoiser_sigma
                ])

        # OpenCV version
        if uses_demosaicing and demosaicing_method in ("VNG", "EdgeAware"):

            import cv2

            writer.writerow(["OpenCV Version", cv2.__version__])

        writer.writerow([])

        # Individual image results
        headers = [
            "Image",
            "MSE Red",
            "MSE Green",
            "MSE Blue",
            "MSE Full",
            "CPSNR",
            "SSIM"
        ]

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

            writer.writerow([
                filename,
                red,
                green,
                blue,
                mse_full,
                cpsnr,
                ssim_value
            ])

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

    print(f"\nCSV successfully saved to: {csv_path}")


print("\nProcessing complete.")