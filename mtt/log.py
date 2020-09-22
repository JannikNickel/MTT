from enum import Enum
from datetime import datetime

class log_type(Enum):
    DEBUG = 0,
    INFO = 1,
    WARNING = 2,
    ERROR = 3

def get_log_text(text, type):
    l = "[" + datetime.now().strftime("%H:%M:%S") + "] "
    if type == log_type.DEBUG:
        l = l + "[DEBUG] " + text
    elif type == log_type.INFO:
        l = l + "[INFO] " + text
    elif type == log_type.WARNING:
        l = "\033[93m" + l + "[WARNING] " + text + "\033[0m"
    elif type == log_type.ERROR:
        l = "\033[91m" + l + "[ERROR] " + text + "\033[0m"

    return l

def log(text, type=log_type.INFO):
    print(get_log_text(str(text), type))

def log_with_percent(text, progress, type=log_type.INFO, decimals=1, print_end="\r"):
    percent = ("{0:." + str(decimals) + "f}").format(progress * 100)
    t = "%s (%s%%)" % (text, percent)
    print(get_log_text(t, type), end=print_end)
    if progress >= 1:
        print()

def log_progress_bar(progress, prefix="", suffix="", decimals=1, length=100, fill='█', print_end="\r"):
    percent = ("{0:." + str(decimals) + "f}").format(progress * 100)
    filled_length = int(length * progress)
    bar = fill * filled_length + '-' * (length - filled_length)
    print("\r%s|%s| %s%% %s" % (prefix, bar, percent, suffix), end=print_end)
    if progress >= 1:
        print()
