from . import config as cfg
from .log import log, log_type
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

#Function for generic numerical/categorical data loading with measurement times. Returns (value, datetime) and None for invalid data rows
def load_value_entry(source_table: table, row: int, source_column: str, is_numerical: bool, time_column: str = None, value_modifier=None, value_limits=None, error_column_index: int=-1):
    value = source_table.get(source_column, row)
    datetime = None

    #Skip null values
    if value == "":
        return (None, None)

    #Cast numeric values and skip non numeric values in numeric variables
    if is_numerical == True:
        try:
            value = float(value)
        except ValueError:
            return (None, None)

    #Skip invalid measurments (column "error" (0/1) in some tables), some items contain wrong negative values without the error flag (e.g. blood pressure)
    if (error_column_index != -1 and source_table[error_column_index, row] == "1") or (is_numerical == True and value < 0):
        return (None, None)

    #Modify item based on a given function
    if value_modifier != None:
        value = value_modifier(value)

    #Skip out of bounds numeric values
    if is_numerical == True and value_limits != None:
        if value < value_limits[0] or value > value_limits[1]:
            return (None, None)
    
    #Normalize and skip certain categorical values
    if is_numerical == False:
        value = value.title()
        if value == "Other/Remarks":
            return (None, None)

    #Extract datetime (charttime is most accurate)
    if time_column != None:
        datetime = source_table.get(time_column, row)
        try:
            datetime = dt.datetime.strptime(datetime, mimic.time_format)
        except ValueError:
            return (None, None)#Skip entries with invalid times

    return (value, datetime)

def create_item_def_tables_task(task_name, mimic_table, hadm_to_subj, hadm_to_visit, item_definitions, table_base_name, value_category_path, time_column_name, error_column_name):
    log(task_name)
    tm_tables = []

    #GROUP by mapped item ids (MIMIC-III id -> tranSMART target name)
    map_id_to_target = lambda id: (
        filtered := [x for x in item_definitions if x.id == id],
        filtered[0].target if len(filtered) > 0 else "Unmapped"
    )[-1]
    item_groups = mimic_table.group_by("itemid", lambda x: map_id_to_target(x))
    item_groups.pop("Unmapped", None)#Remove unmapped data

    #Iterate through target items
    for item_key in item_groups:
        log(f"Creating item table {item_key}", log_type.STEP)

        item_def = [x for x in item_definitions if x.target == item_key][0]

        #Create a table for this item group
        item_table = table(f"tm_{table_base_name}_" + item_key)
        item_table.add_column("SUBJ_ID")
        item_table.add_column("VISIT_NAME")
        tmtype = transmart.tm_type.NUMERICAL if item_def.numeric else transmart.tm_type.CATEGORICAL
        item_table.add_column("value", transmart.tm_column_md(f"{value_category_path}+{item_key}", tmtype))
        tm_tables.append(item_table)
        column_meta = item_table.column_meta("value")
        error_column = mimic_table.column_index(error_column_name)

        #GROUP the rows of this item group by hospital admissions
        hadm_groups = mimic_table.group_by("hadm_id", func=None, limited_rows=item_groups[item_key])

        #Iterate through all hospital admissions
        for h_key, h_rows in hadm_groups.items():
            subj_id = mimic_table.get("subject_id", h_rows[0])
            hadm_id = mimic_table.get("hadm_id", h_rows[0])
            item_id = mimic_table.get("itemid", h_rows[0])

            #Iterate through each item entry for this hospital admission and load the data
            i = 0#Count number for each entry as metadata
            for row in h_rows:
                #Load data row
                value, datetime = load_value_entry(mimic_table, row, item_def.source, item_def.numeric, time_column_name, item_def.modifier, item_def.limits, error_column)
                if value == None or datetime == None:#Invalid result
                    continue
                
                #Add row and set entry number as metadata
                item_table.add_row([subj_id, hadm_to_visit[hadm_id], value])
                column_meta.set_cell_meta(item_table.row_count - 1, transmart.tm_cell_md(f"{i:06}", datetime))
                i += 1
    
    return tm_tables

def create_observations_data(mimic_tables, hadm_to_subj, hadm_to_visit):
    return create_item_def_tables_task("Observation data",
        mimic_tables["CHARTEVENTS"],
        hadm_to_subj,
        hadm_to_visit,
        mimic_items.observation_items,
        "observation",
        f"Subjects+Hospital_Stays+{visit_name_path}+Medical+Observations",
        "charttime",
        "error")

def create_lab_data(mimic_tables, hadm_to_subj, hadm_to_visit):
    log("Lab data")
    m_lab = mimic_tables["LABEVENTS"]
    m_items = mimic_tables["D_LABITEMS"]
    tm_lab_tables = []

    #Group by items
    item_groups = m_lab.group_by("itemid")
    #Iterate through the items and create one table for each item
    for item_key in item_groups:
        log(f"Creating item table {item_key}", log_type.STEP)

        #Skip lab items with very few occurrences
        if len(item_groups[item_key]) < 100:
            continue

        #Find item definition
        item_def_row = m_items.where_first("itemid", item_key)
        item_name = m_items.get("label", item_def_row)
        item_fluid = m_items.get("fluid", item_def_row)

        #Determine item type (> 50% numbers => numerical item)
        numerical_value_count = 0
        item_rows = item_groups[item_key]
        for i in item_rows:
            value = m_lab.get("value", i)
            if value.replace('.', '', 1).replace('-', '', 1).isdigit():
                numerical_value_count += 1
        is_numerical = numerical_value_count > len(item_rows) * 0.5
        tmtype = transmart.tm_type.NUMERICAL if is_numerical else transmart.tm_type.CATEGORICAL

        #Determine unit for numerical item (For LABEVENTS, units are either missing or consistent for each item => Search first non null value)
        unit = ""
        if tmtype == transmart.tm_type.NUMERICAL:
            for i in item_rows:
                u = m_lab.get("valueuom", i)
                if u != "":
                    unit = u
                    break

        #Create table for this item
        item_table = table("tm_lab_" + item_key)
        item_table.add_column("SUBJ_ID")
        item_table.add_column("VISIT_NAME")
        item_table.add_column("value", transmart.tm_column_md(f"Subjects+Hospital_Stays+{visit_name_path}+Medical+Lab+{item_fluid}+{item_name}", tmtype))
        tm_lab_tables.append(item_table)
        column_meta = item_table.column_meta("value")

        #GROUP the rows of this item by hospital admissions
        hadm_groups = m_lab.group_by("hadm_id", func=None, limited_rows=item_groups[item_key])
        for h_key, h_rows in hadm_groups.items():
            #Load data entries for this admission
            subj_id = m_lab.get("subject_id", h_rows[0])
            item_id = m_lab.get("itemid", h_rows[0])
            i = 0
            for h_row in h_rows:
                #Labevents contains results from external sources (no hadm_id specified) -> Skip those
                hadm_id = m_lab.get("hadm_id", h_rows[0])
                if hadm_id == "":
                    continue

                #Load data row
                value, datetime = load_value_entry(m_lab, h_row, "value", is_numerical, "charttime")
                if value == None or datetime == None:#Invalid result
                    continue
                
                #Add row and set entry number as metadata
                item_table.add_row([subj_id, hadm_to_visit[hadm_id], value])
                column_meta.set_cell_meta(item_table.row_count - 1, transmart.tm_cell_md(f"{i:06}", datetime))
                i += 1
            
    log("Lab data")
    return tm_lab_tables

def create_icu_stay_data(mimic_tables, hadm_to_subj, hadm_to_visit):
    log("ICU stay data")
    m_transfers = mimic_tables["TRANSFERS"]
    
    #Create table
    t_table = table(f"tm_icustays")
    t_table.add_column("SUBJ_ID")
    t_table.add_column("VISIT_NAME")
    t_table.add_column("value", transmart.tm_column_md(f"Subjects+Hospital_Stays+{visit_name_path}+Administration+ICU", transmart.tm_type.CATEGORICAL))
    column_meta = t_table.column_meta("value")

    #GROUP by hospital admissions
    stay_groups = m_transfers.group_by("hadm_id")
    for key, rows in stay_groups.items():
        #Add all transfers of this admission
        i = 0
        for row in rows:
            subj_id = m_transfers.get("subject_id", row)
            hadm_id = m_transfers.get("hadm_id", row)
            eventtype = m_transfers.get("eventtype", row)
            careunit = m_transfers.get("curr_careunit", row)
            datetime = m_transfers.get("intime", row)

            #Discharge entries are not relevant, because the patient got released from the hospital
            if eventtype == "discharge":
                continue

            #Transform icu abbreviation to full name
            careunit = transform.icu_to_full_name(careunit)

            #Load datetime
            try:
                datetime = dt.datetime.strptime(datetime, mimic.time_format)
            except ValueError:
                continue

            #Add row to table
            t_table.add_row([subj_id, hadm_to_visit[hadm_id], careunit])
            column_meta.set_cell_meta(t_table.row_count - 1, transmart.tm_cell_md(f"{i:02}", datetime))
            i += 1

    return t_table

def create_services_data(mimic_tables, hadm_to_subj, hadm_to_visit):
    log("Service data")
    m_services = mimic_tables["SERVICES"]
    
    #Create table
    t_table = table(f"tm_services")
    t_table.add_column("SUBJ_ID")
    t_table.add_column("VISIT_NAME")
    t_table.add_column("value", transmart.tm_column_md(f"Subjects+Hospital_Stays+{visit_name_path}+Administration+Services", transmart.tm_type.CATEGORICAL))
    column_meta = t_table.column_meta("value")

    #GROUP by hospital admissions
    stay_groups = m_services.group_by("hadm_id")
    for key, rows in stay_groups.items():
        #Add all transfers of this admission
        i = 0
        for row in rows:
            subj_id = m_services.get("subject_id", row)
            hadm_id = m_services.get("hadm_id", row)
            service = m_services.get("curr_service", row)
            datetime = m_services.get("transfertime", row)

            #Load datetime
            try:
                datetime = dt.datetime.strptime(datetime, mimic.time_format)
            except ValueError:
                continue

            #Add row to table
            t_table.add_row([subj_id, hadm_to_visit[hadm_id], service])
            column_meta.set_cell_meta(t_table.row_count - 1, transmart.tm_cell_md(f"{i:02}", datetime))
            i += 1

    return t_table

def create_output_data(mimic_tables, hadm_to_subj, hadm_to_visit):
    return create_item_def_tables_task("Output data",
        mimic_tables["OUTPUTEVENTS"],
        hadm_to_subj,
        hadm_to_visit,
        mimic_items.output_items,
        "output",
        f"Subjects+Hospital_Stays+{visit_name_path}+Medical+Output",
        "charttime",
        "")

def create_input_data(mimic_tables, hadm_to_subj, hadm_to_visit):
    log("Merging input tables...")
    #Merge input tables from CareVue and MetaVision
    m_carevue = mimic_tables["INPUTEVENTS_CV"]
    m_metavision = mimic_tables["INPUTEVENTS_MV"]

    m_input = table("INPUTEVENTS")
    column_map = lambda x: "charttime" if x == "starttime" else x #Datetime is different between CareVue and MetaVision
    for i in range(m_carevue.column_count):
        #Find all columns that exist in both tables (or can be mapped by column_map lambda)
        cv_column = m_carevue.column_name(i)
        column = column_map(cv_column)
        mv_column = None
        for k in range(m_metavision.column_count):
            if column_map(m_metavision.column_name(k)) == column:
                mv_column = m_metavision.column_name(k)
                break
        if mv_column != None:
            #Copy the column values from both tables to the new table
            m_input.add_column(column)
            table.map_column(m_carevue, m_input, cv_column, column, None, 0)
            table.map_column(m_metavision, m_input, mv_column, column, None, m_carevue.row_count)

    log("Input data")
    m_items = mimic_tables["D_ITEMS"]
    tm_tables = []
    #GROUP by item
    item_groups = m_input.group_by("itemid").items()
    for item_key, item_rows in item_groups:
        log(f"Creating item table {item_key}", log_type.STEP)

        #Skip items with less than 100 entries
        if len(item_rows) < 100:
            continue

        #Find item definition in D_ITEMS
        item_def_row = m_items.where_first("itemid", item_key)
        item_lbl = m_items.get("label", item_def_row)
        is_cv = (int(m_items.get("itemid", item_def_row)) < 200000)

        #Try to automatically find the unit for this item
        unit_groups = m_input.group_by("amountuom", limited_rows=item_rows)                    #Group by occurring units
        units = [x for x in unit_groups.keys() if x != ""]
        unit = max(unit_groups.keys(), key=lambda x: len(unit_groups[x]) if x != "" else 0) #Find the most occurring unit
        rate_unit_groups = m_input.group_by("rateuom", limited_rows=item_rows)                 #Find all possible rate units for this item
        rate_units = [x for x in rate_unit_groups.keys() if x != ""]
        rate_unit = max(rate_unit_groups.keys(), key=lambda x: len(rate_unit_groups[x]) if x != "" else 0).replace("/", " ")    #Find most occuring rate unit

        #Warning if multiple units exists for this item
        if len(units) > 1 or len(rate_units) > 1:
            log(log_type.WARNING, f"Input Item {item_lbl} ({item_key}) uses multiple units! {len([x for x in units if x != unit])} entries will be skipped")

        #Create a table for this item
        db_path = "CareVue" if is_cv == True else "Metavision"
        path = f"Subjects+Hospital_Stays+{visit_name_path}+Medical+Input+{db_path}+{item_lbl} ({unit})"
        i_table = table(f"tm_input_{item_key}")
        i_table.add_column("SUBJ_ID")
        i_table.add_column("VISIT_NAME")
        i_table.add_column("value", transmart.tm_column_md(path, transmart.tm_type.NUMERICAL))
        tm_tables.append(i_table)
        column_meta = i_table.column_meta("value")

        #Group by hospital admissions
        h_groups = m_input.group_by("hadm_id", limited_rows=item_rows)
        for h_key, h_rows in h_groups.items():
            i = 0
            for row in h_rows:
                subject_id = m_input.get("subject_id", row)
                hadm_id = m_input.get("hadm_id", row)
                amount = m_input.get("amount", row)
                amountuom = m_input.get("amountuom", row)
                rate = m_input.get("rate", row)
                rateuom = m_input.get("rateuom", row)

                #Skip null values
                if amount == "":
                    continue

                #Skip the entries with different units (3 in total)
                if amountuom != unit:
                    continue

                #Load value
                amount = float(amount)
                if amount <= 0:#Sometimes there are 0/negative entries in the CareVue database when a rate got set
                    continue

                #Load datetime
                datetime = m_input.get("charttime", row)
                try:
                    datetime = dt.datetime.strptime(datetime, mimic.time_format)
                except ValueError:
                    continue#Skip entries with invalid times

                i_table.add_row([subject_id, hadm_to_visit[hadm_id], amount])
                column_meta.set_cell_meta(i_table.row_count - 1, transmart.tm_cell_md(f"{i:06}", datetime))
                i += 1

    log("Input data")
    return tm_tables
