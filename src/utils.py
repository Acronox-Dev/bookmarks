from urllib.parse import urlparse
from src.exceptions import InvalidURLError
import src.commands as commands

# VALIDATION FUNCTIONS

def is_url_valid(url) :
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

# FACTORING FUNCTIONS

def do_commands(options, bookmarks) :
    if options.command == 'add' or options.command == 'modify':
        title = format_title(options.t[:64] if options.t else "")
        url = format_url(options.u if options.u else "")
        notes = options.n if options.n else ""
    
        if not is_url_valid(url):
            raise InvalidURLError
    
        details = "; ".join([title, url, notes])

        if options.command == 'add' : 
            commands.add(details, options.file, bookmarks)
        else :
            commands.modify(options.id, details, options.file, bookmarks)
    
    elif options.command == 'rm':
        commands.rm(options.id, options.file, bookmarks)
    
    elif options.command == 'show':
        commands.show(bookmarks)

# OTHERS

def url_duplicate_detection(details, bookmarks) :
    if details.split(";")[1] in [b.split(";")[2] for b in bookmarks] :
        print("This URL has alreay been added")
        return