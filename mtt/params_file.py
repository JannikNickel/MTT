import os
from .log import log_type, log

class params_file:
    def __init__(self):
        self._key_value_pairs = {}

    def __getitem__(self, key):
        return self._key_value_pairs[key]

    def __setitem__(self, key, value):
        self._key_value_pairs[key] = value

    def write_to(self, file_path):
        with open(file_path, "w") as file:
            file.truncate(0)#Clear old contents
            for key, value in self._key_value_pairs.items():
                file.write(str(key) + "=" + str(value) + "\n")

    def load_from(self, file_path):
        self._key_value_pairs.clear()
        with open(file_path, "r") as file:
            for line in file:
                kv = line.split("=")
                if len(kv) != 2 and len(kv) != 0:
                    log(file_path + " contains an invalid key-value pair!", log_type.WARNING)
                    continue
                if len(kv) != 0:
                    self._key_value_pairs[kv[0]] = kv[1]
