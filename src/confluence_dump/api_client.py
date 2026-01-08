"""
Confluence REST API v2 client
"""

import os
from typing import Any, Optional

import requests


class ConfluenceClient:
    """
    Simple Confluence REST API v2 client for page content retrieval
    """

    def __init__(
        self, base_url: Optional[str], email: Optional[str], api_token: Optional[str]
    ):
        """
        Initialize Confluence client

        Args:
            base_url: Confluence base URL (e.g., https://kinto-dev.atlassian.net)
            email: User email for authentication
            api_token: API token generated from Atlassian account settings
        """
        self.base_url = base_url.rstrip("/") if base_url else ""
        self.email = email if email else ""
        self.api_token = api_token if api_token else ""
        self.session = requests.Session()
        self.session.auth = (self.email, self.api_token)
        self.session.headers.update({"Accept": "application/json"})

    def get_page(self, page_id: str) -> dict[str, Any]:
        """
        Get single page content with body

        Args:
            page_id: Confluence page ID

        Returns:
            dict: Page data with 'body.storage' expanded
        """
        url = f"{self.base_url}/wiki/api/v2/pages/{page_id}?body-format=storage"
        response = self.session.get(url, timeout=30)

        response.raise_for_status()
        return response.json()

    def get_descendants(self, page_id: str) -> list[dict[str, Any]]:
        """
        Get all descendant pages recursively

        Args:
            page_id: Parent page ID

        Returns:
            list: All descendant pages
        """
        all_pages = []
        cursor = None

        while True:
            params = {"limit": 100}
            if cursor:
                params["cursor"] = cursor

            url = f"{self.base_url}/wiki/api/v2/pages/{page_id}/descendants"
            response = self.session.get(url, params=params, timeout=30)

            response.raise_for_status()
            data = response.json()

            all_pages.extend(data.get("results", []))

            # Check for next page
            cursor = data.get("_links", {}).get("next")
            if not cursor:
                break

        return all_pages

    def get_attachments(self, page_id: str) -> list[dict[str, Any]]:
        """
        Get all attachments for a page

        Args:
            page_id: Confluence page ID

        Returns:
            list: Attachment metadata including download links
        """
        all_attachments = []
        cursor = None

        while True:
            params = {"limit": 100}
            if cursor:
                params["cursor"] = cursor

            url = f"{self.base_url}/wiki/api/v2/pages/{page_id}/attachments"
            try:
                response = self.session.get(url, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
            except requests.exceptions.HTTPError as e:
                # If 400 or 404, it might mean no attachments or permission issue
                # Log warning and return what we have
                if e.response.status_code in [400, 404]:
                    print(f"    ⚠ Warning: Failed to fetch attachments for page {page_id} (Status {e.response.status_code})")
                    break
                raise e

            all_attachments.extend(data.get("results", []))

            # Check for next page
            cursor = data.get("_links", {}).get("next")
            if not cursor:
                break

        return all_attachments

    def download_attachment(self, download_link: str) -> bytes:
        """
        Download attachment content using authenticated session

        Args:
            download_link: Relative download link from attachment metadata

        Returns:
            bytes: File content
        """
        # download_link is relative, need to prepend base_url/wiki
        if download_link.startswith("/"):
            url = f"{self.base_url}/wiki{download_link}"
        else:
            url = f"{self.base_url}/wiki/{download_link}"

        response = self.session.get(url, timeout=30)
        response.raise_for_status()
        return response.content


def create_client_from_env() -> ConfluenceClient:
    """
    Create Confluence client from environment variables

    Returns:
        ConfluenceClient: Configured client instance

    Raises:
        ValueError: If required environment variables are missing
    """
    base_url = os.getenv("CONFLUENCE_BASE_URL")
    email = os.getenv("CONFLUENCE_EMAIL")
    api_token = os.getenv("CONFLUENCE_API_TOKEN")

    if not all([base_url, email, api_token]):
        raise ValueError(
            "Missing required environment variables. "
            "Please set CONFLUENCE_BASE_URL, CONFLUENCE_EMAIL, and CONFLUENCE_API_TOKEN."
        )

    return ConfluenceClient(base_url, email, api_token)
