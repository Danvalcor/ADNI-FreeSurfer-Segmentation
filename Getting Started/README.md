# FreeSurfer Segmentation Visualization Guide

## Table of Contents 
* [Getting Ready](#getting-ready)
  * [Required Extensions](#required-extensions)
  * [Needed Files](#needed-files)
  * [LUT and Stats Files](#lut-and-stats-files)
* [Segmentation](#segmentation)
  * [Accessing the Volume](#accessing-the-volume)
  * [Segmentation](#segmentation-steps)
    * [Color Mapping](#color-mapping)
    * [Individual Segmentations](#individual-segmentations)
* [3D Visualizing](#3d-visualizing)

## Description

This repository contains a Jupyter Notebook that walks you through the basics of visualizing segmentations obtained with FreeSurfer. To correctly visualize the segmentations, you must have the following libraries installed:

* `os`
* `random`
* `numpy`
* `pandas`
* `nibabel`
* `matplotlib` (with `pyplot` and `colors`)
* `nilearn` (with `plotting` and `image`)
* `vtk` (for 3D visualization)

## Getting Ready <a class="anchor" id="getting-ready"></a>

Before preparing to extract each segment by the color contained in the image, we must import the necessary extensions and prepare some files.

### Required Extensions <a class="anchor" id="required-extensions"></a>

```python
import os
import random
import numpy as np
import pandas as pd
import nibabel as nib
import matplotlib.pyplot as plt
from nilearn import plotting, image
from matplotlib.colors import ListedColormap
```

The volumes can be visualized in 2D using the existing library of nilearn. While in order to visualize specific segmentations, you must work with the images as an array of points containing specific indexes that correspond to a segment.

In order to view the volumes you can use a mesh with matplotlib. Or use better optimized libraries such as mayavi or vtk. In the example, we use vtk since it allows us to integrate it with tkinter.

### Needed files <a class="anchor" id="needed-files"></a>

To obten access to ADNI data collectios (MRI images), sign in is needed at https://adni.loni.usc.edu/data-samples/access-data/ 
scroll down until "apply for ADNI data" button appears, click on it and read the terms and conditions, agree on them and click submit. There will be 4 steps, enter your email, hit continue button, second put the security code sent to the email you just wrote, third, enter your information and follow instructions for step four, once you completed this steps wait for ADNI email for access.

