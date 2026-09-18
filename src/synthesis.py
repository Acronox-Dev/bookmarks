'''
File synthesis: combine several lists of bookmarks into one, renumbering
ids and merging bookmarks that share the same URL.
'''

def merge_duplicate(first, second):
    """
    Merge two bookmarks that share the same URL into one.

    Args:
        first : the bookmark kept so far for this URL (its title and
            notes are kept)
        second : another bookmark sharing the same URL

    Returns:
        A bookmark combining both: the union of their labels, the
        earliest creation_date, the most recent last_read_date, and the
        higher read_count. Its id and related_ids are left as first's,
        since synthesize() overwrites both afterwards.

    Effects:
        None (pure function).
    """
    labels = first[7] + tuple(label for label in second[7] if label not in first[7])
    return (
        first[0], first[1], first[2], first[3],
        min(first[4], second[4]), max(first[5], second[5]),
        max(first[6], second[6]), labels, first[8]
    )

def synthesize(bookmark_lists):
    """
    Combine several lists of bookmarks into one, renumbered and
    deduplicated by URL.

    Args:
        bookmark_lists : list of lists of bookmark tuples (e.g. one list
            per source file)

    Returns:
        A single list of bookmarks with sequential ids (starting at 1, in
        first-seen order across the inputs), one per distinct URL:
        bookmarks sharing a URL are combined with merge_duplicate.

    Constraints:
        related_ids are cleared on the result, since they cannot be
        reliably reconciled across different files' id spaces.

    Effects:
        None (pure function).
    """
    merged_by_url = {}
    url_order = []
    for bookmarks in bookmark_lists:
        for bookmark in bookmarks:
            url = bookmark[2]
            if url in merged_by_url:
                merged_by_url[url] = merge_duplicate(merged_by_url[url], bookmark)
            else:
                merged_by_url[url] = bookmark
                url_order.append(url)

    return [
        (new_id,) + merged_by_url[url][1:8] + ((),)
        for new_id, url in enumerate(url_order, start=1)
    ]
