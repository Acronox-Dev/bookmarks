# Bookmarks

A simple command line tool to manage a collection of digital bookmarks,
developed for the TAF ILSD codecamp.

## Features

- **add** a bookmark (title, URL, notes), with an id assigned automatically
- **read** a bookmark by id, displaying it and recording that it was read
- **modify** an existing bookmark by id
- **rm** (remove) a bookmark by id
- **show** all bookmarks, sorted by id, in a formatted table
- **Duplicate detection**: adding or modifying a bookmark is refused if the
  URL is already used by another bookmark
- **Date tracking**: each bookmark keeps its creation date and the date it
  was last read
- **Read count**: each bookmark tracks how many times it has been read

## Requirements

- Python 3
- No external dependencies: the program only relies on the standard library

## Usage

```
python main.py <bookmarks_file> <command> [options]
```

`bookmarks_file` is the path to the file storing the bookmarks. It is
created automatically on first use if it doesn't exist yet.

Run `python main.py --help` or `python main.py <command> --help` for the
full list of options for each command.

### Add a bookmark

```
python main.py bookmarks.txt add -t "Linux archives" -u "https://lore.kernel.org" -n "Check every week"
```

- `-t` title (defaults to "no title", truncated to 64 characters)
- `-u` URL (defaults to "no url"; must be a valid http/https URL)
- `-n` notes (defaults to "no notes")

### Show all bookmarks

```
python main.py bookmarks.txt show
```

### Read a bookmark

```
python main.py bookmarks.txt read 1
```

Displays the bookmark with id `1` and updates its last-read date and read
count.

### Modify a bookmark

```
python main.py bookmarks.txt modify 1 -t "New title" -u "https://example.com" -n "Updated notes"
```

### Remove a bookmark

```
python main.py bookmarks.txt rm 1
```

## Bookmark file format

Bookmarks are stored as plain text, one bookmark per line:

```
id; title; url; notes; creation_date; last_read_date; read_count
```

## Project structure

```
main.py             Entry point: dispatches CLI commands
src/options.py       Command line argument parser (argparse)
src/commands.py      Command handlers, bridging the CLI to core/utils
src/core.py          Core operations on the in-memory bookmark list
src/utils.py         Validation, formatting, parsing and file I/O helpers
src/exceptions.py     Custom exceptions
tests/               Unit tests
```

## Running the tests

Unit tests live in the `tests/` directory and cover `src/core.py`,
`src/utils.py` and `src/commands.py`.

```
python -m unittest discover -s tests
```

or, if pytest is installed:

```
python -m pytest tests
```

## Code quality

The codebase is checked with pylint:

```
python -m pylint main.py src/ tests/
```
