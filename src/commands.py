'''
Command handlers bridging the CLI options to the core bookmark operations.
'''

from src import compliance, core, io_formats, search as search_module, stats as stats_module
from src import related as related_module, synthesis, tree as tree_module
from src import utils
from src.options import create_parser

def add(details, filename, bookmarks):
    '''
    Add a new bookmark to the file if its url is not already present.

    Args:
        details : tuple (title, url, notes, labels) describing the new bookmark
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

def read(bookmark_id, filename, bookmarks, config) :
    '''
    Display a bookmark and record that it was read (last-read date and read count).

    Args:
        bookmark_id : bookmark_id of the bookmark to read
        filename : path of the bookmarks file to write to
        bookmarks : list of existing bookmarks
        config : configuration dict, used to render the reminder/reading
            time columns

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

    core.show([core.find(updated_bookmarks, bookmark_id)], config)


def modify(bookmark_id, details, filename, bookmarks):
    '''
    Modify an existing bookmark if the new url is not already used by another one.

    Args:
        bookmark_id : bookmark_id of the bookmark to modify
        details : new tuple (title, url, notes, labels) to describe the bookmark
        filename : path of the bookmarks file to write to
        bookmarks : list of existing bookmarks

    Effects:
        Prints an empty line and returns without writing if the url is
        already used by another bookmark, or if no bookmark matches
        bookmark_id; otherwise rewrites filename with the modified bookmark.
    '''
    # Verification (the bookmark being modified is excluded, so keeping
    # its own current url is not mistaken for a duplicate)
    other_bookmarks = [b for b in bookmarks if b[0] != bookmark_id]
    url_already_added = utils.url_duplicate_detection(details, other_bookmarks)
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
        matches bookmark_id; otherwise rewrites filename without it, also
        removing bookmark_id from every remaining bookmark's related_ids.
    '''

    # Check if the bookmark exist
    bookmark = core.find(bookmarks, bookmark_id)
    if not bookmark :
        print("")
        return

    # Update bookmarks
    updated_bookmarks = core.rm(bookmarks, bookmark_id)
    utils.write_bookmarks(filename, 'w', updated_bookmarks)

def show(bookmarks, config):
    '''
    Display the bookmarks.

    Args:
        bookmarks : list of existing bookmarks
        config : configuration dict, used to render the reminder/reading
            time columns

    Effects:
        Prints the bookmarks table to stdout.
    '''
    core.show(bookmarks, config)

def search(bookmarks, config, filters):
    '''
    Search, filter and sort bookmarks, then display the results.

    Args:
        bookmarks : list of existing bookmarks
        config : configuration dict, used to render the reminder/reading
            time columns
        filters : dict with keys "query", "label", "domain" (see
            search.matches), "sort_by" and "descending" (see
            search.sort_bookmarks)

    Effects:
        Prints the matching bookmarks table to stdout.
    '''
    filtered = search_module.filter_bookmarks(
        bookmarks, filters["query"], filters["label"], filters["domain"]
    )
    sorted_bookmarks = search_module.sort_bookmarks(
        filtered, filters["sort_by"], filters["descending"]
    )
    rows = [core.bookmark_row(b, config) for b in sorted_bookmarks]
    core.render_table(core.BOOKMARK_TABLE_HEADER, rows)

def stats(bookmarks):
    '''
    Display reading statistics about the bookmarks.

    Args:
        bookmarks : list of existing bookmarks

    Effects:
        Prints the statistics report to stdout.
    '''
    stats_module.print_stats(bookmarks)

def tree(bookmarks, config, by):
    '''
    Display the bookmarks grouped in a tree view.

    Args:
        bookmarks : list of existing bookmarks
        config : configuration dict, used to resolve label categories
        by : "category" or "domain"

    Effects:
        Prints the tree to stdout.
    '''
    tree_module.print_tree(bookmarks, config, by)

def check(lines):
    '''
    Check a bookmarks file's raw lines for compliance issues.

    Args:
        lines : lines read from the bookmarks file

    Effects:
        Prints the compliance report to stdout.
    '''
    compliance.print_check(lines)

def related(id1, id2, filename, bookmarks, remove):
    '''
    Link or unlink two bookmarks given their ids.

    Args:
        id1 : bookmark_id of the first bookmark
        id2 : bookmark_id of the second bookmark
        filename : path of the bookmarks file to write to
        bookmarks : list of existing bookmarks
        remove : if True, remove the relation instead of adding it

    Effects:
        Prints an empty line and returns without writing if either id
        does not match an existing bookmark; otherwise rewrites filename
        with the updated relation.
    '''
    updated_bookmarks = core.link(bookmarks, id1, id2, remove)
    if updated_bookmarks == bookmarks :
        print("")
        return

    utils.write_bookmarks(filename, 'w', updated_bookmarks)

def sequence(bookmarks, start_id):
    '''
    Display a recommended reading sequence starting from a bookmark.

    Args:
        bookmarks : list of existing bookmarks
        start_id : bookmark_id to start the sequence from

    Effects:
        Prints an empty line if no bookmark matches start_id; otherwise
        prints the numbered reading sequence to stdout.
    '''
    order = related_module.reading_sequence(bookmarks, start_id)
    if not order :
        print("")
        return

    for position, bookmark in enumerate(order, start=1):
        print(f"{position}. [{bookmark[0]}] {bookmark[1]}")

def export(bookmarks, fmt, output):
    '''
    Export the bookmarks to a file.

    Args:
        bookmarks : list of existing bookmarks
        fmt : "json" or "csv"
        output : path of the file to export to

    Effects:
        Overwrites output with the serialized bookmarks.
    '''
    io_formats.export_bookmarks(bookmarks, fmt, output)

def import_bookmarks(bookmarks, fmt, input_file, filename):
    '''
    Import bookmarks from a file, merging them into the current bookmarks
    file.

    Args:
        bookmarks : list of existing bookmarks
        fmt : "json", "csv" or "html" (Firefox/Chrome bookmarks)
        input_file : path of the file to import from
        filename : path of the bookmarks file to write the merged result to

    Effects:
        Reads input_file and rewrites filename with the bookmarks merged
        with the imported ones (see synthesis.synthesize).
    '''
    imported = io_formats.import_bookmarks(fmt, input_file)
    merged = synthesis.synthesize([bookmarks, imported])
    utils.write_bookmarks(filename, 'w', merged)

def merge(files, output):
    '''
    Merge several bookmarks files into one output file.

    Args:
        files : list of paths of the bookmarks files to merge
        output : path of the file to write the merged result to

    Effects:
        Reads every file in files and overwrites output with the merged
        result (see synthesis.synthesize).
    '''
    bookmark_lists = []
    for file in files:
        with open(file, 'r', encoding='utf-8') as f:
            bookmark_lists.append(utils.parse_bookmarks(f.readlines()))

    merged = synthesis.synthesize(bookmark_lists)
    utils.write_bookmarks(output, 'w', merged)

def show_help():
    '''
    Display the list of available commands and what each of them does.

    Effects:
        Prints the parser's help text, including every command and its
        one-line description, to stdout.
    '''
    create_parser().print_help()
