---
title: Denoising and Demosaicing Methods
tags: [docs]
---

# Evaluation Metrics
> [!WARNING]
> This is all mostly noodling around right now.

<br>

#### NIQE
Papers mention the “NIQE performance metric and the correlation coefficient”
- https://thesai.org/Downloads/Volume14No10/Paper_3-Comparison_of_Four_Demosaicing_Methods.pdf

The NIQE:
- https://quality.nfdi4ing.de/en/latest/image_quality/NIQE.html.
- Scores with 0 being best.

<br>

#### What do WE as a group care about?
Not sure. Possibly:
- Computation cost
- Denoising capacity
  - What types of noise?
    - Photon shot noise
    - Sensor read noise
- Accuracy -> how do we quantify this?
- Do these metrics (any/all) depend on sensor resolution or pixel size/density?
- Deviation from “lazy” use of quarter-resolution mosaic result -> does this make actually-sampled color information worse?
- What is scale of noise and error introduced relative to data? SNR? Artificial Error-to-noise ratio?
- Depending on how fast the images are taken relative to the sample noise, drizzling may help improve resolution without “guessing” with demosaicing.
- Are we measuring spatial or temporal noise of the sample? Denoising and combined steps (JDD) are going to flatten spatial noise, whether sample or sensor, without discerning between them.
- Are learning methods deterministic? Does it matter?