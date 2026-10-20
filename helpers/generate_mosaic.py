import numpy as np

def generate_mosaic(input_images, bayer_pattern = "RGGB"):
    result_images = []  # Return helper

    # Build mosaic pattern on Bayer pattern input
    bayer_filter = np.zeros((2, 2, 3), dtype=np.uint8)

    patterns = {
        "RGGB": ((0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 2)),
        "BGGR": ((0, 0, 2), (0, 1, 1), (1, 0, 1), (1, 1, 0)),
        "GBRG": ((0, 0, 1), (0, 1, 2), (1, 0, 0), (1, 1, 1)),
        "GRBG": ((0, 0, 1), (0, 1, 0), (1, 0, 2), (1, 1, 1)),
    }

    if bayer_pattern not in patterns:
        raise ValueError(f"Invalid Bayer pattern: {bayer_pattern}. Supported patterns are: {list(patterns.keys())}")

    for row, col, channel in patterns[bayer_pattern]:
        bayer_filter[row, col, channel] = 1

    # Build bayer filter and apply to each image. Dynamic for input arrays containing mixed image sizes
    for image in input_images:
        height, width = image.shape[:2]

        # Tile bayer filter to cover image (cropping if necessary)
        bayer_selector = np.tile(bayer_filter, ((height + 1) // 2, (width + 1) // 2, 1))[:height, :width, :]
        
        # Keep one channel per pixel and flatten to grayscale
        image_out = np.sum(image * bayer_selector, axis=2, dtype=image.dtype)
        result_images.append(image_out)

    return result_images