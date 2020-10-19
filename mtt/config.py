import os

#Paths are expected to be relative from the working directory (os.getcwd() == MTT/) and end with '/'
mimic_path = "data/input/mimic-iii-clinical-database-demo-1.4/"
output_path = "data/output/"

#Study settings
study_id = "MIMIC3_DEMO"
study_protected = False
study_top_node = "\\Public Studies\\" + study_id

#Data settings
first_visit_only = False

def getcwd():
    return os.getcwd() + "/"