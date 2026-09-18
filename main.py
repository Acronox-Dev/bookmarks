'''
Entry point of the bookmarks manager: parses the command line, loads the
configuration and the bookmarks file, and dispatches to src.commands.
'''

from src.options import create_parser
from src import commands, config, labels, logger, utils
from src.exceptions import InvalidURLError

def describe_options(options):
    """
    Build a short, human-readable description of the options relevant to
    a command, for logging purposes.

    Args:
        options : parsed command line options

    Returns:
        A "key=value, key=value, ..." string built from every option
        attribute except command, file and config.

    Effects:
        None (pure function).
    """
    return ", ".join(
        f"{key}={value}" for key, value in vars(options).items()
        if key not in ("command", "file", "config")
    )

def build_details(options, app_config):
    """
    Build the (title, url, notes, labels) tuple shared by add and modify.

    Args:
        options : parsed command line options (t, u, n, l)
        app_config : configuration dict, used for URL-based label
            classification (see labels.classify)

    Returns:
        Tuple (title, url, notes, labels) ready to pass to commands.add
        or commands.modify

    Raises:
        InvalidURLError: if the provided url is not valid.

    Effects:
        None (pure function).
    """
    title = utils.format_title(options.t[:64] if options.t else "")
    url = utils.format_url(options.u if options.u else "")
    notes = options.n if options.n else ""
    bookmark_labels = utils.format_labels(options.l if options.l else "")

    if not utils.is_url_valid(url):
        raise InvalidURLError

    bookmark_labels = labels.classify(url, bookmark_labels, app_config)
    return (title, url, notes, bookmark_labels)

def do_commands(options, bookmarks, app_config) :
    """
    Dispatch the parsed command line options to the corresponding command.

    Args:
        options : parsed command line options (command, id, t, u, n, l, file)
        bookmarks : list of existing bookmarks
        app_config : configuration dict, as returned by config.load_config

    Returns:
        None. The dispatched command handles its own output and file writes.

    Raises:
        InvalidURLError: if the provided url is not valid.

    Effects:
        May write to options.file and print to stdout, depending on the
        dispatched command.
    """
    handlers = {
        'add': lambda: commands.add(
            build_details(options, app_config), options.file, bookmarks
        ),
        'modify': lambda: commands.modify(
            options.id, build_details(options, app_config), options.file, bookmarks
        ),
        'read': lambda: commands.read(options.id, options.file, bookmarks, app_config),
        'rm': lambda: commands.rm(options.id, options.file, bookmarks),
        'show': lambda: commands.show(bookmarks, app_config),
        'search': lambda: commands.search(bookmarks, app_config, {
            "query": options.q, "label": options.l, "domain": options.d,
            "sort_by": options.sort, "descending": options.desc
        }),
        'stats': lambda: commands.stats(bookmarks),
        'tree': lambda: commands.tree(bookmarks, app_config, options.by),
        'related': lambda: commands.related(
            options.id1, options.id2, options.file, bookmarks, options.remove
        ),
        'sequence': lambda: commands.sequence(bookmarks, options.id),
        'export': lambda: commands.export(bookmarks, options.format, options.output),
        'import': lambda: commands.import_bookmarks(
            bookmarks, options.format, options.input, options.file
        ),
    }
    handlers[options.command]()

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

    app_config = config.load_config(options.config)

    if options.command == 'check':
        try:
            with open(options.file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except FileNotFoundError:
            lines = []
        commands.check(lines)
        logger.log_action(app_config, options.command, describe_options(options))
        return

    if options.command == 'merge':
        commands.merge(options.files, options.output)
        logger.log_action(app_config, options.command, describe_options(options))
        return

    try:
        with open(options.file, 'r', encoding='utf-8') as f:
            bookmarks = utils.parse_bookmarks(f.readlines())

        do_commands(options, bookmarks, app_config)
        logger.log_action(app_config, options.command, describe_options(options))

    except FileNotFoundError:
        with open(options.file, 'w', encoding='utf-8') as f:
            pass

        do_commands(options, [], app_config)
        logger.log_action(app_config, options.command, describe_options(options))

    except InvalidURLError:
        print("Error : This url is not valid or doesn't exist")
        logger.log_action(app_config, options.command, "failed: invalid url")

if __name__ == "__main__":
    main()
