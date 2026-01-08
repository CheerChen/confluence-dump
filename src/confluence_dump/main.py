"""
Confluence Dump CLI - Export Confluence pages to Markdown for LLM context
"""

import os
import sys
import re
from pathlib import Path

import click
from dotenv import load_dotenv
import requests

from confluence_dump import __version__
from confluence_dump.url_parser import parse_confluence_url
from confluence_dump.api_client import ConfluenceClient, create_client_from_env
from confluence_dump.converter import html_to_markdown, rewrite_image_links
from confluence_dump.downloader import ImageDownloader


def sanitize_filename(name: str) -> str:
    """
    Remove invalid filename characters while preserving as much as possible
    Only removes characters that are truly invalid in filenames
    """
    invalid_chars = r'<>:"|?*\/\x00-\x1f'
    sanitized = re.sub(f"[{re.escape(invalid_chars)}]", "", name)
    sanitized = re.sub(r"\s+", " ", sanitized).strip()
    return sanitized if sanitized else "Untitled"


def export_page(
    client: ConfluenceClient, page_id: str, output_dir: str, page_data: dict
) -> bool:
    """
    Export single page to Markdown with images

    Args:
        client: Confluence API client
        page_id: Page ID
        output_dir: Output directory
        page_data: Page data from API (may not include body content)

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        title = page_data.get("title", "Untitled")
        
        # If page_data doesn't have body content, fetch it from API
        html_content = page_data.get("body", {}).get("storage", {}).get("value")
        if html_content is None:
            # Fetch full page content from API
            full_page = client.get_page(page_id)
            html_content = full_page.get("body", {}).get("storage", {}).get("value", "")

        print(f"  → Exporting: {title}")

        safe_title = sanitize_filename(title)
        page_dir = os.path.join(output_dir, safe_title)
        os.makedirs(page_dir, exist_ok=True)

        # Handle empty content - create markdown with just the title
        if not html_content:
            markdown = f"# {title}\n\n*(This page has no content)*\n"
            image_filenames = []
        else:
            # Get attachments and build filename -> download_link mapping
            attachments = client.get_attachments(page_id)
            attachment_map = {}
            for att in attachments:
                filename = att.get("title", "")
                download_link = att.get("downloadLink", "")
                if filename and download_link:
                    attachment_map[filename] = download_link

            # Download images and build filename -> local_path mapping
            image_map = {}
            if attachment_map:
                image_dir = os.path.join(page_dir, "images")
                os.makedirs(image_dir, exist_ok=True)

                for filename, download_link in attachment_map.items():
                    # Only download image files
                    if any(filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp']):
                        try:
                            content = client.download_attachment(download_link)
                            local_path = os.path.join(image_dir, filename)
                            with open(local_path, "wb") as f:
                                f.write(content)
                            # Store relative path for markdown
                            image_map[filename] = f"images/{filename}"
                        except Exception as e:
                            print(f"    ⚠ Failed to download {filename}: {e}")

                if image_map:
                    print(f"    ✓ Downloaded {len(image_map)} images")

            # Convert HTML to Markdown with image mapping
            markdown, image_filenames = html_to_markdown(html_content, image_map)

        md_path = os.path.join(page_dir, "README.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(markdown)

        print(f"    ✓ Saved: {md_path}")
        return True

    except Exception as e:
        print(f"  ✗ Failed to export page: {e}")
        return False


@click.command()
@click.argument("url")
@click.option(
    "-o",
    "--output",
    default="./output",
    help="Output directory (default: ./output)",
)
@click.option(
    "-r",
    "--recursive/--no-recursive",
    default=True,
    help="Include all descendant pages (default: True)",
)
@click.option(
    "-f",
    "--format",
    default="md",
    type=click.Choice(["md", "html", "json"]),
    help="Output format (default: md)",
)
@click.option(
    "-i",
    "--include-images/--no-include-images",
    default=True,
    help="Download and embed images (default: True)",
)
@click.option("-v", "--verbose/--no-verbose", default=False, help="Verbose output")
@click.version_option(__version__, prog_name="confluence-dump")
def main(
    url: str,
    output: str,
    recursive: bool,
    format: str,
    include_images: bool,
    verbose: bool,
):
    """
    Export Confluence pages to Markdown for LLM context

    Example:
        confluence-dump https://kinto-dev.atlassian.net/wiki/pages/viewpage.action?pageId=3140419873
    """
    if verbose:
        print(f"DEBUG: Original URL: {url}")

    try:
        load_dotenv()

        site, page_id = parse_confluence_url(url)

        if verbose:
            print(f"DEBUG: Parsed site: {site}")
            print(f"DEBUG: Parsed page ID: {page_id}")

        client = create_client_from_env()

        output_path = Path(output)
        output_path.mkdir(parents=True, exist_ok=True)

        print(f"\n📚 Confluence Dump Tool")
        print(f"═════════════════════════\n")

        pages = []
        if recursive:
            print(f"🔍 Fetching all descendant pages...")
            all_pages = client.get_descendants(page_id)
            parent_page = client.get_page(page_id)
            pages = [parent_page] + all_pages
            print(f"✓ Found {len(pages)} pages total")
        else:
            print(f"🔍 Fetching single page...")
            page_data = client.get_page(page_id)
            pages = [page_data]
            print(f"✓ Found page: {page_data.get('title')}")

        print(f"\n📥 Exporting to: {output_path.absolute()}\n")

        success_count = 0
        for page_data in pages:
            if export_page(client, page_data["id"], str(output_path), page_data):
                success_count += 1

        print(f"\n✅ Export completed!")
        print(f"   Total: {len(pages)} pages")
        print(f"   Success: {success_count} pages")
        print(f"   Failed: {len(pages) - success_count} pages")
        print(f"\n📁 Output: {output_path.absolute()}")

    except ValueError as e:
        print(f"❌ Configuration Error: {e}", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"❌ API Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        if verbose:
            import traceback

            traceback.print_exc()
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
