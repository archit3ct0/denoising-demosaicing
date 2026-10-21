import numpy as np

def split_into_color_channels(image, bayer_pattern = "RGGB"):
    # Split the mosaiced image into its color channels based on the Bayer pattern
    height, width = image.shape
    channels = np.zeros((height, width, 3), dtype=image.dtype)

    patterns = {
        "RGGB": ((0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 2)),
        "BGGR": ((0, 0, 2), (0, 1, 1), (1, 0, 1), (1, 1, 0)),
        "GBRG": ((0, 0, 1), (0, 1, 2), (1, 0, 0), (1, 1, 1)),
        "GRBG": ((0, 0, 1), (0, 1, 0), (1, 0, 2), (1, 1, 1)),
    }

    if bayer_pattern not in patterns:
        raise ValueError(f"Invalid Bayer pattern: {bayer_pattern}. Supported patterns are: {list(patterns.keys())}")

    for row_offset in range(2):
        for col_offset in range(2):
            channel = patterns[bayer_pattern][row_offset * 2 + col_offset][2]
            channels[row_offset::2, col_offset::2, channel] = image[row_offset::2, col_offset::2]

    return channels