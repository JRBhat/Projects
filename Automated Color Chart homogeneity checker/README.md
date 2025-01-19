# ROI Masking and Image Annotation Workflow (Condensed)

## Overview
This project processes images to:
- Extract luminance values from specified regions of interest (ROI).
- Annotate images with luminance data.
- Save annotated images and plot luminance trends.

---

## Workflow
1. **Setup**: Define paths, ROI coordinates, and luminance thresholds.
2. **Process Images**:
   - Create binary ROI masks.
   - Extract LAB color space data.
   - Calculate median luminance (L) values.
   - Annotate and save processed images (optional).
3. **Visualize**: Plot luminance trends for analysis.

---

## Functions

### `create_roi_mask`
- Creates a binary mask for a given ROI.
- **Input**: Image, ROI coordinates (x, y, w, h).
- **Output**: Binary mask.

### `draw_rect`
- Draws a rectangle on the ROI based on luminance thresholds.
- **Input**: Image, ROI coordinates, luminance value, thresholds.
- **Output**: Image with a colored rectangle.

### `save_masked_img`
- Saves annotated images with transparency and masks.
- **Input**: Image, mask, ROI coordinates, luminance, thresholds.

### `annotate_img`
- Adds text annotations for luminance values.
- **Input**: Image, luminance value, thresholds.

### `main`
- Coordinates the entire workflow: ROI masking, luminance extraction, annotation, and plotting.

---

## Algorithm
1. **Mask Creation**: Define binary masks for ROIs.
2. **Luminance Extraction**: Convert to LAB space, extract L channel, compute median.
3. **Annotation**: Draw rectangles and add luminance text.
4. **Save and Plot**: Save annotated images and plot luminance trends.

---

## How to Run
1. Install dependencies: `opencv-python`, `numpy`, `matplotlib`.
2. Configure paths and parameters in the script.
3. Execute: `python script_name.py`.
4. Analyze annotated images and luminance plots.

---

## File Structure
```
project_root/
├── main.py       # Main workflow script
├── LAB_Extractor.py     # LAB conversion module
├── data/                # Input images
├── masks/               # Processed images
└── README.md            # Documentation
```



