'''
Main file to use the bookmarks software
'''

from src.options import create_parser
from src import commands, utils
from src.exceptions import InvalidURLError

def do_commands(options, bookmarks) :
    """
    Dispatch the parsed command line options to the corresponding command.

    Args:
        options : parsed command line options (command, id, t, u, n, file)
        bookmarks : list of existing bookmarks

    Returns:
        None. The dispatched command handles its own output and file writes.

    Raises:
        InvalidURLError: if the provided url is not valid.

    Effects:
        May write to options.file and print to stdout, depending on the
        dispatched command.
    """
    if options.command in ['add', 'modify'] :
        title = utils.format_title(options.t[:64] if options.t else "")
        url = utils.format_url(options.u if options.u else "")
        notes = options.n if options.n else ""

        if not utils.is_url_valid(url):
            raise InvalidURLError

        details = (title, url, notes)

        if options.command == 'add' :
            commands.add(details, options.file, bookmarks)
        else :
            commands.modify(options.id, details, options.file, bookmarks)

    elif options.command == 'read':
        commands.read(options.id, options.file, bookmarks)

    elif options.command == 'rm':
        commands.rm(options.id, options.file, bookmarks)

    elif options.command == 'show':
        commands.show(bookmarks)

def main():
    """
    Entry point: parse the command line options, validate their types, load
    the bookmarks file and dispatch the requested command.

    Effects:
        Reads options.file (creating it if missing) and, depending on the
        dispatched command, writes to it and/or prints to stdout.
    """
    options = create_parser().parse_args()

    if not utils.validate_option_types(options):
        return

    try:
        with open(options.file, 'r', encoding='utf-8') as f:
            bookmarks = utils.parse_bookmarks(f.readlines())

        do_commands(options, bookmarks)

    except FileNotFoundError:
        with open(options.file, 'w', encoding='utf-8') as f:
            pass

        do_commands(options, [])

    except InvalidURLError:
        print("Error : This url is not valid or doesn't exist")

if __name__ == "__main__":
    main()
