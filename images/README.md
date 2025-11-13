# Image Download Script

This script downloads images from listings in the `ogloszenia_lodz.csv` file.

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the script with default settings:

```bash
python download_images.py
```

Or with custom parameters:

```bash
# Download all images to a custom directory
python download_images.py --max-images 0 --output ./my_images

# Use a different CSV file
python download_images.py --csv /path/to/other.csv

# Download 50 images
python download_images.py --max-images 50
```

Make it executable and run directly:

```bash
chmod +x download_images.py
./download_images.py --max-images 20
```

View all available options:

```bash
python download_images.py --help
```

## Features

- **Progress bar**: Shows real-time download progress
- **Error handling**: Gracefully handles failed downloads
- **Smart naming**: Images are named `image_00001.jpg`, `image_00002.jpg`, etc.
- **Skip existing**: Won't re-download images that already exist
- **Respectful crawling**: Adds delay between requests to avoid overloading the server
- **Summary report**: Shows statistics at the end

## Configuration

### Command Line Arguments

- `--csv`: Path to CSV file (default: `../scraper/data/ogloszenia_lodz.csv`)
- `--output`: Output directory for images (default: `./downloaded`)
- `--max-images`: Maximum number of images to download (default: 10, use 0 for all)

### Script Settings

You can modify these settings at the top of the script:

- `TIMEOUT`: Request timeout in seconds (default: 1)
- `DELAY_BETWEEN_REQUESTS`: Delay between downloads in seconds (default: 0.5)

## Output

By default, images are saved to: `./downloaded/` (relative to the script location)

The script will create this directory automatically if it doesn't exist.

