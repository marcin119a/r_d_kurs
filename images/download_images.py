#!/usr/bin/env python3
"""
Script to download images from ogloszenia_lodz.csv file.
Downloads images from the image_url column and saves them locally.
"""

import csv
import os
import requests
from pathlib import Path
from urllib.parse import urlparse
import time
import argparse
from tqdm import tqdm

# Get the script directory
SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent

# Configuration
DEFAULT_CSV_FILE = PROJECT_ROOT / "scraper" / "data" / "ogloszenia_lodz.csv"
DEFAULT_OUTPUT_DIR = SCRIPT_DIR / "downloaded"
TIMEOUT = 1  # seconds
DELAY_BETWEEN_REQUESTS = 0.5  # seconds to be respectful to the server
DEFAULT_MAX_IMAGES = 10  # maximum number of images to download (None for all)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Download images from ogloszenia_lodz.csv file"
    )
    parser.add_argument(
        "--csv",
        type=str,
        default=str(DEFAULT_CSV_FILE),
        help=f"Path to CSV file (default: {DEFAULT_CSV_FILE})"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=str(DEFAULT_OUTPUT_DIR),
        help=f"Output directory for images (default: {DEFAULT_OUTPUT_DIR})"
    )
    parser.add_argument(
        "--max-images",
        type=int,
        default=DEFAULT_MAX_IMAGES,
        help=f"Maximum number of images to download (default: {DEFAULT_MAX_IMAGES}, use 0 for all)"
    )
    return parser.parse_args()


def create_output_directory(output_dir):
    """Create the output directory if it doesn't exist."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {output_dir}")


def get_image_filename(url, index):
    """
    Generate a filename for the image based on the URL and index.
    
    Args:
        url: Image URL
        index: Row index from CSV
    
    Returns:
        Filename string
    """
    if not url:
        return None
    
    parsed_url = urlparse(url)
    original_filename = os.path.basename(parsed_url.path)
    
    # Extract file extension
    _, ext = os.path.splitext(original_filename)
    if not ext:
        ext = '.jpg'  # default extension
    
    # Create filename with index to avoid duplicates
    filename = f"image_{index:05d}{ext}"
    return filename


def download_image(url, filepath):
    """
    Download an image from URL and save it to filepath.
    
    Args:
        url: Image URL to download
        filepath: Local path where to save the image
    
    Returns:
        True if successful, False otherwise
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=TIMEOUT, stream=True)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return True
    except requests.exceptions.RequestException as e:
        print(f"\nError downloading {url}: {e}")
        return False
    except Exception as e:
        print(f"\nUnexpected error for {url}: {e}")
        return False


def main():
    """Main function to orchestrate the image downloading process."""
    # Parse command line arguments
    args = parse_arguments()
    csv_file = args.csv
    output_dir = args.output
    max_images = args.max_images if args.max_images > 0 else None
    
    print("Starting image download script...")
    print("=" * 60)
    
    # Create output directory
    create_output_directory(output_dir)
    
    # Read CSV file and collect image URLs
    image_data = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, start=1):
            image_url = row.get('image_url', '').strip()
            if image_url:  # Only process rows with image URLs
                image_data.append({
                    'index': idx,
                    'url': image_url,
                    'locality': row.get('locality', ''),
                    'street': row.get('street', '')
                })
    
    # Limit the number of images if max_images is set
    if max_images is not None:
        image_data = image_data[:max_images]
    
    print(f"Found {len(image_data)} images to download")
    print("=" * 60)
    
    # Download images
    successful = 0
    failed = 0
    skipped = 0
    
    for data in tqdm(image_data, desc="Downloading images", unit="image"):
        filename = get_image_filename(data['url'], data['index'])
        if not filename:
            skipped += 1
            continue
        
        filepath = os.path.join(output_dir, filename)
        
        # Skip if file already exists
        if os.path.exists(filepath):
            skipped += 1
            continue
        
        # Download the image
        if download_image(data['url'], filepath):
            successful += 1
        else:
            failed += 1
        
        # Be respectful to the server
        time.sleep(DELAY_BETWEEN_REQUESTS)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 Download Summary:")
    print(f"  ✅ Successful: {successful}")
    print(f"  ❌ Failed: {failed}")
    print(f"  ⏭️  Skipped (already exists): {skipped}")
    print(f"  📦 Total: {len(image_data)}")
    print("=" * 60)
    print(f"💾 Images saved to: {output_dir}")


if __name__ == "__main__":
    main()

