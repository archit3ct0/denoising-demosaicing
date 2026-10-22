---
title: Denoising and Demosaicing Methods
tags: [docs]
---

# Denoising and Demosaicing Methods
> [!IMPORTANT]
> This list represents an in-no-way-comprehensive collection of denoising and demosaicing methods. They are an assortment of industry-standard methodologies, specific implementations and approaches, and general categories. Standard approaches like Bilinear and AHD will have specific implementations noted, while methods derived from papers use the authors' implementations and naming schemes.

This list is split into demosaicing-only methods, which only de-Bayer raw images, denoising-only methods, which only remove noise from the raw (or de-Bayered image), joint methods which accomplish both at the same time, and multi-stage methods, which operate as a bundle but perform denoising and demosaicing as separate steps.

***

### Demosaicing Only Methods:

#### Bilinear
##### Overview
| ![alt text](images/demosaicing_bilinear.png) |
|:--:|
| *Bilinear interpolation process* [*(Crafting Pixels)*](https://pixelcraft.photo.blog/tag/bilinear-demosaicing/) |

Estimates missing color values by averaging nearby samples of desired color. Serves as the foundation on which other methods improve on.

1. Identify Bayer pattern
2. Preserve measured value
3. Estimate missing values
4. Assign RGB values
5. Repeat for each pixel

##### Notes

**Computational Cost:** Low
**Edge Awareness:** Low
**Detail Preservation:** Low
**Implementation Complexity:** Low

<br>

#### Improved Linear Demosaicing
##### Overview
| ![Filter coefficients for improved linear demosaicing (Microsoft Research)](images\demosaicing_improved_linear.png) |
|:--:| 
| *Filter coefficients for improved linear demosaicing* [*(Microsoft Research)*](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/Demosaicing_ICASSP04.pdf) |

(HQLI) Improves bilinear demosaicing by adding corrections to estimated color value. Corrections are gradient-based with fixed correction coefficients.

1. Identify Bayer pattern
2. Preserve measured value
3. Calculate initial estimates (bilinear)
4. Calculate gradient correction (based on nearby samples of measured color values)
5. Add correction to initial estimates (coefficient depends on location and color of estimation, different approaches here)
6. Assign RGB values
7. Repeat for each pixel

##### Notes
- [Paper](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/Demosaicing_ICASSP04.pdf) (HQLI)

**Computational Cost:** Low
**Edge Awareness:** Low
**Detail Preservation:** Moderate
**Implementation Complexity:** Moderate

<br>

#### Adaptive Homogeneity-Directed Demosaicing (AHD)
##### Overview

Compares horizontal and vertical using homogeneity.

1. Identify Bayer pattern
2. Interpolate green in vertical and horizontal directions
3. Estimate missing red and blue values for each direction using difference between known and interpolated values
4. Create vertical and horizontal images
5. Convert images into CIELab to separate lightness from color components
6. Calculate local homogeneity (quantify local similarities, then tally them up between the two images)
7. Give priority to greater homogeneity and reconstruct image
8. Apply artifact reduction

##### Notes
- [Whitepaper](https://ieeexplore.ieee.org/document/1395991)

**Computational Cost:** High
**Edge Awareness:** High
**Detail Preservation:** High
**Implementation Complexity:** High

<br>

#### Variable Number of Gradient (VNG)
##### Overview

Selects a variable set of directions using gradient thresholds.

1. Identify Bayer pattern
2. Estimate green value
3. Calculate directional gradients
4. Determine threshold of suitability (using local gradients)
5. Estimate missing values
6. Repeat for each pixel
7. Assign RGB values

##### Notes

-[paper](https://ui.adsabs.harvard.edu/abs/1999SPIE.3650...36C/abstract)

**Computational Cost:** Moderate
**Edge Awareness:** High
**Detail Preservation:** High
**Implementation Complexity:** Moderate

<br>

#### Patterned Pixel Grouping (PPG)
##### Overview

Interpolates green using directional edge measures, then reconstructs red and blue values from color differences.

1. Identify Bayer pattern
2. Calculate edge measures for red and blue pixels with missing green
3. Estimate green value using direction of smallest edge measure
4. Repeat for each pixel
5. Use green image to estimate missing red and blue values
6. Hue-transit interpolation
7. Assign RGB values

##### Notes

-[Paper](https://sources.debian.org/src/dcraw/9.28-2/dcraw.c/) (source code)

**Computational Cost:** Low
**Edge Awareness:** Moderate
**Detail Preservation:** High
**Implementation Complexity:** Moderate

<br>

#### High Quality Linear Interpolation (HQLI)
##### Overview

Improves bilinear demosaicing by adding corrections to estimated color value. Corrections are gradient-based with fixed correction coefficients.

1. Identify Bayer pattern
2. Preserve measured value
3. Calculate initial estimates (bilinear)
4. Calculate gradient correction (based on nearby samples of measured color values)
5. Add correction to initial estimates (coefficient depends on location and color of estimation, different approaches here)
6. Assign RGB values
7. Repeat for each pixel

##### Notes

- [Paper](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/Demosaicing_ICASSP04.pdf)

**Computational Cost:** Low
**Edge Awareness:** Low
**Detail Preservation:** Moderate
**Implementation Complexity:** Moderate

<br>

#### Directional Filtering and a Posteriori Decision (DFPD)
##### Overview

Applies directional filters, then makes posteriori decision between estimates

1. Identify Bayer pattern
2. Calculate directional gradients
3. Determine which directional estimates are more consistent with surrounding samples
4. Make a posteriori decision
5. Repeat process as needed to estimate missing red, green, and blue values
6. Assign RGB values

##### Notes

-[paper](https://pubmed.ncbi.nlm.nih.gov/17283772/)

**Computational Cost:** Moderate
**Edge Awareness:** High
**Detail Preservation:** High
**Implementation Complexity:** High

<br>

#### Multiple Gradients (MG)
##### Overview

Combines directional estimates using consistency between multiple gradients.

1. Identify Bayer pattern
2. Calculate directional gradients to estimate missing green values
3. Calculate color differences
4. Evaluate gradients in multiple directions and scales
5. Combine directional estimates based on consistency
6. Reconstruct red and blue based on estimated green value and interpolated color differences
7. Assign RGB values

##### Notes
- [Paper](https://pubmed.ncbi.nlm.nih.gov/22868571/)

**Computational Cost:** Moderate
**Edge Awareness:** High
**Detail Preservation:** High
**Implementation Complexity:** Moderate

***

### Denoising Only Methods:

#### Non-Local Means & Patch-Based Difference (NLM/PBD)
##### Overview
##### Notes
- [Paper](https://www.researchgate.net/publication/317244370_Denoising_Algorithm_for_CFA_Image_Sensors_Considering_Inter-Channel_Correlation)

<br>

#### DTDeMo
##### Overview
##### Notes
- [Paper](https://www.researchgate.net/publication/382151929_DTDeMo_A_Deep_Learning-based_Two-stage_Image_Demosaicing_Model_with_Interpolation_and_Enhancement)

***

### Joint Methods:

#### Generative Adversarial Network (GAN)
##### Overview
##### Notes
- [Paper](https://www.sciencedirect.com/science/article/abs/pii/S0925231221001181)

<br>

#### Joint Demosaicing and Denoising Light (JDD-LI)
##### Overview
##### Notes
- [Paper](https://www.sciencedirect.com/science/article/pii/S1047320326002191?utm_source=chatgpt.com)

<br>

#### Mutual Guidance of COlor Channels (MGCC)
##### Overview
##### Notes
- [Paper](https://www.sciencedirect.com/science/article/abs/pii/S0165168422002134)

<br>

#### Unified Multi-bayer Demosaicing (UMBD)
##### Overview
##### Notes
- [Paper](https://arxiv.org/html/2504.07145v2)

***

### Multi-Stage Methods:

#### Demosaic-First CNN (DF-CNN)
##### Overview
##### Notes
- [Implementation/Paper](https://www.sciencedirect.com/science/article/abs/pii/S0377042723002741)
