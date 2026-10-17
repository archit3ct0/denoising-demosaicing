---
title: Denoising and Demosaicing Methods
tags: [docs]
---

# Function Definitions
Toolkit functions and helpers.

***

## Helper Functions

#### generate_mosaic(*image, bayer_pattern='RGGB'*)
Generate mosaiced image from an input image (as though it was captured through a Bayer filter). Filter parameters are configurable.

**Parameters:**

&emsp;&emsp; **image : *NumPy array***

&emsp;&emsp;&emsp;&emsp; Input image (three channel, RGB)

&emsp;&emsp; **bayer_pattern : *string***

&emsp;&emsp;&emsp;&emsp; Bayer pattern ordering. Accepts: **'RGGB'**, **'BGGR'**, **'RGBG'**, **'GRBG'**

**Returns:**

&emsp;&emsp; **result : *NumPy array***

&emsp;&emsp;&emsp;&emsp; Mosaiced grayscale image (single channel)


***

## Method Modules

#### bilinear(*image*)
Implements bilinear (nearest-neighbor) interpolative demosaicing. Very simple and computationally light, but prone to artifacts and blurring (not edge-aware).

**Parameters:**

&emsp;&emsp; **image : *NumPy array***

&emsp;&emsp;&emsp;&emsp; Input image to demosaic (single channel)

**Returns:**

&emsp;&emsp; **result : *NumPy array***

&emsp;&emsp;&emsp;&emsp; Reconstructed output image (three channel, RGB)

<br>

#### improved_linear(*image*)
Implements improved linear interpolative demosaicing (Microsoft Research). Simple and computationally light, and exhibits much less artifacting than bilinear and even some nonlinear methods.

**Parameters:**

&emsp;&emsp; **image : *NumPy array***

&emsp;&emsp;&emsp;&emsp; Input image to demosaic (single channel)

**Returns:**

&emsp;&emsp; **result : *NumPy array***

&emsp;&emsp;&emsp;&emsp; Reconstructed output image (three channel, RGB)

<br>

***

## Documentation & Templates

> [!INFO]
> Templates to copy for creating documentation:

#### documentation_template(*parameters='defaults'*)
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