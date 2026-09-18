'''
Command line argument parser for the bookmarks application.
'''

import argparse

def create_parser():
    """
    Build the command line argument parser with its subcommands (add, read,
    modify, rm, show, search, stats, tree, check, related, sequence,
    export, import, merge, help).

    Returns:
        The configured argparse.ArgumentParser instance
    """
    # Create command line parser
    parser = argparse.ArgumentParser(description='Simple bookmark manager')

    # Add a positional argument (the file storing the bookmarks)
    parser.add_argument('file', help='The bookmarks file')
    parser.add_argument(
        '-c', '--config', default='config.json',
        help='Path to the configuration file (default: config.json)'
    )

    # Add a subparser for subcommands
    subparsers = parser.add_subparsers(
        help='The commands to manage bookmarks', dest='command', required=True
    )

    # Create parser for the add command
    parser_add = subparsers.add_parser(
        'add',
        help='Add a new bookmark. The rest of the command line is used for the bookmark '
             'details, the default being "no details".'
    )
    parser_add.add_argument('-t', nargs='?', default="no title", help="the title of the bookmark")
    parser_add.add_argument('-u', nargs='?', default="no url", help="the url of the bookmark")
    parser_add.add_argument('-n', nargs='?', default="no notes", help="the notes of the bookmark")
    parser_add.add_argument(
        '-l', nargs='?', default="", help="comma-separated labels for the bookmark"
    )

    # Create parser for the read command
    parser_read = subparsers.add_parser(
        'read',
        help='Read a bookmark. The rest of the command line is used for the bookmark id'
    )
    parser_read.add_argument('id', help="the bookmark id")

    # Create parser for the modify command
    parser_modify = subparsers.add_parser(
        'modify',
        help='Modify a bookmark given its id. The rest of the command line is used for the '
             'bookmark details, the default being "no details"'
    )
    parser_modify.add_argument('id', help="the bookmark id")
    parser_modify.add_argument(
        '-t', nargs='?', default="no title", help="the new title of the bookmark"
    )
    parser_modify.add_argument(
        '-u', nargs='?', default="no url", help="the new url of the bookmark"
    )
    parser_modify.add_argument(
        '-n', nargs='?', default="no notes", help="the new notes of the bookmark"
    )
    parser_modify.add_argument(
        '-l', nargs='?', default="", help="comma-separated labels for the bookmark"
    )

    # Create parser for the rm command
    parser_rm = subparsers.add_parser('rm', help='Remove a bookmark given its id')
    parser_rm.add_argument('id', help="the bookmark id")

    # Create parser for the show command
    subparsers.add_parser('show', help='Show the bookmarks')

    # Create parser for the search command
    parser_search = subparsers.add_parser(
        'search', help='Search and filter bookmarks by text, label, domain and/or sort them'
    )
    parser_search.add_argument('-q', default=None, help="text to search in the title and notes")
    parser_search.add_argument('-l', default=None, help="only keep bookmarks with this label")
    parser_search.add_argument('-d', default=None, help="only keep bookmarks with this domain")
    parser_search.add_argument(
        '--sort', default='id',
        choices=['id', 'title', 'read_count', 'creation_date', 'last_read_date'],
        help="field to sort the results by (default: id)"
    )
    parser_search.add_argument(
        '--desc', action='store_true', help="sort in descending order"
    )

    # Create parser for the stats command
    subparsers.add_parser('stats', help='Show reading statistics about the bookmarks')

    # Create parser for the tree command
    parser_tree = subparsers.add_parser(
        'tree', help='Show the bookmarks grouped in a tree view'
    )
    parser_tree.add_argument(
        '--by', default='category', choices=['category', 'domain'],
        help="how to group the tree (default: category)"
    )

    # Create parser for the check command
    subparsers.add_parser('check', help='Check the bookmarks file for compliance issues')

    # Create parser for the related command
    parser_related = subparsers.add_parser(
        'related', help='Link or unlink two bookmarks given their ids'
    )
    parser_related.add_argument('id1', help="the first bookmark id")
    parser_related.add_argument('id2', help="the second bookmark id")
    parser_related.add_argument(
        '--remove', action='store_true', help="remove the relation instead of adding it"
    )

    # Create parser for the sequence command
    parser_sequence = subparsers.add_parser(
        'sequence', help='Recommend a reading sequence starting from a bookmark'
    )
    parser_sequence.add_argument('id', help="the bookmark id to start from")

    # Create parser for the export command
    parser_export = subparsers.add_parser(
        'export',
        help='Export the bookmarks to a file (json, csv, html for Firefox/Chrome, or markdown)'
    )
    parser_export.add_argument(
        'format', choices=['json', 'csv', 'html', 'markdown'], help="the export format"
    )
    parser_export.add_argument('output', help="the file to export to")

    # Create parser for the import command
    parser_import = subparsers.add_parser(
        'import',
        help='Import bookmarks from a file into the bookmarks file (json, csv, or html '
             'from Firefox/Chrome)'
    )
    parser_import.add_argument('format', choices=['json', 'csv', 'html'], help="the import format")
    parser_import.add_argument('input', help="the file to import from")

    # Create parser for the merge command
    parser_merge = subparsers.add_parser(
        'merge', help='Merge several bookmarks files together'
    )
    parser_merge.add_argument('files', nargs='+', help="the bookmarks files to merge")
    parser_merge.add_argument('-o', '--output', required=True, help="the merged output file")

    # Create parser for the help command
    subparsers.add_parser('help', help='Show what each command does')

    return parser
