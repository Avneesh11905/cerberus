"""
Contains shared utility functions for the API layer.
Includes custom response formatters and generic error handlers to maintain a consistent JSON structure across the entire app.
"""

from urllib.parse import urlparse

from fastapi import Request

from src.shared.domain.entities import ClientMetadata


def extract_client_metadata(request: Request) -> ClientMetadata:
    """Extracts IP address and User-Agent from the incoming request."""
    ip = request.client.host if request.client else None
    ua = request.headers.get("user-agent")

    safe_headers = [
        "accept-language",
        "referer",
        "host",
        "cf-ipcountry",
        "sec-ch-ua",
        "sec-ch-ua-mobile",
        "sec-ch-ua-platform",
        "origin",
        "x-forwarded-for",
    ]
    extra = {k: v for k, v in request.headers.items() if k.lower() in safe_headers}

    return ClientMetadata(ip_address=ip, user_agent=ua, extra_headers=extra)


def origin_from_url(value: str | None) -> str | None:
    if not value:
        return None
    parsed = urlparse(value)
    if not parsed.scheme or not parsed.netloc:
        return None
    return f"{parsed.scheme}://{parsed.netloc}".rstrip("/")
