import src.core as core

def add(details, filename, bookmarks):
    # URL Duplicate detection
    if details.split(";")[1] in [b.split(";")[1] for b in bookmarks] :
        print("This URL has alreay been added")
        return

    # Add the bookmark otherwise
    with open(filename, 'a') as f:
        bookmark = core.add(bookmarks, details)
        id = bookmark.split(";")[0]
        f.write(bookmark)
    return id

def modify(id, details, filename, bookmarks):
    # URL Duplicate detection
    if details.split(";")[1] in [b.split(";")[1] for b in bookmarks] :
        print("This URL has alreay been added")
        return

    # Update the bookmark otherwise
    updated_bookmarks = core.modify(bookmarks, id, details)
    with open(filename, 'w') as f:
        content = "".join(updated_bookmarks)
        f.write(content)

def rm(id, filename, bookmarks) :
    updated_bookmarks = core.rm(bookmarks, id)
    with open(filename, 'w') as f:
        content = "".join(updated_bookmarks)
        f.write(content)

def show(bookmarks):
    core.show(bookmarks)