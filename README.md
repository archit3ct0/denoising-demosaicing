# Denoising & Demosaicing
Python framework for the quantitative comparison of denoising and demosaicing methods for raw camera images.

***

## Motivation
Most scientific cameras do not demosaic their images onboard, requiring processing before they can be used for further investigation. While this adds an extra step between collecting images and actually using them, it also opens a door to increased processing flexibility. We can now run denoising, demosaicing, and any other image processing steps in whichever order and to whatever degree or method we want.

With that freedom, a few decisions need to be made. First and foremost is which denoising and demosaicing processing methods we want to apply to the images, if any, and the extent to which they are used. With many different, established approaches to [color reconstruction and noise removal](docs/denoising-and-demosaicing-methods.md), how do we determine which to use in a given situation? Many of them claim to be better than each other, and many offer largely qualitative comparisons to other techniques. We need some quantitative means to compare and contrast these approaches, to enable better understanding of the tradeoffs involved in and inherent to each method. This project endeavors to do just that.

<br>

## Structure
In addition to assessing different color reconstruction (demosaicing) and noise removal (denoising) approaches, there is also a standing objective to make the tooling built here reusable in actual scientific pipelines and workflows. That means building our implementations of each method in modular units that can be called by other scripts, whether our test coordinator or otherwise. This drives the structure of this repo's code, with a central test script, method modules, and test data chunked logically and intentionally to enable easy reuse.

The test coordinator evaluates our [test metrics](docs/evaluation-metrics.md) for each method function it calls, using an interchangeable set of test images. While applied to common, pseudo-standard [reference images](docs/test-datasets.md) here, it can just as easily be run on other images, to better assess the applicability of these methods to specific use cases.

<br>

## Method Modules


<br>

## Results


<br>

## Usage