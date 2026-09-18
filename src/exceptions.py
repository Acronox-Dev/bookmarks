'''
Custom exceptions used by the bookmarks application.
'''

class InvalidURLError(Exception):
    """Raised when a bookmark's URL is not valid (see utils.is_url_valid)."""
