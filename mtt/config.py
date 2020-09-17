import os

#Paths are expected to be relative from the working directory (os.getcwd() == MTT/) and end with '/'
mimic_path = "data/input/mimic-iii-clinical-database-demo-1.4/"
output_path = "data/output/"

#Study settings
study_id = "MIMIC3_DEMO"
study_protected = False
study_top_node = "\\Public Studies\\" + study_id

#Server path settings (address, username, password in secrets.py)
docker_path = r"/home/cloud/tm_umg/"                                                #Path to the docker version of tranSMART
incoming_data_path = r"/var/lib/docker/volumes/tm_umg_tm_opt/_data/data/incoming/"  #Path to the incoming study data path (Needs write permission, parent dir also needs write permission)

#Data settings
first_visit_only = True

def getcwd():
    return os.getcwd() + "/"