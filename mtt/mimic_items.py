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
    item(211, "Heart Rate (bpm)", True, None, (0, 250), "value"),

    item(220210, "Respiratory Rate (insp/min)", True),
    item(618, "Respiratory Rate (insp/min)", True),

    item(223985, "Respiratory Pattern", False),
    item(617, "Respiratory Pattern", False),

    item(220277, "O2 Saturation (%)", True, None, (0, 100)),
    item(646, "O2 Saturation (%)", True, None, (0, 100)),

    #item(224084, "Activity", False),
    #item(31, "Activity", False),

    #item(220545, "Hematocrit (%)", True),
    #item(813, "Hematocrit (%)", True),
]

output_items = [
    item(40055, "Urine Out Foley (mL)", True),
    item(226559, "Urine Out Foley (mL)", True),

    item(40054, "Stool Out (mL)", True),
    item(226579, "Stool Out (mL)", True),

    item(40059, "Oral Gastric (mL)", True),
    item(226576, "Oral Gastric (mL)", True),

    item(40060, "Pre Admission Out (mL)", True),
    item(226633, "Pre Admission Out (mL)", True),

    item(40473, "Ileoconduit (mL)", True),
    item(226584, "Ileoconduit (mL)", True),

    item(40069, "Urine Out Void (mL)", True),
    item(226560, "Urine Out Void (mL)", True),

    item(40067, "Gastric Emesis (mL)", True),
    item(226571, "Gastric Emesis (mL)", True),

    item(40076, "Chest Tube #1 (mL)", True),
    item(226588, "Chest Tube #1 (mL)", True),

    item(41707, "Chest Tube #2 (mL)", True),
    item(226589, "Chest Tube #2 (mL)", True),

    item(40052, "Nasogastric (mL)", True),
    item(226575, "Nasogastric (mL)", True),

    item(40286, "Ultrafiltrate (mL)", True),
    #item(0, "Ultrafiltrate (mL)", True), #No entry in metavision?

    item(41683, "Drain Out JP Lateral (mL)", True),
    item(226598, "Drain Out JP Lateral (mL)", True),

    item(40926, "Drain Out JP Medial (mL)", True),
    item(226597, "Drain Out JP Medial (mL)", True),
    
    item(40071, "Drain Out JP #1 (mL)", True),
    item(226599, "Drain Out JP #1 (mL)", True),

    item(40064, "OR Out EBL (mL)", True),
    item(226626, "OR Out EBL (mL)", True),

    item(40051, "Gastric Tube (mL)", True),
    item(226573, "Gastric Tube (mL)", True),

    item(40367, "Rectal Tube (mL)", True),
    item(226583, "Rectal Tube (mL)", True),

    item(40053, "Fecal Bag (mL)", True),
    item(226580, "Fecal Bag (mL)", True),

    item(46071, "Ostomy Out (mL)", True),
    item(226582, "Ostomy Out (mL)", True),

    item(40292, "Drain Out T Tube (mL)", True),
    item(40093, "Drain Out T Tube (mL)", True),
    item(226603, "Drain Out T Tube (mL)", True),

    item(40061, "OR Urine (mL)", True),
    item(226627, "OR Urine (mL)", True),

    #item(0, "TF Residual (mL)", True), #No entry in carevue?
    item(227510, "TF Residual (mL)", True),

    item(46539, "Drainage Bag (mL)", True),
    item(227701, "Drainage Bag (mL)", True),

    #item(0, "GU Irrigant Volume In (mL)", True), #No entry in carevue?
    item(227488, "GU Irrigant Volume In (mL)", True),

    item(46449, "GU Irrigant Volume Out (mL)", True),
    item(42209, "GU Irrigant Volume Out (mL)", True),
    item(227489, "GU Irrigant Volume Out (mL)", True),

    item(42315, "Pericardial (mL)", True),
    item(43722, "Pericardial (mL)", True),
    item(41933, "Pericardial (mL)", True),
    item(226612, "Pericardial (mL)", True),

    item(40956, "Paracentesis (mL)", True),
    #item(0, "Paracentesis (mL)", True), # No entry in metavision?

    item(40056, "Drain Out Nephrostomy Lt #1 (mL)", True),
    item(226564, "Drain Out Nephrostomy Lt #1 (mL)", True),

    item(44676, "Drain Out Nephrostomy Lt #2 (mL)", True),
    item(226565, "Drain Out Nephrostomy Lt #2 (mL)", True),
]
