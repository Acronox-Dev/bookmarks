'''
Export and import bookmarks to/from JSON, CSV, the Netscape Bookmark
File Format used by Firefox/Chrome ("html"), or Markdown (export-only).
'''

import csv
import html
import json
from datetime import datetime
from html.parser import HTMLParser

CSV_FIELDS = (
    "id", "title", "url", "notes", "creation_date", "last_read_date",
    "read_count", "labels", "related_ids"
)

def bookmark_to_dict(bookmark):
    """
    Convert a bookmark tuple into a JSON-friendly dict.

    Args:
        bookmark : bookmark tuple

    Returns:
        A dict with one key per bookmark field, labels and related_ids
        as lists

    Effects:
        None (pure function).
    """
    return {
        "id": bookmark[0], "title": bookmark[1], "url": bookmark[2],
        "notes": bookmark[3], "creation_date": bookmark[4],
        "last_read_date": bookmark[5], "read_count": bookmark[6],
        "labels": list(bookmark[7]), "related_ids": list(bookmark[8])
    }

def dict_to_bookmark(data):
    """
    Convert a JSON-friendly dict back into a bookmark tuple.

    Args:
        data : dict as produced by bookmark_to_dict

    Returns:
        The corresponding bookmark tuple

    Effects:
        None (pure function).
    """
    return (
        int(data["id"]), data["title"], data["url"], data["notes"],
        data["creation_date"], data["last_read_date"], int(data["read_count"]),
        tuple(data["labels"]), tuple(int(r) for r in data["related_ids"])
    )

def export_json(bookmarks, path):
    """
    Export bookmarks to a JSON file.

    Args:
        bookmarks : list of existing bookmarks
        path : path of the JSON file to write to

    Effects:
        Overwrites path with the JSON-serialized bookmarks.
    """
    with open(path, 'w', encoding='utf-8') as f:
        json.dump([bookmark_to_dict(b) for b in bookmarks], f, indent=2)

def import_json(path):
    """
    Import bookmarks from a JSON file.

    Args:
        path : path of the JSON file to read from

    Returns:
        The list of bookmarks found in path

    Effects:
        Reads path.
    """
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return [dict_to_bookmark(item) for item in data]

def export_csv(bookmarks, path):
    """
    Export bookmarks to a CSV file, with labels and related_ids joined
    by '|' within their cell.

    Args:
        bookmarks : list of existing bookmarks
        path : path of the CSV file to write to

    Effects:
        Overwrites path with the CSV-serialized bookmarks.
    """
    with open(path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(CSV_FIELDS)
        for bookmark in bookmarks:
            writer.writerow([
                bookmark[0], bookmark[1], bookmark[2], bookmark[3], bookmark[4],
                bookmark[5], bookmark[6], "|".join(bookmark[7]),
                "|".join(map(str, bookmark[8]))
            ])

def import_csv(path):
    """
    Import bookmarks from a CSV file produced by export_csv.

    Args:
        path : path of the CSV file to read from

    Returns:
        The list of bookmarks found in path

    Effects:
        Reads path.
    """
    with open(path, 'r', encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        return [
            (
                int(row["id"]), row["title"], row["url"], row["notes"],
                row["creation_date"], row["last_read_date"], int(row["read_count"]),
                tuple(label for label in row["labels"].split("|") if label),
                tuple(int(r) for r in row["related_ids"].split("|") if r)
            )
            for row in reader
        ]

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def to_unix_timestamp(date_string):
    """
    Convert a "%Y-%m-%d %H:%M:%S" date string to a Unix timestamp, as
    used by the Netscape Bookmark File Format's ADD_DATE/LAST_VISIT_DATE
    attributes.

    Args:
        date_string : date in DATE_FORMAT

    Returns:
        The corresponding Unix timestamp, as an int

    Effects:
        None (pure function).
    """
    return int(datetime.strptime(date_string, DATE_FORMAT).timestamp())

def from_unix_timestamp(timestamp):
    """
    Convert a Unix timestamp back to a "%Y-%m-%d %H:%M:%S" date string.

    Args:
        timestamp : Unix timestamp (int or numeric string)

    Returns:
        The corresponding date, formatted as DATE_FORMAT

    Effects:
        None (pure function).
    """
    return datetime.fromtimestamp(int(timestamp)).strftime(DATE_FORMAT)

NETSCAPE_HEADER = (
    "<!DOCTYPE NETSCAPE-Bookmark-file-1>\n"
    "<!-- This is an automatically generated file.\n"
    "     It will be read and overwritten.\n"
    "     DO NOT EDIT! -->\n"
    "<META HTTP-EQUIV=\"Content-Type\" CONTENT=\"text/html; charset=UTF-8\">\n"
    "<TITLE>Bookmarks</TITLE>\n"
    "<H1>Bookmarks</H1>\n"
    "<DL><p>\n"
)

def export_html(bookmarks, path):
    """
    Export bookmarks to the Netscape Bookmark File Format used by
    Firefox (and Chrome) for bookmark import/export, with labels stored
    as Firefox-compatible TAGS.

    Args:
        bookmarks : list of existing bookmarks
        path : path of the HTML file to write to

    Effects:
        Overwrites path with the HTML-serialized bookmarks.
    """
    lines = [NETSCAPE_HEADER]
    for bookmark in bookmarks:
        add_date = to_unix_timestamp(bookmark[4])
        last_visit_date = to_unix_timestamp(bookmark[5])
        title = html.escape(bookmark[1])
        url = html.escape(bookmark[2], quote=True)
        tags = html.escape(",".join(bookmark[7]), quote=True)
        lines.append(
            f'    <DT><A HREF="{url}" ADD_DATE="{add_date}" '
            f'LAST_VISIT_DATE="{last_visit_date}" TAGS="{tags}">{title}</A>\n'
        )
        if bookmark[3]:
            lines.append(f"    <DD>{html.escape(bookmark[3])}\n")
    lines.append("</DL><p>\n")

    with open(path, 'w', encoding='utf-8') as f:
        f.write("".join(lines))

class NetscapeBookmarkParser(HTMLParser):
    """
    HTML parser collecting every <A> bookmark entry of a Netscape
    Bookmark File Format document (as exported by Firefox/Chrome),
    along with its optional following <DD> description.
    """

    def __init__(self):
        super().__init__()
        self.entries = []
        self._current = None
        self._in_link = False
        self._in_description = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'a':
            self._in_link = True
            self._in_description = False
            self._current = {
                "url": attrs.get("href", ""),
                "title": "",
                "add_date": attrs.get("add_date"),
                "last_visit_date": attrs.get("last_visit_date") or attrs.get("last_modified"),
                "tags": attrs.get("tags", ""),
                "notes": ""
            }
            self.entries.append(self._current)
        elif tag == 'dd':
            self._in_description = True
        elif tag == 'dt':
            self._in_description = False

    def handle_endtag(self, tag):
        if tag == 'a':
            self._in_link = False

    def handle_data(self, data):
        if self._in_link and self._current is not None:
            self._current["title"] += data
        elif self._in_description and self._current is not None:
            self._current["notes"] += data

def entry_to_bookmark(new_id, entry):
    """
    Convert a parsed Netscape bookmark entry into a bookmark tuple.

    Args:
        new_id : id to assign to the bookmark
        entry : dict as collected by NetscapeBookmarkParser (url, title,
            add_date, last_visit_date, tags, notes)

    Returns:
        The corresponding bookmark tuple, with read_count and
        related_ids left at 0/empty (not represented in this format)

    Effects:
        None (pure function).
    """
    now = datetime.now().strftime(DATE_FORMAT)
    creation_date = from_unix_timestamp(entry["add_date"]) if entry["add_date"] else now
    last_read_date = (
        from_unix_timestamp(entry["last_visit_date"]) if entry["last_visit_date"]
        else creation_date
    )
    labels = tuple(label.strip() for label in entry["tags"].split(",") if label.strip())
    title = entry["title"].strip() or entry["url"]

    return (
        new_id, title, entry["url"], entry["notes"].strip(), creation_date,
        last_read_date, 0, labels, ()
    )

def export_markdown(bookmarks, path):
    """
    Export bookmarks to a Markdown list.

    Args:
        bookmarks : list of existing bookmarks
        path : path of the Markdown file to write to

    Constraints:
        Export-only: dates, read counts and related_ids are not
        reliably recoverable from a Markdown list, so this format has
        no matching import.

    Effects:
        Overwrites path with the Markdown-serialized bookmarks.
    """
    lines = ["# Bookmarks\n\n"]
    for bookmark in bookmarks:
        labels = f" _{', '.join(bookmark[7])}_" if bookmark[7] else ""
        notes = f" — {bookmark[3]}" if bookmark[3] else ""
        lines.append(f"- [{bookmark[1]}]({bookmark[2]}){labels}{notes}\n")

    with open(path, 'w', encoding='utf-8') as f:
        f.write("".join(lines))

def import_html(path):
    """
    Import bookmarks from a Netscape Bookmark File Format file (as
    exported by Firefox/Chrome).

    Args:
        path : path of the HTML file to read from

    Returns:
        The list of bookmarks found in path, with sequential ids

    Effects:
        Reads path.
    """
    parser = NetscapeBookmarkParser()
    with open(path, 'r', encoding='utf-8') as f:
        parser.feed(f.read())

    return [
        entry_to_bookmark(new_id, entry)
        for new_id, entry in enumerate(
            (entry for entry in parser.entries if entry["url"]), start=1
        )
    ]

EXPORTERS = {
    "json": export_json, "csv": export_csv, "html": export_html,
    "markdown": export_markdown
}
IMPORTERS = {"json": import_json, "csv": import_csv, "html": import_html}

def export_bookmarks(bookmarks, fmt, path):
    """
    Export bookmarks to a file in the given format.

    Args:
        bookmarks : list of existing bookmarks
        fmt : "json", "csv", "html" (Firefox/Chrome-compatible Netscape
            Bookmark File Format) or "markdown"
        path : path of the file to write to

    Effects:
        Overwrites path with the serialized bookmarks.
    """
    EXPORTERS[fmt](bookmarks, path)

def import_bookmarks(fmt, path):
    """
    Import bookmarks from a file in the given format.

    Args:
        fmt : "json", "csv" or "html" (Firefox/Chrome-compatible
            Netscape Bookmark File Format); "markdown" is export-only
        path : path of the file to read from

    Returns:
        The list of bookmarks found in path

    Effects:
        Reads path.
    """
    return IMPORTERS[fmt](path)
