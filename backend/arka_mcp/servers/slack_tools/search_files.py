"""
Slack Search Files Tool.

Searches for files across the workspace using search.files.

Slack API Reference:
https://api.slack.com/methods/search.files
"""
from typing import Dict, Any, Optional
from .client import SlackAPIClient


async def search_files(
    query: str,
    count: Optional[int] = 20,
    highlight: Optional[bool] = True,
    page: Optional[int] = 1,
    sort: Optional[str] = "score",
    sort_dir: Optional[str] = "desc"
) -> Dict[str, Any]:
    """
    Search for files across the Slack workspace.

    Args:
        query: Search query (supports operators like from:@user, in:#channel, type:pdf, etc.)
        count: Number of results to return per page (default: 20, max: 100)
        highlight: Highlight matching terms in results (default: True)
        page: Page number for pagination (1-indexed, default: 1)
        sort: Sort order - "score" (relevance) or "timestamp" (default: "score")
        sort_dir: Sort direction - "desc" or "asc" (default: "desc")

    Returns:
        Dict containing:
        - ok: Success status
        - query: The search query used
        - files: Search results object with:
          - total: Total number of matching files
          - matches: Array of file objects with:
            - id: File ID
            - name: Filename
            - title: File title
            - mimetype: MIME type (e.g., "application/pdf", "image/png")
            - filetype: File type (e.g., "pdf", "png", "docx")
            - pretty_type: Human-readable type (e.g., "PDF", "PNG Image")
            - user: User ID who uploaded
            - username: Username
            - size: File size in bytes
            - url_private: Private download URL
            - url_private_download: Direct download URL
            - permalink: Permanent link to file
            - timestamp: Upload timestamp
            - channels: Array of channel IDs where shared
            - comments_count: Number of comments
            - preview: File preview text (if available)
            - thumb_*: Thumbnail URLs in various sizes
          - pagination: Pagination info with page, page_count, total_count
          - paging: Additional paging details

    Raises:
        ValueError: If Slack API returns an error

    Example:
        # Simple filename search
        result = await search_files(
            query="presentation.pdf"
        )
        # Returns: {
        #   "ok": True,
        #   "query": "presentation.pdf",
        #   "files": {
        #     "total": 5,
        #     "matches": [
        #       {
        #         "id": "F1234567890",
        #         "name": "Q4_presentation.pdf",
        #         "title": "Q4 Results Presentation",
        #         "mimetype": "application/pdf",
        #         "filetype": "pdf",
        #         "pretty_type": "PDF",
        #         "user": "U1234567890",
        #         "username": "john",
        #         "size": 2048576,
        #         "url_private": "https://files.slack.com/files-pri/...",
        #         "permalink": "https://workspace.slack.com/files/...",
        #         "timestamp": 1234567890,
        #         "channels": ["C1234567890"],
        #         ...
        #       },
        #       ...
        #     ],
        #     "pagination": {
        #       "page": 1,
        #       "page_count": 1,
        #       "total_count": 5
        #     }
        #   }
        # }

        # Search by file type
        result = await search_files(
            query="type:pdf"
        )

        # Search files from specific user
        result = await search_files(
            query="from:@sarah type:image"
        )

        # Search files in specific channel
        result = await search_files(
            query="in:#design mockup"
        )

        # Search with date range
        result = await search_files(
            query="report after:2024-01-01 before:2024-12-31"
        )

        # Search by multiple criteria
        result = await search_files(
            query='from:@john in:#engineering type:pdf "architecture"'
        )

        # Get more results, sorted by date
        result = await search_files(
            query="screenshot",
            count=50,
            sort="timestamp",
            sort_dir="desc"
        )

        # Paginate through results
        result = await search_files(
            query="spreadsheet",
            page=2,
            count=20
        )

    Search Query Operators:
        - from:@username - Files from specific user
        - in:#channel - Files shared in specific channel
        - type:filetype - Files of specific type (pdf, image, doc, etc.)
        - "exact phrase" - Exact phrase match in filename/title
        - after:YYYY-MM-DD - Files uploaded after date
        - before:YYYY-MM-DD - Files uploaded before date
        - on:YYYY-MM-DD - Files uploaded on specific date
        - from:me - Files uploaded by authenticated user

    Common File Types:
        - type:pdf - PDF documents
        - type:image - All images (jpg, png, gif, etc.)
        - type:doc - Word documents
        - type:spreadsheet - Excel/Google Sheets
        - type:presentation - PowerPoint/Slides
        - type:video - Video files
        - type:audio - Audio files
        - type:zip - Compressed archives
        - type:text - Text files
        - type:code - Source code files

    Notes:
        - Requires search:read scope
        - Search is case-insensitive by default
        - Use quotes for exact phrase matching
        - Highlight wraps matches in <em> tags
        - Maximum 100 results per page
        - Pagination uses 1-based indexing
        - sort="score" ranks by relevance (recommended)
        - sort="timestamp" orders by upload date
        - Returns error "invalid_query" for malformed queries
        - Rate limits apply (Tier 2: 20+ requests per minute)
        - Search includes all files user has access to
        - Private channel files only searchable if user is member
        - File URLs are private and require authentication
        - URLs expire after some time
        - Preview text available for text-based files
        - Thumbnails available for images and some documents
    """
    client = SlackAPIClient()

    # Build request parameters
    params: Dict[str, Any] = {
        "query": query,
        "count": min(count, 100) if count else 20,  # Cap at API maximum
        "page": page
    }

    if highlight is not None:
        params["highlight"] = highlight
    if sort:
        params["sort"] = sort
    if sort_dir:
        params["sort_dir"] = sort_dir

    # Use GET method for search.files
    return await client.get_method("search.files", params)
