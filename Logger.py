from tkinter import Label

# special color codes
GREEN = '\u001b[32m'
YELLOW = '\u001b[33m'
RED = '\u001b[31m'
RESET = '\u001b[0m'


def print_info(info_message):
    """Print the given string to the console with "[INFO]  " prefixed

    Parameters:
        info_message (String): The string to print to console
    """

    print('[INFO]  ' + info_message)


def print_warn(warn_message):
    """Print the given string to the console with a yellow "[WARN]  " prefixed

    Parameters:
        warn_message (String): The string to print to console
    """

    print(YELLOW + '[WARN]  ' + RESET + warn_message)


def print_error(error_message):
    """Print the given string to the console with a red "[ERROR] " prefixed

    Parameters:
        error_message (String): The string to print to console
    """

    print(RED + '[ERROR] ' + RESET + error_message)


def print_info_label(info_message, info_label):
    """Print the given string to the console with "[INFO]  " prefixed

    Parameters:
        info_message (String): The string to print to console
        info_label (Label): The label to update with the given info_message
    """

    print('[INFO]  ' + info_message)
    info_label.config(text='[INFO]  ' + info_message)


def print_warn_label(warn_message, warn_label):
    """Print the given string to the console with a yellow "[WARN]  " prefixed

    Parameters:
        warn_message (String): The string to print to console
        warn_label (Label): The label to update with the given warn_message

    """

    print(YELLOW + '[WARN]  ' + RESET + warn_message)
    warn_label.config(text='[WARN]  ' + warn_message)


def print_error_label(error_message, error_label):
    """Print the given string to the console with a red "[ERROR] " prefixed

    Parameters:
        error_message (String): The string to print to console
        error_label (Label): The label to update with the given error_message

    """

    print(RED + '[ERROR] ' + RESET + error_message)
    error_label.config(text='[ERROR] ' + error_message)
