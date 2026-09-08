import core

def add(details, filename, bookmarks):
    with open(filename, 'a') as f:
        bookmark = core.add(bookmarks, details)
        id = bookmark.split(",")[0]
        content = "".join(bookmarks + [bookmark])
        f.write(content)
    return id

def modify(id, details, filename, bookmarks):
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