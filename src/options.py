'''
Command line argument parser for the bookmarks application.
'''

import argparse

def create_parser():
    """
    Build the command line argument parser with its subcommands (add, modify, rm, show).

    Returns:
        The configured argparse.ArgumentParser instance
    """
    # Create command line parser
    parser = argparse.ArgumentParser(description='Simple bookmark manager')

    # Add a positional argument (the file storing the bookmarks)
    parser.add_argument('file', help='The bookmarks file')

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

    # Create parser for the rm command
    parser_rm = subparsers.add_parser('rm',help='Remove a bookmark given its id')
    parser_rm.add_argument('id', help="the bookmark id")

    # Create parser for the show command
    subparsers.add_parser('show', help='Show the bookmarks')

    return parser
