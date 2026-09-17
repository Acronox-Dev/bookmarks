import src.commands as commands
from src.exceptions import InvalidURLError
from src.options import create_parser
import src.utils as utils

def do_commands(options, bookmarks) :
    if options.command == 'add':
        title = options.t[:64] if options.t else ""
        url = options.u if options.u else ""
        notes = options.n if options.n else ""
    
        if not utils.is_url_valid(url):
            raise InvalidURLError
    
        details = "; ".join([title, url, notes])
            
        commands.add(details, options.file, bookmarks)
    
    elif options.command == 'modify':
        title = options.t[:64] if options.t else ""
        url = options.u if options.u else ""
        notes = options.n if options.n else ""
            
        if not utils.isURLvalid(url):
            raise InvalidURLError
            
        details = "; ".join([title, url, notes])
            
        commands.modify(options.id, details, options.file, bookmarks)
    
    elif options.command == 'rm':
        commands.rm(options.id, options.file, bookmarks)
    
    elif options.command == 'show':
        commands.show(bookmarks)


options = create_parser().parse_args()

try:
    with open(options.file, 'r') as f:
        bookmarks = f.readlines()

    do_commands(options, bookmarks)

except FileNotFoundError:
    with open(options.file, 'w') as f:
        pass

    do_commands(options, [])

except InvalidURLError:
    print(f"Error : This url is not valid or doesn't exist")