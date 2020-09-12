from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from . import mimic
import numpy as np
import math

def date_dif_d(dates):
    if len(dates) < 2:
        return ""
    return str(math.floor(float(date_dif_d_fractional(dates))))

def date_dif_d_fractional(dates):
    if len(dates) < 2:
        return ""
    d0 = datetime.strptime(dates[0], mimic.time_format)
    d1 = datetime.strptime(dates[1], mimic.time_format)
    if d0 < d1:
        duration = (d1 - d0).total_seconds() / timedelta(days=1).total_seconds()
    else:
        duration = (d0 - d1).total_seconds() / timedelta(days=1).total_seconds()
    return str(duration)

def date_dif_h_fractional_with_null(dates):
    if len(dates) < 2:
        return "0"
    if dates[0] == "" or dates[1] == "":
        return "0"
    d0 = datetime.strptime(dates[0], mimic.time_format)
    d1 = datetime.strptime(dates[1], mimic.time_format)
    duration = (d1 - d0).total_seconds() / timedelta(hours=1).total_seconds()
    return str(duration)

def calc_age_for_hadm(patients_table, admissions_table, row):
    d1 = datetime.strptime(admissions_table.get("admittime", row), mimic.time_format)
    subj_id = admissions_table.get("subject_id", row)
    patients_indices = patients_table.where_value("subject_id", subj_id)
    if len(patients_indices) == 0:
        return ""
    d0 = datetime.strptime(patients_table.get("dob", patients_indices[0]), mimic.time_format)
    age = relativedelta(d1, d0).years
    if age == 300:
        age = 90
    return str(age)

def map_values_to_one(values, value, x):
    if x in values:
        return value
    return x