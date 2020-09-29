import time
import os
import ctypes

from . import config as cfg
from .log import log, log_type, log_with_percent
from .table import table
from . import mimic
from . import transmart
from . import transform
from . import num_str_utils
from . import T
from . import tm_upload
from . import secrets

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
# Generate data tables (transform)                                            #
###############################################################################
log(">>> Transform")
tm_tables = []

#Patient data
tm_tables += [T.create_patients_data(mimic_tables, hadm_to_subj, hadm_to_visit)]
#Admissions data
tm_tables += [T.create_admissions_data(mimic_tables, hadm_to_subj, hadm_to_visit)]
#Diagnoses/Procedures data
tm_tables += [T.create_diagnoses_data(mimic_tables, hadm_to_subj, hadm_to_visit)]
tm_tables += [T.create_procedures_data(mimic_tables, hadm_to_subj, hadm_to_visit)]
#Observation data
tm_tables += T.create_observations_data(mimic_tables, hadm_to_subj, hadm_to_visit)
#Lab data
tm_tables += T.create_lab_data(mimic_tables, hadm_to_subj, hadm_to_visit)
#ICU stays data
tm_tables += [T.create_icu_stay_data(mimic_tables, hadm_to_subj, hadm_to_visit)]
#Services data
tm_tables += [T.create_services_data(mimic_tables, hadm_to_subj, hadm_to_visit)]
#Output data
tm_tables += T.create_output_data(mimic_tables, hadm_to_subj, hadm_to_visit)
#Input data
tm_tables += T.create_input_data(mimic_tables, hadm_to_subj, hadm_to_visit)


###############################################################################
# Export                                                                      #
###############################################################################
log(">>> Export")
rel_export_path = transmart.export_study(tm_tables, mimic_tables)


###############################################################################
# Upload                                                                      #
###############################################################################
log(">>> Do you want to upload the dataset to transmart? [y/n/f/h] (yes/no/full/home)")
upload_answer = input()
if upload_answer == "Y" or upload_answer == "y":
    tm_upload.upload_data(rel_export_path)
elif upload_answer == "F" or upload_answer == "f":
    secrets.tmserver_address = secrets.tm_fullserver_address
    secrets.tmserver_user = secrets.tm_fullserver_user
    secrets.tmserver_password = secrets.tm_fullserver_password
    tm_upload.upload_data(rel_export_path)
elif upload_answer == "H" or upload_answer == "h":
    secrets.tmserver_address = secrets.tm_homeserver_address
    secrets.tmserver_user = secrets.tm_homeserver_user
    secrets.tmserver_password = secrets.tm_homeserver_password
    tm_upload.upload_data(rel_export_path)
