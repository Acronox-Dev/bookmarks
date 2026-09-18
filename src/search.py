'''
Search, filter and sort bookmarks by text, label, domain and various
fields.
'''

from urllib.parse import urlparse

SORT_KEYS = {
    "id": lambda b: b[0],
    "title": lambda b: b[1].lower(),
    "read_count": lambda b: b[6],
    "creation_date": lambda b: b[4],
    "last_read_date": lambda b: b[5],
}

def domain_of(bookmark):
    """
    Extract the network location (domain) of a bookmark's URL.

    Args:
        bookmark : bookmark tuple, using url at index 2

    Returns:
        The bookmark's URL domain (e.g. "example.com")

    Effects:
        None (pure function).
    """
    return urlparse(bookmark[2]).netloc

def matches(bookmark, query=None, label=None, domain=None):
    """
    Check whether a bookmark satisfies every given filter. A filter left
    as None is ignored.

    Args:
        bookmark : bookmark tuple to test
        query : text that must appear (case-insensitively) in the title
            or the notes
        label : label that must be present on the bookmark
        domain : text that must appear in the bookmark's URL domain

    Returns:
        True if every provided filter matches, False otherwise

    Effects:
        None (pure function).
    """
    if query is not None:
        haystack = f"{bookmark[1]} {bookmark[3]}".lower()
        if query.lower() not in haystack:
            return False
    if label is not None and label not in bookmark[7]:
        return False
    if domain is not None and domain not in domain_of(bookmark):
        return False
    return True

def filter_bookmarks(bookmarks, query=None, label=None, domain=None):
    """
    Keep only the bookmarks matching every given filter.

    Args:
        bookmarks : list of existing bookmarks
        query : see matches()
        label : see matches()
        domain : see matches()

    Returns:
        The bookmarks for which matches() is True

    Effects:
        None (pure function).
    """
    return [b for b in bookmarks if matches(b, query, label, domain)]

def sort_bookmarks(bookmarks, sort_by="id", descending=False):
    """
    Sort bookmarks by a given field.

    Args:
        bookmarks : list of existing bookmarks
        sort_by : one of "id", "title", "read_count", "creation_date",
            "last_read_date" (default "id")
        descending : if True, sort in descending order

    Returns:
        A new list of bookmarks sorted by sort_by

    Constraints:
        sort_by must be a key of SORT_KEYS.

    Effects:
        None (pure function).
    """
    return sorted(bookmarks, key=SORT_KEYS[sort_by], reverse=descending)
