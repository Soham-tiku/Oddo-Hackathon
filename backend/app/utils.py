from flask import jsonify
import bleach

ALLOWED_TAGS = [
    "p", "b", "i", "u", "pre", "code", "ul", "ol", "li", "blockquote", "a", "h1", "h2", "h3"
]

def sanitize_html(html: str) -> str:
    """Remove dangerous tags / attrs from rich‑text input."""
    return bleach.clean(html, tags=ALLOWED_TAGS, strip=True)


def error_response(message, status_code):
    response = jsonify({"error": message})
    response.status_code = status_code
    return response