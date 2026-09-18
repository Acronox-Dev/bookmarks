# Bookmarks

A command line tool to manage a collection of digital bookmarks, developed
for the TAF ILSD codecamp. It implements the base CRUD feature set plus
every extension described in the subject (levels 1 to 4).

## Requirements

- Python 3
- No external dependencies: the program only relies on the standard library

## Usage

```
python main.py <bookmarks_file> [-c config.json] <command> [options]
```

`bookmarks_file` is the path to the file storing the bookmarks. It is
created automatically on first use if it doesn't exist yet. `-c/--config`
optionally points to a JSON configuration file (see
[Configuration](#configuration)); it defaults to `config.json` and is
silently ignored if missing.

Run `python main.py --help` or `python main.py <file> <command> --help`
for the full list of options for each command.

## Core commands (level 1)

### Add a bookmark

```
python main.py bookmarks.txt add -t "Linux archives" -u "https://lore.kernel.org" -n "Check every week" -l "dev,linux"
```

- `-t` title (defaults to "no title", truncated to 64 characters)
- `-u` URL (defaults to "no url"; must be a valid http/https URL)
- `-n` notes (defaults to "no notes")
- `-l` comma-separated labels (extension 1.b); any label matched by a
  configured URL rule is added automatically on top of these (extension 3.a)

Adding is refused, without writing, if the URL is already used by another
bookmark (extension 1.a, duplicate detection).

### Show all bookmarks

```
python main.py bookmarks.txt show
```

Prints every bookmark, sorted by id, including its labels, related
bookmark ids, a reading reminder marker (extension 2.c) and an estimated
reading time (extension 4.a).

### Read a bookmark

```
python main.py bookmarks.txt read 1
```

Displays the bookmark with id `1` and updates its last-read date and read
count (extensions 1.c/1.d).

### Modify a bookmark

```
python main.py bookmarks.txt modify 1 -t "New title" -u "https://example.com" -n "Updated notes" -l "dev"
```

### Remove a bookmark

```
python main.py bookmarks.txt rm 1
```

Also removes the bookmark from every other bookmark's related ids.

## Extension commands

### search — search, filter and sort (3.d)

```
python main.py bookmarks.txt search -q kernel -l dev -d kernel.org --sort read_count --desc
```

- `-q` text to search in the title and notes
- `-l` only keep bookmarks with this label
- `-d` only keep bookmarks with this URL domain
- `--sort` one of `id`, `title`, `read_count`, `creation_date`,
  `last_read_date` (default `id`)
- `--desc` sort in descending order

### stats — reading statistics (3.b)

```
python main.py bookmarks.txt stats
```

Prints total bookmarks/reads, average reads per bookmark, reads by domain,
reads by label, the most-read bookmark and the least-recently-read one.

### tree — tree view (4.b)

```
python main.py bookmarks.txt tree --by category
python main.py bookmarks.txt tree --by domain
```

`--by category` (default) groups bookmarks by root category → category →
label, using the `label_categories`/`category_parents` configuration
(extension 3.c). `--by domain` groups them by URL domain.

### check — compliance checks (3.e)

```
python main.py bookmarks.txt check
```

Validates the raw file (field count, id uniqueness, title length, URL
validity, date format, read count) without requiring it to already be
parseable, so it can diagnose a broken file.

### related / sequence — related bookmarks (4.c)

```
python main.py bookmarks.txt related 1 2
python main.py bookmarks.txt related 1 2 --remove
python main.py bookmarks.txt sequence 1
```

`related` links (or with `--remove`, unlinks) two bookmarks bidirectionally.
`sequence` recommends a reading order by traversing the graph of related
bookmarks breadth-first, starting from the given id.

### export / import — import/export formats (2.d, 4.e)

```
python main.py bookmarks.txt export json backup.json
python main.py bookmarks.txt export csv backup.csv
python main.py other.txt import json backup.json
```

Supported formats: `json` and `csv`. `import` merges the file's content
into the current bookmarks file the same way `merge` does (deduplicating
by URL, see below), and writes the result back to it.

### merge — file synthesis (4.d)

```
python main.py bookmarks.txt merge file1.txt file2.txt -o merged.txt
```

Combines several bookmarks files into `-o/--output`: bookmarks are
renumbered sequentially in first-seen order, and bookmarks sharing a URL
across files are merged into one (union of labels, the higher read count,
the earliest creation date, the most recent last-read date). Related ids
are cleared on the result, since they can't be reliably reconciled across
different files' id spaces.

## Configuration

An optional JSON file (`config.json` by default, or the path given with
`-c/--config`) configures the extensions below. Any key left out falls
back to its default; a missing or invalid file falls back entirely to
these defaults:

```json
{
  "log_file": "bookmarks.log",
  "reading_reminder_days": 30,
  "reading_speed_wpm": 200,
  "default_reading_words": 200,
  "url_label_rules": { "github.com": "dev", "youtube.com": "video" },
  "label_categories": { "dev": "tech", "video": "media" },
  "category_parents": { "tech": "interests", "media": "interests" }
}
```

- `log_file` — where every action is logged (extension 2.a)
- `reading_reminder_days` — a bookmark not read for at least this many
  days is flagged in `show`/`search` (extension 2.c)
- `reading_speed_wpm`, `default_reading_words` — used to estimate reading
  time from the notes' word count, or `default_reading_words` when notes
  are empty (extension 4.a)
- `url_label_rules` — `{url substring: label}`, applied automatically when
  adding a bookmark (extension 3.a)
- `label_categories`, `category_parents` — group labels into categories,
  themselves optionally nested under a parent category, used by `tree`
  and available to `stats` (extension 3.c)

## Log management (2.a)

Every command run is appended to `log_file` as
`timestamp; command; key=value, ...`, including failed attempts (e.g. an
invalid URL on `add`).

## Bookmark file format

Bookmarks are stored as plain text, one bookmark per line:

```
id; title; url; notes; creation_date; last_read_date; read_count; labels; related_ids
```

`labels` and `related_ids` are comma-separated (empty if none).

## Project structure

```
main.py                Entry point: builds the dispatch table and logs each command
src/options.py          Command line argument parser (argparse)
src/commands.py         Command handlers, bridging the CLI to the modules below
src/core.py             Core operations on the in-memory bookmark list (add/modify/rm/find/link/show)
src/utils.py            Validation, formatting, parsing and file I/O helpers
src/config.py           Configuration loading (2.b)
src/logger.py           Action logging (2.a)
src/labels.py           URL-based label classification (3.a) and label categories (3.c)
src/reminders.py        Reading reminder (2.c) and reading time estimate (4.a)
src/search.py           Search, filter and sort (3.d)
src/stats.py            Reading statistics (3.b)
src/tree.py             Tree view (4.b)
src/related.py          Reading sequence traversal (4.c)
src/compliance.py       File compliance checks (3.e)
src/io_formats.py       JSON/CSV export and import (2.d, 4.e)
src/synthesis.py        File merging/deduplication, shared by merge and import (4.d)
src/exceptions.py       Custom exceptions
tests/                  Unit tests (one file per src module, plus command-level integration tests)
```

## Running the tests

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
