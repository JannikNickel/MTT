"""Definitions for merging items from different database sources in the MIMIC-III dataset"""
from enum import Enum

#Unit conversion
def fahrenheit_to_celcius(value):
    return (value - 32) * (5.0 / 9.0)

def inch_to_cm(value):
    return value * 2.54

#Item merge functions
def pain_0_10(pain_str):
    if pain_str == "0":
        return "None"
    elif pain_str == "1":
        return "None to Mild"
    elif pain_str == "2":
        return "Mild"
    elif pain_str == "3":
        return "Mild to Moderate"
    elif pain_str == "4":
        return "Mild to Moderate"
    elif pain_str == "5":
        return "Moderate"
    elif pain_str == "6":
        return "Moderate to Severe"
    elif pain_str == "7":
        return "Moderate to Severe"
    elif pain_str == "8":
        return "Severe"
    elif pain_str == "9":
        return "Severe to Worst"
    elif pain_str == "10":
        return "Worst"
    return "Unable to Score"

def heart_rythm(rythm):
    if rythm.startswith("1st AV ("):
        return "1st Deg AV Block"
    elif rythm.startswith("A Flut ("):
        return "Atrial Flutter"
    elif rythm.startswith("AF ("):
        return "Atrial Fib"
    elif rythm.startswith("JR ("):
        return "Junctional"
    elif rythm.startswith("SB ("):
        return "Sinus Brady"
    elif rythm.startswith("SR ("):
        return "Normal Sinus"
    elif rythm.startswith("ST ("):
        return "Sinus Tachy"
    elif rythm.startswith("SVT ("):
        return "Supravent Tachy"
    return rythm

def gcs_motor(scale):
    if scale == "1":
        return "No Response"
    elif scale == "2":
        return "Extension to Pain"
    elif scale == "3":
        return "Flexion to Pain"
    elif scale == "4":
        return "Withdrawal from Pain"
    elif scale == "5":
        return "Localising Pain"
    elif scale == "6":
        return "Obeys Commands"
    return scale

def gcs_verbal(scale):
    if scale == "1":
        return "No Response"
    elif scale == "2":
        return "Incomprehensible Sounds"
    elif scale == "3":
        return "Inappropriate Words"
    elif scale == "4":
        return "Confused"
    elif scale == "5":
        return "Orientated"
    return scale

def gcs_eye(scale):
    if scale == "1":
        return "No Opening"
    elif scale == "2":
        return "Open to Pain"
    elif scale == "3":
        return "Open to Verbal Command"
    elif scale == "4":
        return "Open Spontaneously"
    return scale

#Item class definition
class load_source(Enum):
    auto = 0,
    value = 1,
    value_num = 2,

class item():
    def __init__(self, id: int, target: str, numeric: bool, modifier=None, limits=None, source="value"):
        self.id = str(id)
        self.target = target
        self.numeric = numeric
        self.modifier = modifier
        self.limits = limits
        self.source = source

#Item merge definitions
observation_items = [
    item(220045, "Heart Rate (bpm)", True, None, (0, 250), "value"),
    item(211, "Heart Rate (bpm)", True, None, (0, 250, "value")),

    item(220048, "Heart Rythm", False, heart_rythm, "value"),
    item(212, "Heart Rythm", False, None, "value"),
]
