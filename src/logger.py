'''
Log management: record every action performed with the program to a log
file, so the history of what was done can be reviewed later.
'''

from datetime import datetime

def log_action(config, command, detail):
    """
    Append a timestamped entry describing an action to the configured log file.

    Args:
        config : configuration dict, as returned by config.load_config,
            using config['log_file'] as the destination path
        command : name of the command that was run (e.g. "add", "rm")
        detail : short human-readable description of the action's arguments

    Effects:
        Appends one line to config['log_file'], creating it if missing.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(config["log_file"], 'a', encoding='utf-8') as f:
        f.write(f"{timestamp}; {command}; {detail}\n")
