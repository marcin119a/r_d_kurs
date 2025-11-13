# Image Download Script

This script downloads images from listings in the `ogloszenia_lodz.csv` file.

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the script:

```bash
python download_images.py
```

Or make it executable and run directly:

```bash
chmod +x download_images.py
./download_images.py
```

## Features

- **Progress bar**: Shows real-time download progress
- **Error handling**: Gracefully handles failed downloads
- **Smart naming**: Images are named `image_00001.jpg`, `image_00002.jpg`, etc.
- **Skip existing**: Won't re-download images that already exist
- **Respectful crawling**: Adds delay between requests to avoid overloading the server
- **Summary report**: Shows statistics at the end

## Configuration

You can modify these settings at the top of the script:

- `OUTPUT_DIR`: Where images will be saved (default: `downloaded/`)
- `TIMEOUT`: Request timeout in seconds (default: 10)
- `DELAY_BETWEEN_REQUESTS`: Delay between downloads in seconds (default: 0.5)

## Output

Images will be saved to: `/home/mw404851/r_d/images/downloaded/`

The script will create this directory automatically if it doesn't exist.

