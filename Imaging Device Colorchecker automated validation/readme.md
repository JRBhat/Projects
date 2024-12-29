# Color Chart Validator

## Overview

This project involves the validation of color accuracy using a Visia color chart. The goal is to extract color patches from images, convert them to LAB color space, and compare them against predefined standard values. The deltas between extracted and standard LAB values are calculated to assess color accuracy.

## Workflow

1. **Image Input**: A set of images containing the Visia color chart is loaded.
2. **ROI Extraction**: Regions of interest (ROIs) corresponding to specific color patches on the chart are defined using pixel coordinates.
3. **LAB Conversion**: The ROI from each image is extracted, and its color values are converted to LAB color space.
4. **Comparison**: The extracted LAB values are compared to predefined standard LAB values for each color patch.
5. **Delta Calculation**: The delta (difference) between the extracted LAB values and the standard values is calculated.
6. **Plotting**: The results are visualized through a plot comparing L* values across different images and colors.

## Requirements

- OpenCV
- NumPy
- Matplotlib

You can install the required dependencies via:

```bash
pip install opencv-python numpy matplotlib
