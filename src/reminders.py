'''
Reading reminder and reading time estimation, both driven by the
configuration's reminder threshold and reading speed heuristics.
'''

from datetime import datetime

def is_stale(bookmark, config):
    """
    Check whether a bookmark has not been read recently enough and should
    be highlighted as a reading reminder.

    Args:
        bookmark : bookmark tuple, using last_read_date at index 5
        config : configuration dict, using config['reading_reminder_days']

    Returns:
        True if the bookmark's last-read date is at least
        config['reading_reminder_days'] days in the past

    Effects:
        None (pure function).
    """
    last_read_date = datetime.strptime(bookmark[5], "%Y-%m-%d %H:%M:%S")
    age_days = (datetime.now() - last_read_date).days
    return age_days >= config["reading_reminder_days"]

def estimate_reading_minutes(bookmark, config):
    """
    Estimate how long it takes to read a bookmark, in minutes.

    Args:
        bookmark : bookmark tuple, using notes at index 3
        config : configuration dict, using config['reading_speed_wpm'] and
            config['default_reading_words'] (used when notes are empty, as
            a stand-in for the linked page's assumed length)

    Returns:
        The estimated reading time in whole minutes, at least 1

    Effects:
        None (pure function).
    """
    notes_word_count = len(bookmark[3].split())
    word_count = notes_word_count if notes_word_count else config["default_reading_words"]
    return max(1, round(word_count / config["reading_speed_wpm"]))
