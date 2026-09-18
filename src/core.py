'''
Core operations on the in-memory list of bookmarks (add, modify, rm, show).
'''

from datetime import datetime

def add(bookmarks, details) :
    """
    Add a new bookmark into the list of current bookmarks.

    Args:
        bookmarks : list of existing bookmarks, used to compute the new id
        details : tuple (title, url, notes) describing the new bookmark

    Returns:
        The new bookmark tuple
        (id, title, url, notes, creation_date, last_read_date, read_count),
        with read_count at 0 and creation_date used as the initial
        last_read_date

    Constraints:
        bookmarks must not contain duplicate ids.

    Effects:
        None (pure function, does not mutate bookmarks).
    """
    new_id = 1 if not bookmarks else max(map(lambda b: b[0], bookmarks)) + 1
    creation_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return (new_id, details[0], details[1], details[2], creation_date, creation_date, 0)

def find(bookmarks, bookmark_id) :
    """
    Find a bookmark by its id.

    Args:
        bookmarks : list of existing bookmarks
        bookmark_id : bookmark_id of the bookmark to find

    Returns:
        The matching bookmark, or None if no bookmark has this id

    Effects:
        None (pure function).
    """
    found = list(filter(lambda b: b[0] == bookmark_id, bookmarks))
    return found[0] if found else None

def modify(bookmarks, bookmark_id, details):
    """
    Modify an existing bookmark with new details.

    Args:
        bookmarks : list of existing bookmarks
        bookmark_id : bookmark_id of the bookmark to modify
        details : new tuple (title, url, notes) to update the bookmark with

    Returns:
        Updated list of bookmarks, with the bookmark matching bookmark_id
        replaced (id, creation_date, last_read_date and read_count kept
        unchanged); the list is returned unchanged if no bookmark matches

    Effects:
        None (pure function, does not mutate bookmarks).
    """
    modified_bookmarks = list(map(
        lambda b: (b[0], details[0], details[1], details[2], b[4], b[5], b[6])
        if b[0] == bookmark_id else b, bookmarks
    ))
    return modified_bookmarks

def increment_read_count(bookmarks, bookmark_id) :
    """
    Increment the read count of a bookmark and refresh its last-read date.

    Args:
        bookmarks : list of existing bookmarks
        bookmark_id : bookmark_id of the bookmark that was read

    Returns:
        Updated list of bookmarks with the read bookmark's last-read date
        and read count refreshed; the list is returned unchanged if no
        bookmark matches

    Effects:
        None (pure function, does not mutate bookmarks).
    """
    last_read_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return list(map(
        lambda b: (b[0], b[1], b[2], b[3], b[4], last_read_date, b[6] + 1)
        if b[0] == bookmark_id else b,
        bookmarks
    ))

def rm(bookmarks, bookmark_id):
    """
    Remove a bookmark from the list of bookmarks.

    Args:
        bookmarks : list of existing bookmarks
        bookmark_id : bookmark_id of the bookmark to modify

    Returns:
        Updated list of bookmarks without the removed bookmark; the list is
        returned unchanged if no bookmark matches

    Effects:
        None (pure function, does not mutate bookmarks).
    """
    return list(filter(lambda b: b[0] != bookmark_id, bookmarks))

def show(bookmarks):
    """
    Display the bookmarks in a formatted table with centered text.

    Args:
        bookmarks : list of existing bookmarks

    Constraints:
        Every bookmark must have the same number of fields as the header
        (id, title, url, notes, creation_date, last_read_date, read_count).

    Effects:
        Prints the table to stdout.
    """
    header = ("Id", "Title", "Url", "Notes", "Creation Date", "Last-Read Date", "Read Count")
    sorted_bookmarks = [header] + sorted(bookmarks, key=lambda b: b[0])
    parsed_bookmarks = [[str(item).strip() for item in b] for b in sorted_bookmarks]
    max_lengths = [max(len(row[i]) for row in parsed_bookmarks) for i in range(len(header))]

    border = "+" + "+".join("-" * (length + 2) for length in max_lengths) + "+"

    def recursive_print(i):
        if i >= len(parsed_bookmarks):
            return

        row = parsed_bookmarks[i]
        centered_cells = [row[j].center(max_lengths[j]) for j in range(len(row))]

        print("| " + " | ".join(centered_cells) + " |")
        print(border)

        recursive_print(i + 1)

    print(border)
    recursive_print(0)
