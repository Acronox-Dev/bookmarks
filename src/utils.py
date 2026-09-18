'''
Utility functions for validating, formatting and deduplicating bookmarks.
'''

from urllib.parse import urlparse

# VALIDATION FUNCTIONS

def is_url_valid(url) :
    """
    Check whether a URL is valid (uses http/https scheme and has a network location).

    Args:
        url : the URL to validate
    Returns:
        True if the URL is valid, False otherwise
    Effects:
        None (pure function).
    """
    try:
        result = urlparse(url)
        return all([result.scheme in ("http", "https"), result.netloc])
    except ValueError:
        return False

def validate_option_types(options):
    """
    Validate the types of the parsed command line options and cast the
    bookmark id to an int in place when present.

    Args:
        options : parsed command line options (command, id, t, u, n, file)

    Returns:
        True if every present option has a valid type, False otherwise

    Effects:
        Prints an error message per invalid option and mutates
        options.id in place, replacing it with an int when it is valid.
    """
    types_boolean = True

    if hasattr(options, 't') and options.t is not None and not isinstance(options.t, str):
        print("Le titre doit être une chaîne de caractères")
        types_boolean = False

    if hasattr(options, 'u') and options.u and not isinstance(options.u, str):
        print("L'URL cible doit être une chaîne de caractères")
        types_boolean = False

    if hasattr(options, 'n') and options.n is not None and not isinstance(options.n, str):
        print("Les notes doivent être une chaîne de caractères")
        types_boolean = False

    if hasattr(options, 'id') and options.id is not None:
        try:
            options.id = int(options.id)
        except ValueError:
            print("L'ID doit être un nombre entier")
            types_boolean = False

    return types_boolean

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
    Effects:
        None (pure function).
    """
    return title.strip().replace("\n", "").replace(";", "")[:64]

def format_url(url) :
    """
    Format the URL of a bookmark to ensure it is valid and properly formatted.
    Removes any leading or trailing whitespace and ensures the URL starts
    with "http://" or "https://".

    Args:
        url : the URL of the bookmark
    Returns:
        Formatted URL, or None if the URL is invalid
    Effects:
        None (pure function).
    """
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "http://" + url
    return url if is_url_valid(url) else None

def format_notes(notes) :
    """
    Format the notes of a bookmark.
    Removes any leading or trailing whitespace and removes any newline
    or splitting (";") characters.

    Args:
        notes : the notes of the bookmark
    Returns:
        Formatted notes
    Effects:
        None (pure function).
    """
    return notes.strip().replace("\n", "").replace(";", "")

# FACTORING FUNCTIONS

def write_bookmarks(filename, file_right, bookmarks):
    """
    Write bookmarks to the bookmarks file, one per line, using the
    id; title; url; notes; creation_date; last_read_date; read_count format.

    Args:
        filename : path of the bookmarks file to write to
        file_right : file mode to open the file with ('a' to append, 'w' to overwrite)
        bookmarks : list of bookmark tuples to write

    Effects:
        Opens filename in file_right mode and writes the serialized
        bookmarks to it.
    """
    content = "".join(
        "; ".join(str(field) for field in bookmark) + "\n" for bookmark in bookmarks
    )
    with open(filename, file_right, encoding='utf-8') as f:
        f.write(content)

# OTHERS

def parse_bookmarks(lines):
    """
    Convert the lines read from the bookmarks file into bookmark tuples.

    Args:
        lines: lines read from the bookmarks file.

    Returns:
        List of tuples (id, title, url, notes, creation_date, last_read_date, read_count).

    Constraints:
        Each non-empty line must follow the
        id; title; url; notes; creation_date; last_read_date; read_count format.

    Effects:
        None (pure function).
    """
    def parse_line(line):
        """
        Parse a single bookmark line.

        Args:
            line: line in the id; title; url; notes; creation_date; last_read_date;
                read_count format.

        Returns:
            Tuple (id, title, url, notes, creation_date, last_read_date, read_count).

        Constraints:
            The line must contain exactly seven fields separated by '; '.

        Effects:
            None (pure function).
        """
        bookmark_id, title, url, notes, creation_date, last_read_date, read_count = (
            line.split("; ", 6)
        )
        return (
            int(bookmark_id), format_title(title), url,
            format_notes(notes), creation_date, last_read_date, int(read_count)
        )

    return list(map(parse_line, filter(None, map(str.strip, lines))))

def url_duplicate_detection(details, bookmarks) :
    """
    Check whether the url contained in details is already used by an existing bookmark.

    Args:
        details : tuple describing the bookmark (title, url, notes), url expected at index 1
        bookmarks : list of existing bookmark tuples
    Returns:
        True if the url is already present among the bookmarks, False otherwise
    Effects:
        None (pure function).
    """
    return details[1] in [b[2] for b in bookmarks]
