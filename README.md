# MTT

The purpose of this repository is to demonstrate the ETL process for integrating the MIMIC-III Demo [1] intensive care data into a docker-based TranSMART 16.2 instance [2] using the HD-Data format to represent time series data.

## Content
The directory `mtt` represents a python module that reads MIMIC tables, transforms and exports them in a format that is readable by the import tool TranSMART-batch [3].

The directory `data/output` contains a transformed result of the application, which can be imported into TranSMART. The required `study.params` and `clinical.params` definition files, which are required to import the dataset, are located in the subdirectory `data/MIMIC3_DEMO/` and the column mapping and data files are can be found in the directory `data/MIMIC3_DEMO/clinical/`. By default, the MIMIC-III tables will be loaded from the data directory, too. (Not included in this repository, link in the references).

## Running the module

### Requirements
The application is written in Python 3.8.3, but doesnt use any advanced features of the newer Python 3 versions, so any Python 3+ installation should be able to run it.
In addition, the following modules are required:
* paraminko (https://github.com/paramiko/paramiko)
* prettytable (https://github.com/jazzband/prettytable)

All other used modules should be part of the Python standard library.

### Execution
To successfully execute the module and generate a TranSMART dataset you have to clone this repository and download the MIMIC-III demo dataset (link in the references).

The first step is to navigate in the directory of the cloned repository.
By default the MIMIC-III tables are expected to be located in the directory `/data/input/mimic-iii-clinical-database-demo-1.4/` as `.csv` files. The path can be changed as described later on.

After moving the MIMIC files to the right location, navigate back in the repository directory and run the python program with the command

```python -m mtt```

It's important to run the application from the specified path, because the default configuration uses relative paths, which will only work in that working directory.

By default you can find the transformed data in the `/data/output/MIMIC3_DEMO` folder.
The application will ask whether you want to upload the data to transmart. If your server settings are correctly set up, you can automatically remove old data, generate a zip file, copy and import the new data via ssh. However, this also requires some writing permissions on the server.

### Configuration
To adjust settings like the import/export path and settings of the dataset, you can modify the variables in the file `config.py`. To allow the program to automatically update the transformed data, you also have to provide values for the variables in the file `secrets.py` to directly upload the files. In addition to that, you have to make sure that your provided login values have read/write permissions in the folders of the `OPT docker volume`

## Module source
Below is a short description of all source files in the python module.

TODO

## References
[1] Johnson, A., Pollard, T., & Mark, R. (2019). MIMIC-III Clinical Database Demo (version 1.4). PhysioNet. https://doi.org/10.13026/C2HM2Q

[2] https://gitlab.gwdg.de/medinfpub/tm_umg

[3] https://github.com/thehyve/transmart-batch