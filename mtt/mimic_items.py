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

    item(220210, "Respiratory Rate (insp/min)", True),
    item(618, "Respiratory Rate (insp/min)", True),

    item(223985, "Respiratory Pattern", False),
    item(617, "Respiratory Pattern", False),

    item(223762, "Temperature (C)", True, None, (0, 45)),
    item(223761, "Temperature (C)", True, fahrenheit_to_celcius, (0, 45)),
    item(676, "Temperature (C)", True, None, (0, 45)),
    item(678, "Temperature (C)", True, fahrenheit_to_celcius, (0, 45)),

    item(220179, "Non invasive blood pressure systolic (mmHg)", True),
    item(455, "Non invasive blood pressure systolic (mmHg)", True),

    item(220180, "Non invasive blood pressure diastolic (mmHg)", True),
    item(8441, "Non invasive blood pressure diastolic (mmHg)", True),

    item(220181, "Non invasive blood pressure mean (mmHg)", True),
    item(456, "Non invasive blood pressure mean (mmHg)", True),

    item(220050, "Arterial blood pressure systolic (mmHg)", True),
    item(51, "Arterial blood pressure systolic (mmHg)", True),

    item(220051, "Arterial blood pressure diastolic (mmHg)", True),
    item(8368, "Arterial blood pressure diastolic (mmHg)", True),

    item(220052, "Arterial blood pressure mean (mmHg)", True),
    item(52, "Arterial blood pressure mean (mmHg)", True),

    item(220277, "O2 Saturation (%)", True, None, (0, 100)),
    item(646, "O2 Saturation (%)", True, None, (0, 100)),

    item(226512, "Weight (kg)", True, None, (0, 250)),
    item(224639, "Weight (kg)", True, None, (0, 250)),
    item(763, "Weight (kg)", True, None, (0, 250)),
    item(3693, "Weight (kg)", True, None, (0, 250)),
    #There are more unused definitions for pain

    item(226730, "Height (cm)", True, None, (0, 275)),
    item(920, "Height (cm)", True, inch_to_cm, (0, 275)),

    item(220277, "Skin color", False),
    item(646, "Skin color", False),

    item(223876, "Apnea interval (s)", True),
    item(50, "Apnea interval (s)", True),

    item(223834, "O2 Flow (L/min)", True),
    item(470, "O2 Flow (L/min)", True),

    item(225664, "Glucose fingerstick", True),
    item(807, "Glucose fingerstick", True),

    item(220621, "Glucose (mg/dL)", True),
    item(1529, "Glucose (mg/dL)", True),

    item(223872, "Inspired Gas Temp (C)", True),
    item(417, "Inspired Gas Temp (C)", True),

    item(220074, "Central venous pressure (mmHg)", True),
    item(113, "Central venous pressure (mmHg)", True),

    item(224144, "Blood flow (ml/min)", True),
    item(79, "Blood flow (ml/min)", True),

    item(223781, "Pain Present", False),
    item(1046, "Pain Present", False),

    item(223782, "Pain Type", False),
    item(527, "Pain Type", False),

    item(223791, "Pain Level", False, pain_0_10),
    item(1044, "Pain Level", False, lambda x: pain_0_10(x.split("-")[0]) if len(x.split("-")) > 0 else "Unable to Score"),

    item(224003, "Abdominal Assessment", False),
    item(27, "Abdominal Assessment", False),

    item(224084, "Activity", False),
    item(31, "Activity", False),

    item(226105, "Behaviour", False),
    item(77, "Behaviour", False),

    item(224004, "Bowel Sounds", False),
    item(80, "Bowel Sounds", False),

    item(220739, "Eye Opening (GCS)", False, gcs_eye),
    item(184, "Eye Opening (GCS)", False, gcs_eye),

    item(227013, "GCS", True),
    item(198, "GCS", True),

    item(224080, "Head of Bed", False, lambda x: x.replace("degrees", "Degrees").replace("-berg", "-Berg")),
    item(210, "Head of Bed", False, lambda x: x.replace("degrees", "Degrees").replace("-berg", "-Berg")),

    item(223989, "LLL Lung Sounds", False),
    item(425, "LLL Lung Sounds", False),

    item(223988, "LUL Lung Sounds", False),
    item(428, "LUL Lung Sounds", False),

    item(223987, "RLL Lung Sounds", False),
    item(593, "RLL Lung Sounds", False),

    item(223986, "RUL Lung Sounds", False),
    item(599, "RUL Lung Sounds", False),

    item(226104, "Level of Conscious", False),
    item(432, "Level of Conscious", False),

    item(223898, "Orientation", False),
    item(479, "Orientation", False, lambda x: x.replace("x ", "x")),

    item(224093, "Position", False),
    item(547, "Position", False),

    item(223759, "Precautions", False),
    item(550, "Precautions", False, lambda x: x.replace("Airborne/Resp", "Airborne/Respiratory")),

    item(224026, "Skin Integrity", False),
    item(644, "Skin Integrity", False),

    item(224015, "Urine Source", False),
    item(707, "Urine Source", False, lambda x: x.replace("Cath", "Urinary Catheter") if x.endswith("Cath") else x),

    item(154, "Diet Type", False),
    item(224001, "Diet Type", False),

    item(223910, "Follows Commands", False),
    item(197, "Follows Commands", False),

    item(223920, "LL Strength/Movement", False),
    item(423, "LL Strength/Movement", False),

    item(223919, "LU Strength/Movement", False),
    item(426, "LU Strength/Movement", False),

    item(223918, "RL Strength/Movement", False),
    item(590, "RL Strength/Movement", False),

    item(223917, "RU Strength/Movement", False),
    item(596, "RU Strength/Movement", False),

    item(223911, "Spontaneous Movement", False),
    item(655, "Spontaneous Movement", False, lambda x: x.replace("-", "")),

    item(223830, "Arterial pH", True, None, (0, 10)),
    item(780, "Arterial pH", True, None, (0, 10)),

    item(224697, "Airway Pressure (cmH2O)", True),
    item(444, "Airway Pressure (cmH2O)", True),

    item(228368, "Cardiac Index", True),
    item(116, "Cardiac Index", True),

    item(224016, "Urine Color", False),
    item(706, "Urine Color", False),

    item(224876, "Urine Appearance", False),
    item(8480, "Urine Appearance", False),

    item(227121, "Pupil Response Right", False),
    item(584, "Pupil Response Right", False, lambda x: x.replace("-", "")),

    item(227288, "Pupil Response Left", False),
    item(8466, "Pupil Response Left", False, lambda x: x.replace("-", "")),

    item(223907, "Pupil Size Right", False),
    item(585, "Pupil Size Right", False),

    item(224733, "Pupil Size Left", False),
    item(8467, "Pupil Size Left", False),

    item(224370, "Sputum Color", False),
    item(656, "Sputum Color", False),

    item(224372, "Sputum Source", False),
    item(657, "Sputum Source", False, lambda x: x.replace("Nasotracheal", "Nasotrachial").replace("Sxn", "Suction")),

    item(224369, "Sputum Consistency", False),
    item(8476, "Sputum Consistency", False),

    item(224373, "Sputum Amount", False),
    item(8477, "Sputum Amount", False),

    item(223754, "Risk for Falls", False),
    item(1484, "Risk for Falls", False),

    item(223898, "Orientation", False),
    item(479, "Orientation", False),

    item(223900, "Verbal Response (GCS)", False, gcs_verbal),
    item(723, "Verbal Response (GCS)", False, gcs_verbal),

    item(223901, "GCS - Motor Response", False, gcs_motor),
    item(454, "GCS - Motor Response", False, gcs_motor),

    item(224651, "Ectopy Frequency", True),
    item(226480, "Ectopy Frequency", True),
    item(159, "Ectopy Frequency", True),
    item(160, "Ectopy Frequency", True),

    item(226104, "Level of Consciousness", False),
    item(432, "Level of Consciousness", False, lambda x: x.replace("Stimul", "Stimulation") if x.endswith("Stimul") else x),

    item(224086, "Activity Tolerance", False),
    item(32, "Activity Tolerance", False),

    item(227346, "Mental Status", False),

    item(223902, "Speech", False),
    item(228414, "Speech", False),
    item(648, "Speech", False, lambda x: x.replace("trached", "trach")),

    item(223903, "Communication", False),
    item(130, "Communication", False),

    item(223904, "Gag Reflex", False),
    item(208, "Gag Reflex", False),

    item(223905, "Cough Reflex", False),
    item(137, "Cough Reflex", False),

    item(223916, "Response to stimuli", False),
    item(3606, "Response to stimuli", False),

    item(224011, "Stool Consistency", False),
    item(8478, "Stool Consistency", False),

    item(224012, "Stool Management", False),
    item(661, "Stool Management", False, lambda x: x.replace("Cath", "Catheter") if x.endswith("Cath") else x),

    item(224794, "Stool Color", False),
    item(8535, "Stool Color", False),
    item(659, "Stool Color", False),

    item(224409, "Pain Level Response", False, pain_0_10),
    item(1045, "Pain Level Response", False, lambda x: pain_0_10(x.split("-")[0]) if len(x.split("-")) > 0 else "Unable to Score"),

    item(227955, "Food and Fluid", False),

    item(220545, "Hematocrit (%)", True),
    item(813, "Hematocrit (%)", True),

    item(220602, "Chloride (mEq/L)", True),
    item(1523, "Chloride (mEq/L)", True),#No unit specified, but matches the metavision values

    item(220615, "Creatinine (mg/dL)", True),
    item(1525, "Creatinine (mg/dL)", True),#No unit specified, but matches the metavision values

    item(220635, "Magnesium (mg/dL)", True),
    item(1532, "Magnesium (mg/dL)", True),#No unit specified, but matches the metavision values

    item(220645, "Sodium (mEq/L)", True),
    item(1536, "Sodium (mEq/L)", True),#No unit specified, but matches the metavision values

    item(225624, "Blood Uread Nitrogen (mg/dL)", True),
    item(1162, "Blood Uread Nitrogen (mg/dL)", True),#No unit specified, but matches the metavision values

    item(227442, "Potassium (mEq/L)", True),
    item(1535, "Potassium (mEq/L)", True),#No unit specified, but matches the metavision values

    item(227443, "HCO3 (mEq/L)", True),
    item(812, "HCO3 (mEq/L)", True),#Not in dataset
]
