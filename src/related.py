'''
Related bookmarks: recommend a reading sequence by traversing the graph
of related_ids starting from a given bookmark.
'''

from collections import deque

def reading_sequence(bookmarks, start_id):
    """
    Build a recommended reading sequence starting from a bookmark,
    following related_ids breadth-first.

    Args:
        bookmarks : list of existing bookmarks
        start_id : bookmark_id to start the sequence from

    Returns:
        List of bookmarks in visiting order, starting with the bookmark
        matching start_id, followed by every bookmark reachable through
        related_ids (each bookmark visited at most once); an empty list
        if no bookmark matches start_id

    Effects:
        None (pure function).
    """
    index = {bookmark[0]: bookmark for bookmark in bookmarks}
    start = index.get(start_id)
    if start is None:
        return []

    visited = {start_id}
    order = [start]
    queue = deque(start[8])

    while queue:
        current_id = queue.popleft()
        if current_id in visited:
            continue
        visited.add(current_id)
        bookmark = index.get(current_id)
        if bookmark is None:
            continue
        order.append(bookmark)
        queue.extend(related_id for related_id in bookmark[8] if related_id not in visited)

    return order
