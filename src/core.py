'''
Core operations on the in-memory list of bookmarks (add, modify, rm, show,
link/unlink related bookmarks).
'''

from datetime import datetime

from src import reminders

def add(bookmarks, details) :
    """
    Add a new bookmark into the list of current bookmarks.

    Args:
        bookmarks : list of existing bookmarks, used to compute the new id
        details : tuple (title, url, notes, labels) describing the new
            bookmark, labels being a tuple of label strings

    Returns:
        The new bookmark tuple
        (id, title, url, notes, creation_date, last_read_date, read_count,
        labels, related_ids), with read_count at 0, creation_date used as
        the initial last_read_date, and related_ids empty

    Constraints:
        bookmarks must not contain duplicate ids.

    Effects:
        None (pure function, does not mutate bookmarks).
    """
    new_id = 1 if not bookmarks else max(map(lambda b: b[0], bookmarks)) + 1
    creation_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return (
        new_id, details[0], details[1], details[2], creation_date,
        creation_date, 0, details[3], ()
    )

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
        details : new tuple (title, url, notes, labels) to update the
            bookmark with

    Returns:
        Updated list of bookmarks, with the bookmark matching bookmark_id
        replaced (id, creation_date, last_read_date, read_count and
        related_ids kept unchanged); the list is returned unchanged if no
        bookmark matches

    Effects:
        None (pure function, does not mutate bookmarks).
    """
    modified_bookmarks = list(map(
        lambda b: (
            b[0], details[0], details[1], details[2], b[4], b[5], b[6],
            details[3], b[8]
        )
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
        lambda b: (b[0], b[1], b[2], b[3], b[4], last_read_date, b[6] + 1, b[7], b[8])
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
        Updated list of bookmarks without the removed bookmark, and with
        bookmark_id removed from every remaining bookmark's related_ids;
        the list is returned unchanged if no bookmark matches

    Effects:
        None (pure function, does not mutate bookmarks).
    """
    remaining = list(filter(lambda b: b[0] != bookmark_id, bookmarks))
    return list(map(
        lambda b: (b[0], b[1], b[2], b[3], b[4], b[5], b[6], b[7],
                   tuple(r for r in b[8] if r != bookmark_id)),
        remaining
    ))

def link(bookmarks, first_id, second_id, remove=False):
    """
    Add or remove a bidirectional relation between two bookmarks.

    Args:
        bookmarks : list of existing bookmarks
        first_id : bookmark_id of the first bookmark
        second_id : bookmark_id of the second bookmark
        remove : if True, remove the relation instead of adding it

    Returns:
        Updated list of bookmarks with first_id and second_id added to (or
        removed from) each other's related_ids; the list is returned
        unchanged if either id does not match an existing bookmark

    Effects:
        None (pure function, does not mutate bookmarks).
    """
    if not find(bookmarks, first_id) or not find(bookmarks, second_id):
        return bookmarks

    def update(b):
        other_id = second_id if b[0] == first_id else first_id if b[0] == second_id else None
        if other_id is None:
            return b
        if remove:
            related_ids = tuple(r for r in b[8] if r != other_id)
        else:
            related_ids = b[8] if other_id in b[8] else b[8] + (other_id,)
        return (b[0], b[1], b[2], b[3], b[4], b[5], b[6], b[7], related_ids)

    return list(map(update, bookmarks))

def render_table(header, rows):
    """
    Print a formatted table with centered text.

    Args:
        header : tuple of column names
        rows : list of tuples, each with the same length as header

    Constraints:
        Every row must have the same number of fields as header.

    Effects:
        Prints the table to stdout.
    """
    all_rows = [header] + rows
    parsed_rows = [[str(item).strip() for item in row] for row in all_rows]
    max_lengths = [max(len(row[i]) for row in parsed_rows) for i in range(len(header))]

    border = "+" + "+".join("-" * (length + 2) for length in max_lengths) + "+"

    def recursive_print(i):
        if i >= len(parsed_rows):
            return

        row = parsed_rows[i]
        centered_cells = [row[j].center(max_lengths[j]) for j in range(len(row))]

        print("| " + " | ".join(centered_cells) + " |")
        print(border)

        recursive_print(i + 1)

    print(border)
    recursive_print(0)

BOOKMARK_TABLE_HEADER = (
    "Id", "Title", "Url", "Notes", "Creation Date", "Last-Read Date",
    "Read Count", "Labels", "Related", "Reminder", "Read Time"
)

def bookmark_row(bookmark, config):
    """
    Build a display row for a bookmark, with labels and related_ids
    joined into readable text and reading reminder / reading time columns
    appended.

    Args:
        bookmark : bookmark tuple
        config : configuration dict, used to compute the reminder flag and
            the reading time estimate (see reminders.is_stale and
            reminders.estimate_reading_minutes)

    Returns:
        Tuple (id, title, url, notes, creation_date, last_read_date,
        read_count, labels, related_ids, reminder, reading_time), all
        fields formatted as display-ready strings/values.

    Effects:
        None (pure function).
    """
    reminder = "!" if reminders.is_stale(bookmark, config) else ""
    reading_time = f"{reminders.estimate_reading_minutes(bookmark, config)} min"
    return bookmark[:7] + (
        ",".join(bookmark[7]), ",".join(map(str, bookmark[8])), reminder, reading_time
    )

def show(bookmarks, config):
    """
    Display the bookmarks in a formatted table with centered text.

    Args:
        bookmarks : list of existing bookmarks
        config : configuration dict, used to compute the reminder flag and
            the reading time estimate for each bookmark

    Effects:
        Prints the table to stdout.
    """
    rows = [bookmark_row(b, config) for b in sorted(bookmarks, key=lambda b: b[0])]
    render_table(BOOKMARK_TABLE_HEADER, rows)
