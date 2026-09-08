import commands
from options import create_parser

# Create command line parser
options = create_parser().parse_args()

try:
    # Read bookmarks file, if it exists
    with open(options.file, 'r') as f:
        bookmarks = f.readlines()

    # Details
    title = options.t if options.t else ""
    notes = options.n if options.n else ""
    target = options.u if options.u else ""
    details = ",".join([title, notes, target])

    # Run the command
    if options.command == 'add':
        commands.add(details, options.file, bookmarks)
    elif options.command == 'modify':
        commands.modify(options.id, details, options.file, bookmarks)
    elif options.command == 'rm':
        commands.rm(options.id, options.file, bookmarks)
    elif options.command == 'show':
        commands.show(bookmarks)

except FileNotFoundError:
    print(f"The file {options.file} was not found")
