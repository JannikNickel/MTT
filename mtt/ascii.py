from .log import log, log_type

def str_to_ascii_array(value: str):
    array = []
    for char in value:
        a = ord(char)
        if a >= 128:#ord works in unicode, which ist equal to ASCII until 128
            a = 33
            log(f"character {char} can not be represented as ASCII number!", log_type.WARNING)
        array.append(a)
    return array