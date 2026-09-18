'''
Configuration management: load the application's settings from a JSON
file, falling back to built-in defaults for anything missing or absent.
'''

import json

DEFAULT_CONFIG = {
    "log_file": "bookmarks.log",
    "reading_reminder_days": 30,
    "reading_speed_wpm": 200,
    "default_reading_words": 200,
    "url_label_rules": {},
    "label_categories": {},
    "category_parents": {}
}

def load_config(path):
    """
    Load the configuration file, merged over the built-in defaults.

    Args:
        path : path to the JSON configuration file

    Returns:
        A dict with every key from DEFAULT_CONFIG, overridden by any
        matching key found in the file at path. If the file is missing or
        is not valid JSON, DEFAULT_CONFIG is returned unchanged.

    Effects:
        Reads path, if it exists.
    """
    config = dict(DEFAULT_CONFIG)
    try:
        with open(path, 'r', encoding='utf-8') as f:
            file_config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return config

    config.update(file_config)
    return config
