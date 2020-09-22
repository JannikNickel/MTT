from . import config as cfg
from .log import log, log_type, log_with_percent
from .table import table
from . import mimic
from . import transmart
from . import transform
from . import num_str_utils
from . import mimic_items

import datetime as dt

#Settings
visit_name_path = "Visit_" + transmart.visitname_placeholder

def create_patients_data(mimic_tables, hadm_to_subj, hadm_to_visit):
    log("Patient data")
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
    log("Admissions data")
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
        meta.set_cell_meta(i, transmart.tm_cell_md(sequence))

    return tm_table

def create_diagnoses_data(mimic_tables, hadm_to_subj, hadm_to_visit):
    log("Diagnoses data")
    return create_icd_table(mimic_tables["DIAGNOSES_ICD"], hadm_to_visit, "tm_diagnoses", f"Subjects+Hospital_Stays+{visit_name_path}+Medical+Diagnoses", lambda x: f"{x:02}" + (f" ({num_str_utils.number_importance(x)})" if num_str_utils.number_importance(x) != "" else ""))

def create_procedures_data(mimic_tables, hadm_to_subj, hadm_to_visit):
    log("Procedures data")
    return create_icd_table(mimic_tables["PROCEDURES_ICD"], hadm_to_visit, "tm_procedures", f"Subjects+Hospital_Stays+{visit_name_path}+Medical+Procedures", lambda x: f"{x:02}{num_str_utils.number_ordinal(x)}")

def create_observations_data(mimic_tables, hadm_to_subj, hadm_to_visit):
    log_with_percent("Observation data", 0.0)
    m_chart = mimic_tables["CHARTEVENTS"]
    tm_observation_tables = []

    #GROUP by mapped item ids (MIMIC-III id -> tranSMART target name)
    map_id_to_target = lambda id: (
        filtered := [x for x in mimic_items.observation_items if x.id == id],
        filtered[0].target if len(filtered) > 0 else "Unmapped"
    )[-1]
    item_groups = m_chart.group_by("itemid", lambda x: map_id_to_target(x))
    item_groups.pop("Unmapped", None)#Remove unmapped data

    #Iterate through target items
    group_progress = 0
    for item_key in item_groups:
        group_progress += 1
        log_with_percent("Observation data", min((group_progress / float(len(item_groups))), 0.999))

        first_item_def = [x for x in mimic_items.observation_items if x.target == item_key][0]

        #Create a table for this item group
        item_table = table("tm_observation_" + item_key)
        item_table.add_column("SUBJ_ID")
        item_table.add_column("VISIT_NAME")
        tmtype = transmart.tm_type.NUMERICAL if first_item_def.numeric else transmart.tm_type.CATEGORICAL
        item_table.add_column("value", transmart.tm_column_md(f"Subjects+Hospital_Stays+{visit_name_path}+Medical+Observations+{item_key}", tmtype))
        #TODO date with special placeholder
        tm_observation_tables.append(item_table)
        column_meta = item_table.column_meta("value")

        #GROUP the rows of this item group by hospital admissions
        hadm_groups = m_chart.group_by("hadm_id", func=None, limited_rows=item_groups[item_key])

        #Iterate through all hospital admissions
        for h_key, h_rows in hadm_groups.items():
            subj_id = m_chart.get("subject_id", h_rows[0])
            hadm_id = m_chart.get("hadm_id", h_rows[0])
            item_id = m_chart.get("itemid", h_rows[0])
            item_def = [x for x in mimic_items.observation_items if x.id == item_id][0]

            #Iterate through each item entry for this hospital admission and load the data
            i = 0#Count number for each entry as metadata
            for row in h_rows:
                value = m_chart.get(item_def.source, row)
                datetime = None

                #Skip null values
                if value == "":
                    continue

                #Cast numeric values and skip non numeric values in numeric variables
                if item_def.numeric == True:
                    try:
                        value = float(value)
                    except ValueError:
                        continue

                #Modify item based on a given function
                if item_def.modifier != None:
                    value = item_def.modifier(value)

                #Skip out of bounds numeric values
                if item_def.numeric == True and item_def.limits != None:
                    if value < item_def.limits[0] or value > item_def.limits[1]:
                        continue
                
                #Normalize and skip certain categorical values
                if item_def.numeric == False:
                    value = value.title()
                    if value == "Other/Remarks":
                        continue

                #Extract datetime (charttime is most accurate)
                datetime = m_chart.get("charttime", row)
                try:
                    datetime = dt.datetime.strptime(datetime, mimic.time_format)
                except ValueError:
                    continue#Skip entries with invalid times
                
                #Add row and set entry number as metadata
                item_table.add_row([subj_id, hadm_to_visit[hadm_id], value])
                column_meta.set_cell_meta(item_table.row_count - 1, transmart.tm_cell_md(f"{i:06}", datetime))
                i += 1

    log_with_percent("Observation data", 1.0)
    return tm_observation_tables
