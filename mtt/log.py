from enum import Enum
from datetime import datetime

class log_type(Enum):
    DEBUG = 0,
    INFO = 1,
    WARNING = 2,
    ERROR = 3

def log(text, type=log_type.INFO):
    text = str(text)
    log = "[" + datetime.now().strftime("%H:%M:%S") + "] "
    if type == log_type.DEBUG:
        log = log + "[DEBUG] " + text
    elif type == log_type.INFO:
        log = log + "[INFO] " + text
    elif type == log_type.WARNING:
        log = "\033[93m" + log + "[WARNING] " + text + "\033[0m"
    elif type == log_type.ERROR:
        log = "\033[91m" + log + "[ERROR] " + text + "\033[0m"

    print(log)

def log_progress_bar(progress, prefix="", suffix="", decimals=1, length=100, fill='█', print_end="\r"):
    percent = ("{0:." + str(decimals) + "f}").format(progress * 100)
    filled_length = int(length * progress)
    bar = fill * filled_length + '-' * (length - filled_length)
    print("\r%s|%s| %s%% %s" % (prefix, bar, percent, suffix), end=print_end)
    if progress >= 1:
        print()
