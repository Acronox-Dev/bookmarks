'''
Command handlers bridging the CLI options to the core bookmark operations.
'''

from src import core, utils

def add(details, filename, bookmarks):
    '''
    Add a new bookmark to the file if its url is not already present.

    Args:
        details : Array values to describe the bookmark
        filename : path of the bookmarks file to write to
        bookmarks : list of existing bookmarks
    '''

    # Verification
    already_added = utils.url_duplicate_detection(details, bookmarks)
    if already_added :
        print("")
        return

    # Add the bookmark otherwise
    with open(filename, 'a', encoding='utf-8') as f:
        bookmark = core.add(bookmarks, details)
        bookmark_id = bookmark.split(";")[0]
        f.write(bookmark)

    print(bookmark_id)

def modify(bookmark_id, details, filename, bookmarks):
    '''
    Modify an existing bookmark if the new url is not already used by another one.

    Args:
        bookmark_id : bookmark_id of the bookmark to modify
        details : new array values to describe the bookmark
        filename : path of the bookmarks file to write to
        bookmarks : list of existing bookmarks
    '''

    # Verification
    already_added = utils.url_duplicate_detection(details, bookmarks)
    if already_added :
        print("")
        return

    # Update the bookmark otherwise
    updated_bookmarks, modified = core.modify(bookmarks, bookmark_id, details)

    if modified :
        with open(filename, 'w', encoding='utf-8') as f:
            content = "".join(updated_bookmarks)
            f.write(content)

def rm(bookmark_id, filename, bookmarks) :
    '''
    Remove a bookmark from the file given its bookmark_id.

    Args:
        bookmark_id : bookmark_id of the bookmark to remove
        filename : path of the bookmarks file to write to
        bookmarks : list of existing bookmarks
    '''
    updated_bookmarks, modified = core.rm(bookmarks, bookmark_id)

    if modified :
        with open(filename, 'w', encoding='utf-8') as f:
            content = "".join(updated_bookmarks)
            f.write(content)

def show(bookmarks):
    '''
    Display the bookmarks.

    Args:
        bookmarks : list of existing bookmarks
    '''
    core.show(bookmarks)
