"""
Image downloader
"""

import os
import re
from urllib.parse import urlparse
import requests
from typing import Dict
import concurrent.futures


class ImageDownloader:
    """
    Download images from Confluence and save locally
    """

    def __init__(self, output_dir: str, max_workers: int = 5):
        """
        Initialize downloader

        Args:
            output_dir: Directory to save images
            max_workers: Maximum concurrent download threads
        """
        self.output_dir = output_dir
        self.max_workers = max_workers
        self.session = requests.Session()

    def _generate_filename(self, url: str) -> str:
        """
        Generate filename from URL
        """
        parsed = urlparse(url)
        path = parsed.path
        filename = os.path.basename(path)

        if not filename:
            filename = f"image_{hash(url)}.png"

        # Remove query parameters
        filename = filename.split("?")[0]

        return filename

    def _download_single(self, url: str) -> tuple[str, str | None]:
        """
        Download single image

        Returns:
            tuple: (url, local_path) or (url, None) if failed
        """
        try:
            filename = self._generate_filename(url)
            local_path = os.path.join(self.output_dir, filename)

            # Check if already exists
            if os.path.exists(local_path):
                return url, local_path

            # Download
            response = self.session.get(url, timeout=10, stream=True)
            response.raise_for_status()

            # Save
            with open(local_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            return url, local_path

        except Exception as e:
            print(f"Warning: Failed to download {url}: {e}")
            return url, None

    def download_images(self, urls: list[str]) -> dict[str, str]:
        """
        Download multiple images concurrently

        Args:
            urls: List of image URLs

        Returns:
            dict: Mapping of original_url -> local_path
        """
        if not urls:
            return {}

        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)

        # Download concurrently
        image_map = {}

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.max_workers
        ) as executor:
            future_to_url = {
                executor.submit(self._download_single, url): url for url in urls
            }

            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    downloaded_url, local_path = future.result()
                    if local_path:
                        image_map[downloaded_url] = local_path
                except Exception as e:
                    print(f"Warning: Download failed for {url}: {e}")

        return image_map
