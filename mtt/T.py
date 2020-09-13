from . import config as cfg
from .log import log, log_type
from .table import table
from . import mimic
from . import transmart
from . import transform
from . import num_str_utils

#Settings
visit_name_path = "Visit_" + transmart.visitname_placeholder

def create_patients_data(mimic_tables, hadm_to_subj, hadm_to_visit):
    #Table definition
    tm_patients = table("tm_patients")
    tm_patients.add_column("STUDY_ID")
    tm_patients.add_column("SUBJ_ID")
    tm_patients.add_column("Gender",        transmart.tm_column_md("Subjects+Demographics", transmart.tm_type.CATEGORICAL))
    tm_patients.add_column("Alive",         transmart.tm_column_md("Subjects+Demographics", transmart.tm_type.CATEGORICAL))
    tm_patients.add_column("Subject ID",    transmart.tm_column_md("Subjects+Demographics", transmart.tm_type.NUMERICAL))

    #Map data
    tm_patients.add_rows(mimic_tables["PATIENTS"].row_count)
    tm_patients.fill_column("STUDY_ID", cfg.study_id)
    tm_patients.map_column_values_from(mimic_tables["PATIENTS"], "subject_id", "SUBJ_ID")
    tm_patients.map_column_values_from(mimic_tables["PATIENTS"], "gender", "Gender")
    tm_patients.map_column_values_from(mimic_tables["PATIENTS"], "expire_flag", "Alive", (lambda x: "Yes" if x == "0" else "No"))
    tm_patients.map_column_values_from(mimic_tables["PATIENTS"], "subject_id", "Subject ID")

    return tm_patients

def create_admissions_data(mimic_tables, hadm_to_subj, hadm_to_visit):
    #Table definition
    tm_admissions = table("tm_admissions")
    tm_admissions.add_column("STUDY_ID")
    tm_admissions.add_column("SUBJ_ID")
    tm_admissions.add_column("VISIT_NAME")
    tm_admissions.add_column("Time In Hospital (days)",             transmart.tm_column_md(f"Subjects+Hospital_Stays+{visit_name_path}+Demographics", transmart.tm_type.NUMERICAL))
    tm_admissions.add_column("Age",                                 transmart.tm_column_md(f"Subjects+Hospital_Stays+{visit_name_path}+Demographics", transmart.tm_type.NUMERICAL))
    tm_admissions.add_column("Admission Type",                      transmart.tm_column_md(f"Subjects+Hospital_Stays+{visit_name_path}+Demographics", transmart.tm_type.CATEGORICAL))
    tm_admissions.add_column("Admission Location",                  transmart.tm_column_md(f"Subjects+Hospital_Stays+{visit_name_path}+Demographics", transmart.tm_type.CATEGORICAL))
    tm_admissions.add_column("Discharge Location",                  transmart.tm_column_md(f"Subjects+Hospital_Stays+{visit_name_path}+Demographics", transmart.tm_type.CATEGORICAL))
    tm_admissions.add_column("Insurance",                           transmart.tm_column_md(f"Subjects+Hospital_Stays+{visit_name_path}+Demographics", transmart.tm_type.CATEGORICAL))
    tm_admissions.add_column("Religion",                            transmart.tm_column_md(f"Subjects+Hospital_Stays+{visit_name_path}+Demographics", transmart.tm_type.CATEGORICAL))
    tm_admissions.add_column("Marital Status",                      transmart.tm_column_md(f"Subjects+Hospital_Stays+{visit_name_path}+Demographics", transmart.tm_type.CATEGORICAL))
    tm_admissions.add_column("Ethnicity",                           transmart.tm_column_md(f"Subjects+Hospital_Stays+{visit_name_path}+Demographics", transmart.tm_type.CATEGORICAL))
    tm_admissions.add_column("Expired In Hospital",                 transmart.tm_column_md(f"Subjects+Hospital_Stays+{visit_name_path}+Demographics", transmart.tm_type.CATEGORICAL))
    tm_admissions.add_column("Time In ED (hours)",                  transmart.tm_column_md(f"Subjects+Hospital_Stays+{visit_name_path}+Demographics", transmart.tm_type.NUMERICAL))
    tm_admissions.add_column("Post Hospital Survival Time (days)",  transmart.tm_column_md(f"Subjects+Hospital_Stays+{visit_name_path}+Demographics", transmart.tm_type.NUMERICAL))

    #Map data
    tm_admissions.add_rows(mimic_tables["ADMISSIONS"].row_count)
    tm_admissions.fill_column("STUDY_ID", cfg.study_id)
    tm_admissions.map_column_values_from(mimic_tables["ADMISSIONS"], "subject_id", "SUBJ_ID")
    tm_admissions.map_column_values_from(mimic_tables["ADMISSIONS"], "hadm_id", "VISIT_NAME", lambda x: hadm_to_visit[x])
    tm_admissions.map_from_many(mimic_tables["ADMISSIONS"], ["admittime", "dischtime"], "Time In Hospital (days)", transform.date_dif_d)
    tm_admissions.fill_column_array("Age", [transform.calc_age_for_hadm(mimic_tables["PATIENTS"], mimic_tables["ADMISSIONS"], row) for row in range(mimic_tables["ADMISSIONS"].row_count)])
    tm_admissions.map_column_values_from(mimic_tables["ADMISSIONS"], "admission_type", "Admission Type")
    tm_admissions.map_column_values("Admission Type", lambda cell: transform.map_values_to_one(["URGENT", "EMERGENCY"], "EMERGENCY", cell))
    tm_admissions.map_column_values_from(mimic_tables["ADMISSIONS"], "admission_location", "Admission Location")
    tm_admissions.map_column_values("Admission Type", lambda cell: transform.map_values_to_one(["", "** INFO NOT AVAILABLE **"], "UNKNOWN", cell))
    tm_admissions.map_column_values_from(mimic_tables["ADMISSIONS"], "discharge_location", "Discharge Location")
    tm_admissions.map_column_values_from(mimic_tables["ADMISSIONS"], "insurance", "Insurance")
    tm_admissions.map_column_values_from(mimic_tables["ADMISSIONS"], "religion", "Religion")
    tm_admissions.map_column_values("Religion", lambda cell: transform.map_values_to_one(["", "NOT SPECIFIED", "UNOBTAINABLE"], "UNKNOWN", cell))
    tm_admissions.map_column_values_from(mimic_tables["ADMISSIONS"], "marital_status", "Marital Status")
    tm_admissions.map_column_values("Marital Status", lambda cell: transform.map_values_to_one(["", "UNKNOWN (DEFAULT)"], "UNKNOWN", cell))
    tm_admissions.map_column_values_from(mimic_tables["ADMISSIONS"], "ethnicity", "Ethnicity")
    tm_admissions.map_column_values("Ethnicity", lambda cell: transform.map_values_to_one(["", "UNKNOWN/NOT SPECIFIED", "UNABLE TO OBTAIN"], "UNKNOWN", cell))
    tm_admissions.map_column_values_from(mimic_tables["ADMISSIONS"], "hospital_expire_flag", "Expired In Hospital", (lambda x: "Yes" if x == "1" else "No"))
    tm_admissions.map_from_many(mimic_tables["ADMISSIONS"], ["edregtime", "edouttime"], "Time In ED (hours)", transform.date_dif_h_fractional_with_null)

    #Calculate the post hospital survival time -> Difference between discharge time and day of death
    post_surv_time = []
    for row in range(mimic_tables["ADMISSIONS"].row_count):
        subj_id = mimic_tables["ADMISSIONS"].get("subject_id", row)
        dis_time = mimic_tables["ADMISSIONS"].get("dischtime", row)
        dod = mimic_tables["PATIENTS"].get("dod", mimic_tables["PATIENTS"].where_first("subject_id", subj_id))

        time = "0"
        if dis_time == "" or dod == "":
            log(f"Could not calculate post hospital survival time for patient {subj_id}", log_type.WARNING)
            time = "0"
        else:
            time = transform.date_dif_d([dis_time, dod])

        post_surv_time.append(time)
    tm_admissions.fill_column_array("Post Hospital Survival Time (days)", post_surv_time)

    return tm_admissions

def create_icd_table(mimic_table, hadm_to_visit, table_name, category_path, num_to_str_func):
    tm_table = table(table_name)
    tm_table.add_column("SUBJ_ID")
    tm_table.add_column("VISIT_NAME")
    tm_table.add_column("icd code", transmart.tm_column_md(category_path, transmart.tm_type.CATEGORICAL))
    meta = tm_table.column_meta("icd code")
    for i in range(mimic_table.row_count):
        seq_num = int(mimic_table.get("seq_num", i))
        tm_table.add_row([mimic_table.get("subject_id", i), str(hadm_to_visit[mimic_table.get("hadm_id", i)]), mimic_table.get("icd9_code", i)])
        sequence = num_to_str_func(seq_num)
        meta.set_cell_meta(i, sequence)

    return tm_table

def create_diagnoses_data(mimic_tables, hadm_to_subj, hadm_to_visit):
    return create_icd_table(mimic_tables["DIAGNOSES_ICD"], hadm_to_visit, "tm_diagnoses", f"Subjects+Hospital_Stays+{visit_name_path}+Medical+Diagnoses", lambda x: f"{x:02}" + (f" ({num_str_utils.number_importance(x)})" if num_str_utils.number_importance(x) != "" else ""))

def create_procedures_data(mimic_tables, hadm_to_subj, hadm_to_visit):
    return create_icd_table(mimic_tables["PROCEDURES_ICD"], hadm_to_visit, "tm_procedures", f"Subjects+Hospital_Stays+{visit_name_path}+Medical+Procedures", lambda x: f"{x:02}{num_str_utils.number_ordinal(x)}")

def create_observations(mimic_tables, hadm_to_subj, hadm_to_visit):
    pass