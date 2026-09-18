'''
Compliance checks: validate a bookmarks file's raw lines for structural
and content integrity issues, without relying on utils.parse_bookmarks
(which would raise on the very lines this module is meant to catch).
'''

from datetime import datetime

from src.utils import is_url_valid

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def check_id(line_number, bookmark_id, seen_ids):
    """
    Validate a line's id field.

    Args:
        line_number : 1-based line number, used in the reported issues
        bookmark_id : the raw id field
        seen_ids : set of bookmark ids already seen in earlier lines

    Returns:
        A tuple (issues, parsed_id): issues is a list of human-readable
        problem descriptions, parsed_id is the int id, or None if it
        could not be parsed

    Effects:
        None (pure function).
    """
    if not bookmark_id.isdigit():
        return ([f"line {line_number}: id '{bookmark_id}' is not a positive integer"], None)
    if int(bookmark_id) in seen_ids:
        return ([f"line {line_number}: duplicate id {bookmark_id}"], int(bookmark_id))
    return ([], int(bookmark_id))

def check_dates(line_number, creation_date, last_read_date):
    """
    Validate a line's creation_date and last_read_date fields.

    Args:
        line_number : 1-based line number, used in the reported issues
        creation_date : the raw creation_date field
        last_read_date : the raw last_read_date field

    Returns:
        A list of human-readable problem descriptions, empty if both
        dates match DATE_FORMAT

    Effects:
        None (pure function).
    """
    issues = []
    for value, name in (("creation_date", creation_date), ("last_read_date", last_read_date)):
        try:
            datetime.strptime(name, DATE_FORMAT)
        except ValueError:
            issues.append(f"line {line_number}: {value} '{name}' does not match "
                           f"the '{DATE_FORMAT}' format")
    return issues

def check_line(line_number, raw_line, seen_ids):
    """
    Validate a single raw bookmarks file line.

    Args:
        line_number : 1-based line number, used in the reported issues
        raw_line : the raw line text (without its trailing newline)
        seen_ids : set of bookmark ids already seen in earlier lines,
            used to detect duplicates; not mutated by this function

    Returns:
        A tuple (issues, bookmark_id): issues is a list of human-readable
        problem descriptions (empty if the line is fully compliant),
        bookmark_id is the parsed id (or None if it could not be parsed),
        for the caller to add to seen_ids

    Effects:
        None (pure function).
    """
    fields = [field.strip() for field in raw_line.split(";", 8)]

    if len(fields) != 9:
        return ([f"line {line_number}: expected 9 fields, got {len(fields)}"], None)

    id_issues, bookmark_id = check_id(line_number, fields[0], seen_ids)

    issues = id_issues + check_dates(line_number, fields[4], fields[5])

    if len(fields[1]) > 64:
        issues.append(f"line {line_number}: title exceeds 64 characters")

    if not is_url_valid(fields[2]):
        issues.append(f"line {line_number}: url '{fields[2]}' is not valid")

    if not fields[6].isdigit():
        issues.append(f"line {line_number}: read_count '{fields[6]}' is not a "
                       "non-negative integer")

    return (issues, bookmark_id)

def check_lines(lines):
    """
    Validate every non-blank line of a bookmarks file.

    Args:
        lines : lines read from a bookmarks file

    Returns:
        A list of human-readable issue descriptions, empty if the file is
        fully compliant

    Effects:
        None (pure function).
    """
    issues = []
    seen_ids = set()
    for line_number, raw_line in enumerate(lines, start=1):
        if not raw_line.strip():
            continue
        line_issues, bookmark_id = check_line(line_number, raw_line.rstrip("\r\n"), seen_ids)
        issues.extend(line_issues)
        if bookmark_id is not None:
            seen_ids.add(bookmark_id)
    return issues

def print_check(lines):
    """
    Validate a bookmarks file's raw lines and print a compliance report.

    Args:
        lines : lines read from a bookmarks file

    Effects:
        Prints one line per issue found, or a confirmation message if
        none were found.
    """
    issues = check_lines(lines)
    if not issues:
        print("No compliance issues found.")
        return
    for issue in issues:
        print(issue)
