'''
Export and import bookmarks to/from JSON or CSV files.
'''

import csv
import json

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

EXPORTERS = {"json": export_json, "csv": export_csv}
IMPORTERS = {"json": import_json, "csv": import_csv}

def export_bookmarks(bookmarks, fmt, path):
    """
    Export bookmarks to a file in the given format.

    Args:
        bookmarks : list of existing bookmarks
        fmt : "json" or "csv"
        path : path of the file to write to

    Effects:
        Overwrites path with the serialized bookmarks.
    """
    EXPORTERS[fmt](bookmarks, path)

def import_bookmarks(fmt, path):
    """
    Import bookmarks from a file in the given format.

    Args:
        fmt : "json" or "csv"
        path : path of the file to read from

    Returns:
        The list of bookmarks found in path

    Effects:
        Reads path.
    """
    return IMPORTERS[fmt](path)
