# Image Processing, layout adjustment in Excel and PDF Report Generation through LaTeX

## Overview
This Python script automates the process of converting, validating, and processing images for clinical studies. It handles tasks such as file conversion, renaming, missing file handling, data randomization, and generating reports in PDF format. The script is specifically tailored to handle image data and metadata, which are often required for clinical trials.

## Key Features:
- **Image Validation & Conversion**: Validates and converts image files to a standard format, including renaming Visia files if necessary.
- **Data Randomization**: Supports various randomization templates (Standard, Custom, Transposed) based on user input.
- **Excel Template Creation**: Generates an editable Excel file for user input and modifications.
- **Report Generation**: Creates a LaTeX-based report from the processed data and converts it into a PDF.
- **Archiving**: Archives the results for later retrieval.

## Requirements:
- Python 3.x
- `openpyxl`, `subprocess`, `re`, and other internal modules (listed in the code)
- LaTeX for PDF generation (`pdflatex` command)

## Usage:
1. Run the script.
2. Follow the prompts to check and validate image files.
3. Edit the generated Excel file as needed and input randomized data.
4. The script will generate a final PDF report and archive the results.

## Notes:
- Ensure that required templates and files are available before running the script.
- The `pdflatex` tool is required to generate the PDF report.

