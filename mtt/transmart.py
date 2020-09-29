"""Module with contains constants about the required format for transmart-batch"""
import shutil
import os
from enum import Enum
from . import config as cfg
from .params_file import params_file
from .table import table
from .log import log, log_type, log_progress_bar, log_with_percent
from . import ascii

#Formats
file_delimiter = "\t"
file_ending = ".txt"
illegal_path_characters = ["<", ">", ":", "/", "\\", "|", "?", "*"] #For the os and the transmart hierarchy path
visitname_placeholder = "VISITNAME"
data_label_placeholder = "DATA_LABEL"

#Time series
create_timeseries_data = True

#Categorical variables
create_categorical_timeseries = True
max_categorical_str_len = 16

def export_study(clinical_tables, mimic_tables):
    rel_path = cfg.output_path + cfg.study_id + "/"
    path = cfg.getcwd() + rel_path

    log_with_percent("Exporting study", 0.0)
    #Delete old study folder
    if os.path.exists(path):
        shutil.rmtree(path, ignore_errors=True)

    log_with_percent("Exporting study", 0.1)
    #Create study folder
    if not os.path.exists(path):
        os.makedirs(path)

    log_with_percent("Exporting study", 0.2)
    #Reduce dataset to improve import speed
    reduce_dataset(clinical_tables)

    log_with_percent("Exporting study", 0.3)
    #Create study definition file and backout.params
    study_file = params_file()
    study_file["STUDY_ID"] = cfg.study_id
    study_file["SECURITY_REQUIRED"] =  "Y" if cfg.study_protected == True else "N"
    study_file["TOP_NODE"] = cfg.study_top_node
    study_file.write_to(path + "study.params")
    study_file.write_to(path + "backout.params")#backout is exactly like study.params, so just write the file twice

    log_with_percent("Exporting study", 0.35)
    #Split clinical and timeseries data (HDD)
    if create_timeseries_data == True:
        clinical_tables, hdd_tables = split_clinical_tables(clinical_tables)
    else:
        hdd_tables = []

    log_with_percent("Exporting study", 0.4)
    #Create clinical data
    export_clinical(rel_path, clinical_tables, mimic_tables)

    log_with_percent("Exporting study", 0.5)
    #Create platform
    platform_name = "ICU"
    export_platform(rel_path, platform_name, "ICU timeseries data about patients")

    log_with_percent("Exporting study", 0.7)
    #Create highdimensional data
    export_hdd(rel_path, hdd_tables, platform_name)

    log_with_percent("Exporting study", 1.0)
    #Return relative export path from the output directory
    return rel_path.replace(cfg.output_path, "")


def reduce_dataset(tables):
    if cfg.first_visit_only == True:
        log("Reducing dataset (first_visit_only)")
    for t in tables:
        #Remove all visits != first
        if cfg.first_visit_only == True:
            vn_index = t.column_index("VISIT_NAME")
            if vn_index != -1:
                for row in range(t.row_count - 1, -1, -1):
                    if int(t[vn_index, row]) > 1:
                        t.remove_row(row)


def split_clinical_tables(src_tables):
    clinical = src_tables
    hdd = []

    for i in range(len(src_tables) - 1, -1, -1):
        table = clinical[i]

        #First approach
        #Target tables are in the format | SUBJ_ID | VISIT_NAME | value |
        #if table.column_count == 3 and table.has_column("value") and (table.column_meta("value").type == tm_type.NUMERICAL or (table.column_meta("value").type == tm_type.CATEGORICAL and create_categorical_timeseries == True)):
        #    del clinical[i]
        #    hdd.append(table)

        #New approach: Dynamically define the platform based on the tables to allow sub values (prescriptions, etc.)
        #HD tables only contain columns SUBJ_ID, VISIT_NAME and the datetime meta data is assigned for all cells of all other columns
        fails_criteria = False
        for c in range(table.column_count):
            if c == 0 and table.column_name(c) != "SUBJ_ID":
                fails_criteria = True
                break
            elif c == 1 and table.column_name(c) != "VISIT_NAME":
                fails_criteria = True
                break
            elif c >= 2:
                meta = table.column_meta(table.column_name(c))
                if type(meta) is tm_column_md:
                    for k in range(table.row_count):
                        cell_meta = meta.get_cell_meta(k)
                        if (not (type(cell_meta) is tm_cell_md)) or (cell_meta.datetime == None):
                            fails_criteria = True
                            break
                else:
                    fails_criteria = True
                    break

        if fails_criteria == True:
            continue

        #Table is valid for hd-data
        del clinical[i]
        hdd.append(table)

    return (clinical, hdd)


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
    if not os.path.exists(clinical_path):
        os.makedirs(clinical_path)

    #Remove illegal file names in the tables
    for i in range(len(clinical_tables)):
        name = clinical_tables[i].name
        for illegal in illegal_path_characters:
            name = name.replace(illegal, "")
        clinical_tables[i]._name = name

    #Create and store mapping file + adjust data tables
    mapping = create_clinical_mapping(clinical_tables)
    mapping.store(clinical_path + clinical_map_file, file_delimiter)

    #Store data tables
    for i in range(len(clinical_tables)):
        clinical_tables[i].store(clinical_path + clinical_tables[i].name + file_ending, file_delimiter)

    #Create word map file
    word_map = create_word_map(clinical_tables, mimic_tables)
    word_map.store(clinical_path + clinical_word_map_file, file_delimiter)


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
                src.fill_column_array(new_column_name, [(column_meta.get_cell_meta(row).seq_num if column_meta.get_cell_meta(row) != None else column_name) for row in range(src.row_count)])
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
        tm_diagnoses = None
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
        tm_procedures = None
    if tm_procedures != None:
        for i in range(mimic_tables["D_ICD_PROCEDURES"].row_count):
            tm_word_map_table.add_row([tm_procedures.name + file_ending,
            tm_procedures.column_index("icd code") + 1,
            mimic_tables["D_ICD_PROCEDURES"].get("icd9_code", i),
            mimic_tables["D_ICD_PROCEDURES"].get("long_title", i)])

    return tm_word_map_table

def export_platform(path, name, title):
    organsism = "Homo Sapiens"
    platform_file_name = "mrna_annotation"
    platform_path = path + platform_file_name + "/"

    #Create platform definition file
    tm_platform = params_file()
    tm_platform["PLATFORM"] = name
    tm_platform["TITLE"] = title
    tm_platform["ANNOTATIONS_FILE"] = name + ".txt"
    tm_platform["ORGANISM"] = organsism
    tm_platform.write_to(path + platform_file_name + ".params")

    #Create platform folder
    if not os.path.exists(platform_path):
        os.makedirs(platform_path)

    #Create platform examination definition table
    tm_platform_table = table(name)
    tm_platform_table.add_column("GPL_ID")
    tm_platform_table.add_column("PROBE_NAME")
    tm_platform_table.add_column("GENES")
    tm_platform_table.add_column("ENTREZ_ID")
    tm_platform_table.add_column("ORGANISM")

    #For now, only define one numeric measurement: measurement
    tm_platform_table.add_row([name, "measurement", "", "", organsism])
    #For categorical data, define one measurement for each character: C1, C2, ...
    if create_categorical_timeseries == True:
        for i in range(max_categorical_str_len):
            tm_platform_table.add_row([name, f"char_{i}", "", "", organsism])

    #Store platform definition table
    tm_platform_table.store(platform_path + name + ".txt", file_delimiter)

def export_hdd(path, hdd_tables, platform_name):
    hdd_folder_path = path + "expression/"
    map_file_name = "subjectsamplemapping"
    map_file_path = hdd_folder_path + map_file_name + file_ending
    data_file_name = "data"
    data_file_path = hdd_folder_path + data_file_name + file_ending

    #Create hdd folder
    if not os.path.exists(hdd_folder_path):
        os.makedirs(hdd_folder_path)

    #Create HDD params file
    hdd_params = params_file()
    hdd_params["DATA_FILE"] = data_file_name + file_ending
    hdd_params["MAP_FILENAME"] = map_file_name + file_ending
    hdd_params["DATA_TYPE"] = "R"
    hdd_params["ALLOW_MISSING_ANNOTATIONS"] = "Y"
    hdd_params["SKIP_UNMAPPED_DATA"] = "N"
    hdd_params["ZERO_MEANS_NO_INFO"] = "N"  #This can be set to Y and 0 will not be inserted in the database. Just using -1 as a value have the same effect!
    hdd_params.write_to(path + "expression" + ".params")

    #Create subject sample mapping table
    map_table = table(map_file_name)
    map_table.add_column("STUDY_ID")
    map_table.add_column("SITE_ID")
    map_table.add_column("SUBJECT_ID")
    map_table.add_column("SAMPLE_CD")
    map_table.add_column("PLATFORM")
    map_table.add_column("SAMPLE_TYPE")
    map_table.add_column("TISSUE_TYPE")
    map_table.add_column("TIME_POINT")
    map_table.add_column("CATEGORY_CD")
    map_table.add_column("SOURCE_CD")

    #Create data table
    data_table = table(data_file_name)
    data_table.add_column("ID_REF")
    #Default numeric probe
    data_table.add_row(["measurement"])
    #Categorical probe
    if create_categorical_timeseries == True:
        for i in range(max_categorical_str_len):
            data_table.add_row([f"char_{i}"])

    total_neg_values = 0
    for t in hdd_tables:
        subject_id_index = t.column_index("SUBJ_ID")
        visit_name_index = t.column_index("VISIT_NAME")
        value_index = t.column_index("value")
        value_meta = t.column_meta("value")
        table_type = value_meta.type
        subj_id_dict = {}
        for row in range(t.row_count):
            #Create sample
            subject = t[subject_id_index, row]
            if not subject in subj_id_dict:
                subj_id_dict[subject] = 0

            cd = value_meta.category.replace(visitname_placeholder, t[visit_name_index, row])#Replace visit name placeholder by value
            sample_id = f"{t.name}_S{subject}_S{subj_id_dict[subject]}"
            map_table.add_row([cfg.study_id, "", subject, sample_id, platform_name, "", "", str(value_meta.get_cell_meta(row).datetime), cd, ""])

            subj_id_dict[subject] += 1

            #Fill data
            value = t[value_index, row]
            data_table.add_column(sample_id)

            #Numerical data
            data_table[data_table.column_count - 1, 0] = value if table_type == tm_type.NUMERICAL else -1

            #Negative values are being used for missing values, so always ensure that no valid negative values are in the dataset
            #In case that happens, the values of the type of measurement have to be shifted to a new positive range (Shouldnt happen, because measurements are usually in positive ranges)
            if table_type == tm_type.NUMERICAL:
                if value < 0:
                    log(f"table {t.name} contains negative value {value}!", log_type.WARNING)
                    total_neg_values += 1

            #Fill categorical data
            if create_categorical_timeseries == True:
                categorical_values = ascii.str_to_ascii_array(value) if table_type == tm_type.CATEGORICAL else []
                if len(categorical_values) > max_categorical_str_len:
                    log(f"The value ({value}) in table ({t.name}) is too long (limit={max_categorical_str_len})", log_type.WARNING)
                while(len(categorical_values) < max_categorical_str_len):
                    categorical_values.append(str(-1))
                for i in range(1, max_categorical_str_len + 1):
                    data_table[data_table.column_count - 1, i] = categorical_values[i - 1]

    #Save tables
    map_table.store(map_file_path, file_delimiter)
    data_table.store(data_file_path, file_delimiter)
    
    if total_neg_values > 0:
        log(f"Detected {total_neg_values} negative values!", log_type.WARNING)


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

class tm_cell_md:
    __slots__ = ["seq_num", "datetime"]
    def __init__(self, seq_num=None, datetime=None):
        self.seq_num = seq_num
        self.datetime = datetime

class tm_column_md():
    def __init__(self, category, tmtype=tm_type.NONE):
        self._category = category
        self._tmtype = tmtype
        #Used for sequence_id and datetime
        self._cell_meta = []

    @property
    def category(self):
        return self._category

    @property
    def type(self):
        return self._tmtype

    def get_cell_meta(self, row: int) -> tm_cell_md:
        if row < len(self._cell_meta):
            return self._cell_meta[row]
        return None

    def set_cell_meta(self, row: int, data: tm_cell_md):
        while row >= len(self._cell_meta):
            self._cell_meta.append(None)
        self._cell_meta[row] = data

    def removed_row(self, row: int):
        if row < len(self._cell_meta):
            del self._cell_meta[row]

#Can be used to define tables with observations that contain more than one sub value (category + node_name + column_name)
class tm_partial_column_md(tm_column_md):
    def __init__(self, category, tmtype=tm_type.NONE, node_name=""):
        super().__init__(category, tmtype)
        self._node_name = node_name

    @property
    def node_name(self):
        return self._node_name
