"""
Confluence URL parser utility
"""

import re
from urllib.parse import urlparse


def parse_confluence_url(url: str) -> tuple[str, str]:
    """
    Parse Confluence page URL to extract site and pageId

    Args:
        url: Confluence page URL

    Returns:
        tuple: (site_url, page_id)

    Examples:
        >>> parse_confluence_url("https://kinto-dev.atlassian.net/wiki/pages/viewpage.action?pageId=123456")
        ('https://kinto-dev.atlassian.net', '123456')
        >>> parse_confluence_url("https://kinto-dev.atlassian.net/wiki/spaces/KIDPF/pages/3397648909/title")
        ('https://kinto-dev.atlassian.net', '3397648909')
    """
    parsed = urlparse(url)

    # Extract site URL
    site = f"{parsed.scheme}://{parsed.netloc}"

    # Extract pageId from URL
    # Format 1: .../pages/viewpage.action?pageId=123456 (old format)
    # Format 2: .../wiki/spaces/SPACE/pages/PAGE-ID/title (new format, pageId is 3rd segment)

    # Try extracting from query parameter first (format 1)
    if "pageId=" in url:
        page_id = url.split("pageId=")[1].split("&")[0]
        return site, page_id

    # Handle Confluence Cloud format: /wiki/spaces/SPACE/pages/PAGE-ID/title
    # Extract path and split, handling leading/trailing slashes
    path = parsed.path.lstrip("/").rstrip("/")
    path_parts = path.split("/")

    # Format: /wiki/spaces/SPACE/pages/PAGE-ID/title
    # Index:    0     1      2      3      4      5
    if (
        len(path_parts) >= 5
        and path_parts[0] == "wiki"
        and path_parts[1] == "spaces"
        and path_parts[3] == "pages"
    ):
        # page_id is at index 4
        potential_id = path_parts[4]
        if potential_id.isdigit():
            return site, potential_id

    # Fallback: try last path segment (old format)
    if path_parts:
        last_part = path_parts[-1]
        if last_part.isdigit():
            return site, last_part

    raise ValueError(f"Could not extract pageId from URL: {url}")


def extract_domain(url: str) -> str:
    """
    Extract domain from URL for cookie purposes
    """
    parsed = urlparse(url)
    return parsed.netloc
