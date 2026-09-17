from src.exceptions import InvalidURLError
from src.options import create_parser
import src.utils as utils

options = create_parser().parse_args()

try:
    with open(options.file, 'r') as f:
        bookmarks = f.readlines()

    utils.do_commands(options, bookmarks)

except FileNotFoundError:
    with open(options.file, 'w') as f:
        pass

    utils.do_commands(options, [])

except InvalidURLError:
    print(f"Error : This url is not valid or doesn't exist")