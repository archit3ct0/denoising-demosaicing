---
title: Denoising and Demosaicing Methods
tags: [docs]
---

# Function Definitions
Toolkit functions and helpers.

***

## Helper Functions

### generate_mosaic(*image, bayer_pattern='RGGB'*)
Generate mosaiced image from an input image (as though it was captured through a Bayer filter). Filter parameters are configurable. Accepts an array of images.

**Parameters:**

&emsp;&emsp; **image : *NumPy array [n, m, 3]***

&emsp;&emsp;&emsp;&emsp; Input image (three channel, RGB). Accepts array of images.

&emsp;&emsp; **bayer_pattern : *string***

&emsp;&emsp;&emsp;&emsp; Bayer pattern ordering. Accepts: **'RGGB'**, **'BGGR'**, **'RGBG'**, **'GRBG'**

**Returns:**

&emsp;&emsp; **result : *NumPy array [n, m]***

&emsp;&emsp;&emsp;&emsp; Mosaiced grayscale image (single channel). Can produce array of images.

<br>

### split_into_color_channels(*image, bayer_pattern='RGGB'*)
Split a grayscale (single-channel) mosaiced image into its constituent color channels, as per the Bayer pattern used to mosaic it in the first place (either in-camera or by the mosaic-generation script).

**Parameters:**

&emsp;&emsp; **image : *NumPy array [n, m]***

&emsp;&emsp;&emsp;&emsp; Raw grayscale mosaiced image (single channel)

&emsp;&emsp; **bayer_pattern : *string***

&emsp;&emsp;&emsp;&emsp; Bayer pattern ordering. Accepts: **'RGGB'**, **'BGGR'**, **'GBRG'**, **'GRBG'**

**Returns:**

&emsp;&emsp; **channels : *NumPy array [n, m, 3]***

&emsp;&emsp;&emsp;&emsp; NumPy array of image, split into separate RGB channels as per Bayer pattern applied (passed as argument)

***

## Method Modules

### bilinear(*image, bayer_pattern='RGGB'*)
Implements bilinear (nearest-neighbor) interpolative demosaicing. Very simple and computationally light, but prone to artifacts and blurring (not edge-aware).

**Parameters:**

&emsp;&emsp; **image : *NumPy array [n, m]***

&emsp;&emsp;&emsp;&emsp; Input image to demosaic (single channel)

&emsp;&emsp; **bayer_pattern : *string***

&emsp;&emsp;&emsp;&emsp; Bayer pattern ordering. Accepts: **'RGGB'**, **'BGGR'**, **'GBRG'**, **'GRBG'**

**Returns:**

&emsp;&emsp; **result : *NumPy array [n, m, 3]***

&emsp;&emsp;&emsp;&emsp; Reconstructed output image (three channel, RGB)

<br>

### improved_linear(*image, bayer_pattern='RGGB'*)
Implements improved linear interpolative demosaicing (Microsoft Research). Simple and computationally light, and exhibits much less artifacting than bilinear and even some nonlinear methods.

**Parameters:**

&emsp;&emsp; **image : *NumPy array [n, m]***

&emsp;&emsp;&emsp;&emsp; Input image to demosaic (single channel)

&emsp;&emsp; **bayer_pattern : *string***

&emsp;&emsp;&emsp;&emsp; Bayer pattern ordering. Accepts: **'RGGB'**, **'BGGR'**, **'RGBG'**, **'GRBG'**

**Returns:**

&emsp;&emsp; **result : *NumPy array [n, m, 3]***

&emsp;&emsp;&emsp;&emsp; Reconstructed output image (three channel, RGB)

<br>

***

## Documentation & Templates

> [!NOTE]
> Templates to copy for creating documentation:

### documentation_template(*parameters='defaults'*)
Function Description

**Parameters:**

&emsp;&emsp; **parameter : *type***

&emsp;&emsp;&emsp;&emsp; Parameter Description

**Returns:**

&emsp;&emsp; **return : *type***

&emsp;&emsp;&emsp;&emsp; Return Description

**Notes:**

Additional notes for function

***