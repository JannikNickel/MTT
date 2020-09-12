import math

def number_importance(num):
    if num == 1:
        return "Primary"
    elif num == 2:
        return "Secondary"
    elif num == 3:
        return "Tertiary"
    return ""

def number_ordinal(num):
    return "%s" % ("tsnrhtdd"[(math.floor(num / 10) % 10 != 1)  *(num % 10 < 4) * num % 10::4])
