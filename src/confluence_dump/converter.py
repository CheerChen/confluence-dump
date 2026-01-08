"""
HTML to Markdown converter
"""

from bs4 import BeautifulSoup
from typing import List, Tuple
import markdownify


def extract_confluence_images(html: str) -> List[str]:
    """
    Extract image filenames from Confluence ac:image tags

    Args:
        html: HTML content from Confluence

    Returns:
        list: List of attachment filenames referenced in the content
    """
    import re
    filenames = []

    # Find all ri:attachment tags with filename attribute
    # Pattern: <ri:attachment ri:filename="xxx.png" .../>
    pattern = r'<ri:attachment[^>]*ri:filename="([^"]+)"[^>]*/?>'
    matches = re.findall(pattern, html)
    filenames.extend(matches)

    return list(set(filenames))  # Remove duplicates


def convert_confluence_images(html: str, image_map: dict[str, str]) -> str:
    """
    Convert Confluence ac:image tags to standard img tags

    Args:
        html: HTML content with ac:image tags
        image_map: Mapping of filename -> local_path

    Returns:
        str: HTML with ac:image converted to standard img tags
    """
    import re

    def replace_ac_image(match):
        full_tag = match.group(0)

        # Extract alt text
        alt_match = re.search(r'ac:alt="([^"]+)"', full_tag)
        alt = alt_match.group(1) if alt_match else ""

        # Extract filename from ri:attachment
        filename_match = re.search(r'ri:filename="([^"]+)"', full_tag)
        if filename_match:
            filename = filename_match.group(1)
            # Use local path if available, otherwise use filename
            src = image_map.get(filename, f"images/{filename}")
            return f'<img src="{src}" alt="{alt}" />'

        return ""  # Remove if no filename found

    # Replace all ac:image tags
    pattern = r'<ac:image[^>]*>.*?</ac:image>'
    result = re.sub(pattern, replace_ac_image, html, flags=re.DOTALL)

    return result


def convert_drawio_macros(html: str, image_map: dict[str, str]) -> str:
    """
    Convert Confluence drawio macros to standard img tags

    Drawio macros have a corresponding .drawio.png preview file as attachment.

    Args:
        html: HTML content with drawio macros
        image_map: Mapping of filename -> local_path

    Returns:
        str: HTML with drawio macros converted to img tags
    """
    import re

    def replace_drawio(match):
        full_tag = match.group(0)

        # Extract diagram name from diagramName parameter
        name_match = re.search(r'<ac:parameter ac:name="diagramName">([^<]+)</ac:parameter>', full_tag)
        if name_match:
            diagram_name = name_match.group(1)
            # The PNG preview file is named {diagramName}.png
            png_filename = f"{diagram_name}.png"

            # Use local path if available
            src = image_map.get(png_filename, f"images/{png_filename}")
            alt = diagram_name

            return f'<img src="{src}" alt="{alt}" />'

        return ""  # Remove if no diagram name found

    # Replace all drawio macros
    pattern = r'<ac:structured-macro[^>]*ac:name="drawio"[^>]*>.*?</ac:structured-macro>'
    result = re.sub(pattern, replace_drawio, html, flags=re.DOTALL)

    return result


def html_to_markdown(html: str, image_map: dict[str, str] = None) -> Tuple[str, List[str]]:
    """
    Convert Confluence HTML to Markdown

    Args:
        html: HTML content from Confluence
        image_map: Optional mapping of filename -> local_path for images

    Returns:
        tuple: (markdown_text, list_of_image_filenames)
    """
    if image_map is None:
        image_map = {}

    # 1. Extract Confluence image filenames
    image_filenames = extract_confluence_images(html)

    # 2. Convert Confluence ac:image tags to standard img tags
    html = convert_confluence_images(html, image_map)

    # 3. Convert drawio macros to standard img tags
    html = convert_drawio_macros(html, image_map)

    # 4. Also extract standard img URLs
    soup = BeautifulSoup(html, "html.parser")
    image_urls = []
    for img in soup.find_all("img"):
        src = img.get("src")
        if src:
            image_urls.append(src)

    # 4. Convert to Markdown
    markdown = markdownify.markdownify(
        html, heading_style="ATX", bullets="*", strip=["script", "style"]
    )

    return markdown, image_filenames


def rewrite_image_links(markdown: str, image_map: dict[str, str]) -> str:
    """
    Rewrite image URLs to local paths in Markdown

    Args:
        markdown: Original Markdown text
        image_map: Mapping of original_url -> local_path

    Returns:
        str: Markdown with rewritten image links
    """
    result = markdown
    for original_url, local_path in image_map.items():
        result = result.replace(original_url, local_path)
    return result
