'''
Reading statistics: aggregate metrics about a bookmarks collection.
'''

from src.search import domain_of

def compute_stats(bookmarks):
    """
    Compute aggregate reading statistics over a list of bookmarks.

    Args:
        bookmarks : list of existing bookmarks

    Returns:
        A dict with keys:
        - total_bookmarks : number of bookmarks
        - total_reads : sum of every bookmark's read_count
        - avg_reads : total_reads / total_bookmarks (0 if there are none)
        - reads_by_domain : dict {domain: summed read_count}
        - reads_by_label : dict {label: summed read_count}
        - most_read : the bookmark with the highest read_count, or None
        - least_recently_read : the bookmark with the oldest
          last_read_date, or None

    Effects:
        None (pure function).
    """
    if not bookmarks:
        return {
            "total_bookmarks": 0, "total_reads": 0, "avg_reads": 0,
            "reads_by_domain": {}, "reads_by_label": {},
            "most_read": None, "least_recently_read": None
        }

    reads_by_domain = {}
    reads_by_label = {}
    for bookmark in bookmarks:
        domain = domain_of(bookmark)
        reads_by_domain[domain] = reads_by_domain.get(domain, 0) + bookmark[6]
        for label in bookmark[7]:
            reads_by_label[label] = reads_by_label.get(label, 0) + bookmark[6]

    total_reads = sum(bookmark[6] for bookmark in bookmarks)

    return {
        "total_bookmarks": len(bookmarks),
        "total_reads": total_reads,
        "avg_reads": total_reads / len(bookmarks),
        "reads_by_domain": reads_by_domain,
        "reads_by_label": reads_by_label,
        "most_read": max(bookmarks, key=lambda b: b[6]),
        "least_recently_read": min(bookmarks, key=lambda b: b[5])
    }

def print_stats(bookmarks):
    """
    Compute and print reading statistics about a bookmarks collection.

    Args:
        bookmarks : list of existing bookmarks

    Effects:
        Prints the statistics report to stdout.
    """
    stats = compute_stats(bookmarks)

    if stats["total_bookmarks"] == 0:
        print("No bookmarks yet.")
        return

    print(f"Total bookmarks: {stats['total_bookmarks']}")
    print(f"Total reads: {stats['total_reads']}")
    print(f"Average reads per bookmark: {stats['avg_reads']:.2f}")

    print("Reads by domain:")
    for domain, reads in sorted(stats["reads_by_domain"].items(), key=lambda item: -item[1]):
        print(f"  {domain}: {reads}")

    print("Reads by label:")
    if stats["reads_by_label"]:
        for label, reads in sorted(stats["reads_by_label"].items(), key=lambda item: -item[1]):
            print(f"  {label}: {reads}")
    else:
        print("  (no labels)")

    print(f"Most read: [{stats['most_read'][0]}] {stats['most_read'][1]}"
          f" ({stats['most_read'][6]} reads)")
    print(f"Least recently read: [{stats['least_recently_read'][0]}]"
          f" {stats['least_recently_read'][1]}"
          f" (last read {stats['least_recently_read'][5]})")
