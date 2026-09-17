'''
Utility functions for validating, formatting and deduplicating bookmarks.
'''

from urllib.parse import urlparse
from src.exceptions import InvalidURLError

# VALIDATION FUNCTIONS

def is_url_valid(url) :
    """
    Check whether a URL is valid (uses http/https scheme and has a network location).

    Args:
        url : the URL to validate
    Returns:
        True if the URL is valid, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme in ("http", "https"), result.netloc])
    except ValueError:
        return False

# FORMATTING FUNCTIONS

def format_title(title) :
    """
    Format the title of a bookmark to ensure it is at most 64 characters long.
    Removes any leading or trailing whitespace and truncates the title if it exceeds 64 characters.
    Removes any newline or splitting (";") characters from the title.

    Args:
        title : the title of the bookmark
    Returns:
        Formatted title, truncated to 64 characters if necessary
    """
    return title.strip().replace("\n", "").replace(";", "")[:64]

def format_url(url) :
    """
    Format the URL of a bookmark to ensure it is valid and properly formatted.
    Removes any leading or trailing whitespace and ensures the URL starts with "http://" or "https://".

    Args:
        url : the URL of the bookmark
    Returns:
        Formatted URL, or None if the URL is invalid
    """
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "http://" + url
    return url if is_url_valid(url) else None

# OTHERS

def url_duplicate_detection(details, bookmarks) :
    """
    Check whether the url contained in details is already used by an existing bookmark.

    Args:
        details : Array values describing the bookmark, url expected at index 1
        bookmarks : list of existing bookmarks
    Returns:
        True if the url is already present among the bookmarks, False otherwise
    """
    return details.split(";")[1] in [b.split(";")[2] for b in bookmarks]