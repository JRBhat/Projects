# Automated Image Blur detection with GUI

This project implements an automated system for monitoring and assessing the quality of images in a specified directory. It provides real-time analysis of newly added images, checking for blurriness and the presence of white calibration cards.

## Features

- Real-time directory monitoring for new image files
- Blur detection using Laplacian variance
- White calibration card detection
- Custom GUI for user interaction and metadata correction
- Logging system for tracking operations and errors

## Requirements

- Python 3.7+
- OpenCV
- NumPy
- PySimpleGUI
- Matplotlib
- pywin32

## Installation

1. Clone this repository
2. Install required packages: `pip install -r requirements.txt`

## Usage

Run the script with appropriate parameters:

python main.py --path /path/to/watch --threshold 2.1 --white_threshold 190


## Configuration

Adjust the following parameters in the script as needed:

- `THRESH`: Blur detection threshold
- `WhiteCard_thresh`: White card detection threshold
- `freeze_count`: Maximum wait time for file system events

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)

