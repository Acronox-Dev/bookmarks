'''
Command handlers bridging the CLI options to the core bookmark operations.
'''

from src import core, utils

def add(details, filename, bookmarks):
    '''
    Add a new bookmark to the file if its url is not already present.

    Args:
        details : tuple (title, url, notes) describing the new bookmark
        filename : path of the bookmarks file to write to
        bookmarks : list of existing bookmarks

    Effects:
        Prints an empty line and returns without writing if the url is
        already used by another bookmark; otherwise appends the new
        bookmark to filename.
    '''
    # Verification
    url_already_added = utils.url_duplicate_detection(details, bookmarks)
    if url_already_added :
        print("")
        return

    # Add the bookmark otherwise
    bookmark = core.add(bookmarks, details)
    utils.write_bookmarks(filename, 'a', [bookmark])

def read(bookmark_id, filename, bookmarks) :
    '''
    Display a bookmark and record that it was read (last-read date and read count).

    Args:
        bookmark_id : bookmark_id of the bookmark to read
        filename : path of the bookmarks file to write to
        bookmarks : list of existing bookmarks

    Effects:
        Prints an empty line and returns without writing if no bookmark
        matches bookmark_id; otherwise rewrites filename with the updated
        last-read date and read count, and prints the bookmark.
    '''
    # Check if the bookmark exist
    bookmark = core.find(bookmarks, bookmark_id)
    if not bookmark :
        print("")
        return

    updated_bookmarks = core.increment_read_count(bookmarks, bookmark_id)
    utils.write_bookmarks(filename, 'w', updated_bookmarks)

    core.show([core.find(updated_bookmarks, bookmark_id)])


def modify(bookmark_id, details, filename, bookmarks):
    '''
    Modify an existing bookmark if the new url is not already used by another one.

    Args:
        bookmark_id : bookmark_id of the bookmark to modify
        details : new tuple (title, url, notes) to describe the bookmark
        filename : path of the bookmarks file to write to
        bookmarks : list of existing bookmarks

    Effects:
        Prints an empty line and returns without writing if the url is
        already used by another bookmark, or if no bookmark matches
        bookmark_id; otherwise rewrites filename with the modified bookmark.
    '''
    # Verification
    url_already_added = utils.url_duplicate_detection(details, bookmarks)
    if url_already_added :
        print("")
        return

    # Check if the bookmark exist
    bookmark = core.find(bookmarks, bookmark_id)
    if not bookmark :
        print("")
        return

    # Update bookmarks
    updated_bookmarks = core.modify(bookmarks, bookmark_id, details)
    utils.write_bookmarks(filename, 'w', updated_bookmarks)

def rm(bookmark_id, filename, bookmarks) :
    '''
    Remove a bookmark from the file given its bookmark_id.

    Args:
        bookmark_id : bookmark_id of the bookmark to remove
        filename : path of the bookmarks file to write to
        bookmarks : list of existing bookmarks

    Effects:
        Prints an empty line and returns without writing if no bookmark
        matches bookmark_id; otherwise rewrites filename without it.
    '''

    # Check if the bookmark exist
    bookmark = core.find(bookmarks, bookmark_id)
    if not bookmark :
        print("")
        return

    # Update bookmarks
    updated_bookmarks = core.rm(bookmarks, bookmark_id)
    utils.write_bookmarks(filename, 'w', updated_bookmarks)

def show(bookmarks):
    '''
    Display the bookmarks.

    Args:
        bookmarks : list of existing bookmarks

    Effects:
        Prints the bookmarks table to stdout.
    '''
    core.show(bookmarks)
