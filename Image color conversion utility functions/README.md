# Color Conversion and Image Analysis

This repository contains various functions for converting between different color spaces and performing image analysis, specifically aimed at skin color analysis. The code is optimized using Numba's `njit` for faster execution.

## Features

- **Color Space Conversion**: Converts images between XYZ, sRGB, AdobeRGB, CIELAB, and other color spaces.
- **Chromophore Detection**: Estimates melanin and hemoglobin levels in skin images.
- **Whiteness Indices**: Computes WIO and WIC whiteness indices for dental research.
- **Correlated Color Temperature (CCT)**: Calculates the correlated color temperature from XYZ color values.
- **Optimized Performance**: Utilizes Numba’s `njit` decorator for speedups in pixel-wise operations.

## Installation

To install the required dependencies, you can use `pip`:

```bash
pip install numpy numba
```

## Usage
Color Conversions

The ColorConversions class provides several methods for converting between different color spaces.

Example:

# Estimate melanin content in the skin image
melanin_image = ColorConversions.xyz_to_melanin(xyz_image)

# Estimate hemoglobin content
hemoglobin_image = ColorConversions.xyz_to_hemoglobine(xyz_image)

# Compute WIO for tooth color
wio_image = ColorConversions.xyz_to_wio(xyz_image)

# Compute WIC for tooth color
wic_image = ColorConversions.xyz_to_wic(xyz_image)


## Correlated Color Temperature (CCT)
The method xyz_to_cct calculates the correlated color temperature (CCT) based on XYZ values.


# Example XYZ value for a pixel
X, Y, Z = 0.3, 0.4, 0.2

# Calculate CCT
cct_value = ColorConversions.xyz_to_cct(X, Y, Z)

## Notes

    The functions assume that the input image data is in the correct format (e.g., a numpy array with shape (height, width, 3) for color images).
    The code uses Numba for JIT compilation to improve performance during color conversion and image analysis operations.
    Ensure that you use valid XYZ values for accurate results.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
Acknowledgements

    Numba for JIT compilation to optimize performance.
    Numpy for efficient array manipulation.

