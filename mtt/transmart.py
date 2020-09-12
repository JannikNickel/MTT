"""Module with contains constants about the required format for transmart-batch"""
import shutil
import os
from enum import Enum
from . import config as cfg
from .params_file import params_file
from .table import table
from .log import log, log_type, log_progress_bar

#Formats
file_delimiter = "\t"
file_ending = ".txt"
illegal_path_characters = ["<", ">", ":", "/", "\\", "|", "?", "*"] #For the os and the transmart hierarchy path
visitname_placeholder = "VISITNAME"
data_label_placeholder = "DATA_LABEL"

def export_study(clinical_tables, mimic_tables):
    rel_path = cfg.output_path + cfg.study_id + "/"
    path = cfg.getcwd() + rel_path

    #Delete old study folder
    if os.path.exists(path):
        shutil.rmtree(path, ignore_errors=True)

    #Create study folder
    if not os.path.exists(path):
        os.makedirs(path)

    #Create study definition file and backout.params
    study_file = params_file()
    study_file["STUDY_ID"] = cfg.study_id
    study_file["SECURITY_REQUIRED"] =  "Y" if cfg.study_protected == True else "N"
    study_file["TOP_NODE"] = cfg.study_top_node
    study_file.write_to(path + "study.params")
    study_file.write_to(path + "backout.params")#backout is exactly like study.params, so just write the file twice

    #Create clinical data
    export_clinical(rel_path, clinical_tables, mimic_tables)

    #Return relative export path from the output directory
    return rel_path.replace(cfg.output_path, "")


def export_clinical(path, clinical_tables, mimic_tables):
    clinical_path = path + "clinical/"
    clinical_map_file = "clinical_map" + file_ending
    clinical_word_map_file = "clinical_word_map" + file_ending

    #Create clinical.params file
    clinical_file = params_file()
    clinical_file["COLUMN_MAP_FILE"] = clinical_map_file
    clinical_file["WORD_MAP_FILE"] = clinical_word_map_file
    clinical_file.write_to(path + "clinical.params")

    #Create clinical data folder
    log_progress_bar(0.0)
    if not os.path.exists(clinical_path):
        os.makedirs(clinical_path)

    #Remove illegal file names in the tables
    log_progress_bar(0.1)
    for i in range(len(clinical_tables)):
        name = clinical_tables[i].name
        for illegal in illegal_path_characters:
            name = name.replace(illegal, "")
        clinical_tables[i]._name = name

    #Create and store mapping file + adjust data tables
    log_progress_bar(0.2)
    mapping = create_clinical_mapping(clinical_tables)
    mapping.store(clinical_path + clinical_map_file, file_delimiter)

    #Store data tables
    log_progress_bar(0.4)
    for i in range(len(clinical_tables)):
        clinical_tables[i].store(clinical_path + clinical_tables[i].name + file_ending, file_delimiter)
        log_progress_bar(0.4 + (i / float(len(clinical_tables)) * 0.6 * 0.9))

    #Create word map file
    word_map = create_word_map(clinical_tables, mimic_tables)
    word_map.store(clinical_path + clinical_word_map_file, file_delimiter)

    log_progress_bar(1.0)


def create_clinical_mapping(clinical_tables) -> table:
    t = table("clinical_map")
    t.add_column("filename")
    t.add_column("category_cd")
    t.add_column("column_nr")
    t.add_column("data_label")
    t.add_column("data_lbl_src")
    t.add_column("control_voc_cd")
    t.add_column("concept_type")

    for src in clinical_tables:
        file_name = src.name + file_ending
        new_column_index = 1

        #Iterate over all columns (they will change -> use while loop)
        src_column_count = src.column_count
        i = 0
        while(i < src_column_count):
            column_name = src.column_name(i)
            column_meta = src.column_meta(column_name)
            if column_meta != None and type(column_meta) != tm_column_md:
                log("Trying to export clinical data table without using tm_column_md metadata class!", log_type.WARNING)
            column_cd = column_meta.category if column_meta != None else ""
            column_type = column_meta.type if column_meta != None else tm_type.NONE

            if column_cd == "" and column_type != tm_type.NONE:
                log(f"Table '{src.name}' column '{column_name}' doesnt not have a category specified. This will most likely result in an upload error!", log_type.WARNING)

            #If the visit name placeholder occurs in the the column, insert a new column that describes the name of this column
            if visitname_placeholder in column_cd:
                #Add new column definition row
                new_column_name = column_name + "_lbl"
                t.add_row([file_name, "", new_column_index, data_label_placeholder, "", "", ""])
                #Insert label column to the data table
                src.insert_column(new_column_index - 1, new_column_name)
                src.fill_column_array(new_column_name, [(column_meta.get_cell_meta(row) if column_meta.get_cell_meta(row) != "" else column_name) for row in range(src.row_count)])
                src_column_count += 1
                i += 1
                new_column_index += 1
                #Add the column definition row
                t.add_row([file_name, column_cd, new_column_index, "\\", str(new_column_index - 1), "", tm_type.to_clinical_type(column_type)])
            else:
                #Otherwise just insert the column definition as a row in the mapping table
                t.add_row([file_name, column_cd, new_column_index, column_name, "", "", tm_type.to_clinical_type(column_type)])

            new_column_index += 1
            i += 1

    return t

def create_word_map(clinical_tables, mimic_tables):
    #Word maps can only be created after the other tables got exported, because the export modifies the columns to work in transmart
    #The word map stores references to the table column indices
    tm_word_map_table = table("tm_word_map")
    tm_word_map_table.add_column("file")
    tm_word_map_table.add_column("column")
    tm_word_map_table.add_column("from")
    tm_word_map_table.add_column("to")


    #Add diagnoses to word map
    try:
        tm_diagnoses = [x for x in clinical_tables if x.name == "tm_diagnoses"][0]
    except:
        pass
    if tm_diagnoses != None:
        for i in range(mimic_tables["D_ICD_DIAGNOSES"].row_count):
            tm_word_map_table.add_row([tm_diagnoses.name + file_ending,
            tm_diagnoses.column_index("icd code") + 1,
            mimic_tables["D_ICD_DIAGNOSES"].get("icd9_code", i),
            mimic_tables["D_ICD_DIAGNOSES"].get("long_title", i)])

    #Add procedures to word map
    try:
        tm_procedures = [x for x in clinical_tables if x.name == "tm_procedures"][0]
    except:
        pass
    if tm_procedures != None:
        for i in range(mimic_tables["D_ICD_PROCEDURES"].row_count):
            tm_word_map_table.add_row([tm_procedures.name + file_ending,
            tm_procedures.column_index("icd code") + 1,
            mimic_tables["D_ICD_PROCEDURES"].get("icd9_code", i),
            mimic_tables["D_ICD_PROCEDURES"].get("long_title", i)])

    return tm_word_map_table


#TODO methods to define platforms and to create HDD data

class tm_type(Enum):
    NONE = 0,
    CATEGORICAL = 1,
    NUMERICAL = 2,
    TIME = 3

    @staticmethod
    def to_clinical_type(tmtype):
        if tmtype == tm_type.NONE:
            return ""
        elif tmtype == tm_type.CATEGORICAL:
            return "CATEGORICAL"
        elif tmtype == tm_type.NUMERICAL:
            return "NUMERICAL"
        elif tmtype == tm_type.TIME:
            return ""

class tm_column_md():
    def __init__(self, category, tmtype=tm_type.NONE):
        self._category = category
        self._tmtype = tmtype
        #Used for sequence_id (kinda legacy now)
        self._cell_meta = []

    @property
    def category(self):
        return self._category

    @property
    def type(self):
        return self._tmtype

    def get_cell_meta(self, row):
        if row < len(self._cell_meta):
            return self._cell_meta[row]
        return ""

    def set_cell_meta(self, row, data):
        while row >= len(self._cell_meta):
            self._cell_meta.append("")
        self._cell_meta[row] = data
