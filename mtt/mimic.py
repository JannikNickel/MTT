"""Module that contains data descriptions of the mimic-III database and methods to extract and transform data from it"""
from . import config as cfg
from .log import log, log_progress_bar, log_type
from .table import table

#Formats
file_delimiter = ","
file_ending = ".csv"
date_format = "%Y-%m-%d"
time_format = "%Y-%m-%d %H:%M:%S"

#Data
table_names = [
    "ADMISSIONS",
    "CALLOUT",
    "CAREGIVERS",
    "CHARTEVENTS",
    "CPTEVENTS",
    "D_CPT",
    "D_ICD_DIAGNOSES",
    "D_ICD_PROCEDURES",
    "D_ITEMS",
    "D_LABITEMS",
    "DATETIMEEVENTS",
    "DIAGNOSES_ICD",
    "DRGCODES",
    "ICUSTAYS",
    "INPUTEVENTS_CV",
    "INPUTEVENTS_MV",
    "LABEVENTS",
    "MICROBIOLOGYEVENTS",
    "OUTPUTEVENTS",
    "PATIENTS",
    "PRESCRIPTIONS",
    "PROCEDUREEVENTS_MV",
    "PROCEDURES_ICD",
    "SERVICES",
    "TRANSFERS"
]

class mimiciii():
    def __init__(self):
        self._tables = {}

    @property
    def tables(self):
        return self._tables

    @staticmethod
    def load_dataset(path):
        log("Loading MIMIC-III tables...")
        m = mimiciii()
        table_count = len(table_names)

        log_progress_bar(0.0)
        for i in range(table_count):
            p = cfg.getcwd() + path + table_names[i] + file_ending
            m._tables[table_names[i]] = table.load_csv(p)
            log_progress_bar(i / float(table_count))
        log_progress_bar(1.0)
        return m
        
