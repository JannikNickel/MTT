# MTT

The purpose of this repository is to demonstrate the ETL process for integrating the MIMIC-III Demo [1] intensive care data into a tranSMART instance with the ETL import tool tranSMART-batch [2] using the highdimensional data format to represent time series data.

## Content
The directory `mtt` represents a python module that reads MIMIC tables, transforms and exports them in a format that is readable by the import tool TranSMART-batch [2].

The directory `data/output/` contains a transformed result of the application, which can be imported into TranSMART. The required `study.params` and `clinical.params` definition files, which are required to import the dataset, are located in the subdirectory `data/output/MIMIC3_DEMO/` alongside with all other required data definitions. By default, the MIMIC-III tables will be loaded from the data directory, too. (Not included in this repository, link in the references).

## Running the module

### Requirements
The application is written in Python 3.8.3, but doesnt use any advanced features of the newer Python 3 versions, so any Python 3+ installation should be able to run it.
In addition, the following modules are required:
* prettytable (https://github.com/jazzband/prettytable)

All other used modules should be part of the Python 3 standard library.

### Execution
To successfully run the module and generate a tranSMART dataset you have to clone this repository and download the MIMIC-III demo dataset (link in the references).

The first step is to navigate in the directory of the cloned repository.
By default the MIMIC-III tables are expected to be located in the directory `/data/input/mimic-iii-clinical-database-demo-1.4/` as `.csv` files. The path can be changed as described later on.

After moving the MIMIC files to the right location, navigate back in the repository directory and run the python program with the command

```python -m mtt```

It's important to run the application from the root of the repository, because the default configuration uses relative paths, which will only work in that working directory.

By default you can find the transformed data in the `/data/output/` folder as a zip file and a directory.

### Configuration
To adjust settings like the import/export path and settings of the dataset, you can modify the variables in the file `config.py`.

## Module source
Below is a short description of all source files in the python module.

| Source file | Description |
| ----------- | ----------- |
| \_\_init.py\_\_ | Empty (module definition) |
| \_\_main.py\_\_ | Controls the ETL-process by calling all required functions in order. |
| ascii.py        | Converts strings to ASCII encoded int arrays |
| config.py       | Contains all required configuration variables for paths, names and file information |
| log.py          | Uses `print` to display formatted log messages with time and log level to the console |
| mimic_items.py  | Item definition for patient messurements and observations + helper methods to convert messurement formats |
| mimic.py        | Functions to load the MIMIC-III dataset into tables and constants about the MIMIC-III data format like Datetimes |
| num_str_utils.py| Helper methods to convert numbers to strings |
| params_file.py  | Create/read/write `.params` files (each line: key=value). The files are required for study definitions |
| T.py            | Contains all functions to transform the MIMIC-III tables into data tables for the import in tranSMART |
| table.py        | A class to create/load/write/copy/modify 2 dimensional table data in various ways as well as definining and generating meta data about columns (data type, number different values, hierarchy path, ...). All methods are documented in the source file. |
| transform.py    | Contains helper functions to calculate differences between datetimes, ... |
| transmart.py    | Transformes the generated data tables into the required format for tranSMART-batch and writes the study folder |


## References
[1] Johnson, A., Pollard, T., & Mark, R. (2019). MIMIC-III Clinical Database Demo (version 1.4). PhysioNet. https://doi.org/10.13026/C2HM2Q

[2] https://github.com/thehyve/transmart-batch
