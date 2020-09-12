import time
import os
import ctypes

from . import config as cfg
from .log import log, log_type
from .table import table
from . import mimic
from . import transmart
from . import transform
from . import num_str_utils
from . import T

#Switch console mode to allo ansi escape sequences on windows
if os.name == "nt":
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

log(">>>>>>>>>>>>>>>>>>>> MTT <<<<<<<<<<<<<<<<<<<<")

###############################################################################
# Load MIMIC tables                                                           #
###############################################################################
mimic3 = mimic.mimiciii.load_dataset(cfg.mimic_path)
mimic_tables = mimic3.tables


###############################################################################
# Transform Preparation                                                       #
###############################################################################
log(">>> Preparation")

#Transmart sorts values lexicographically -> fill with zeros to have length lexicographically order
transmart_visit_name_values = [f"{(i + 1):02}" for i in range(99)]

#Mapping from hadm_id to visit number and hadm_id to patient
#In the mimic tables the hadm_id is a unique value. In transmart the visit has to be an ascending number for each patient
#-> Create helper dictionaries to map each visit id to a number and to map each visit id to the patient
hadm_to_visit = {}
hadm_to_subj = {}
admissions_subj_index = mimic_tables["ADMISSIONS"].column_index("subject_id")
admissions_hadm_index = mimic_tables["ADMISSIONS"].column_index("hadm_id")
for i in range(mimic_tables["ADMISSIONS"].row_count):
    visit_num = 0
    subj_id = mimic_tables["ADMISSIONS"][admissions_subj_index, i]
    hadm_id = mimic_tables["ADMISSIONS"][admissions_hadm_index, i]
    for k in range(i - 1, 0, -1):
        if mimic_tables["ADMISSIONS"][admissions_subj_index, k] == subj_id:
            visit_num += 1

    hadm_to_visit[hadm_id] = str(transmart_visit_name_values[visit_num])
    if not hadm_id in hadm_to_subj:
        hadm_to_subj[hadm_id] = subj_id

###############################################################################
# Generate data tables                                                        #
###############################################################################
log(">>> Transform")

#Patient data
tm_patients = T.create_patients_data(mimic_tables, hadm_to_subj, hadm_to_visit)

#Admissions data
tm_admissions = T.create_admissions_data(mimic_tables, hadm_to_subj, hadm_to_visit)

#Diagnoses/Procedures data
tm_diagnoses = T.create_diagnoses_data(mimic_tables, hadm_to_subj, hadm_to_visit)
tm_procedures = T.create_procedures_data(mimic_tables, hadm_to_subj, hadm_to_visit)

###############################################################################
# Export                                                                      #
###############################################################################
log(">>> Export")
transmart.export_study([tm_patients, tm_admissions, tm_diagnoses, tm_procedures], mimic_tables)