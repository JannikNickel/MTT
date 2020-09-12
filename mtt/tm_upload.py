import paramiko
import shutil
import os
from zipfile import ZipFile, ZIP_DEFLATED
import ctypes
import time
import os.path

from .log import log_type, log, log_progress_bar
from . import secrets
from . import config as cfg

cd_docker_cmd = "cd " + cfg.docker_path + " ; "
double_backslash = "\\\\"
remove_old_data_cmd = f'docker-compose exec tmbatch touch /tmp/backout.params && docker-compose exec tmbatch /opt/git/transmart-batch/transmart-batch.jar -c /opt/git/transmart-batch/batchdb.properties -n -p /tmp/backout.params -d TOP_NODE="{(cfg.study_top_node + double_backslash)}" -d STUDY_ID={cfg.study_id}'

#study_path is expected to be a directory path relative from cfg.output_path and ends with /
def upload_data(study_path):
    cwd = os.getcwd().replace("\\", "/")
    compressed_path = cfg.output_path + study_path.rstrip("/") + ".zip"
    study_path = cfg.output_path + study_path
    
    log("Connecting to " + secrets.tmserver_address + "...", log_type.INFO)

    #Connect via ssh
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(secrets.tmserver_address, username=secrets.tmserver_user, password=secrets.tmserver_password)

    #Compress dataset
    log("Compressing dataset...", log_type.INFO)
    with ZipFile(compressed_path, "w", ZIP_DEFLATED) as zip:
        for dir_name, subdirs, files in os.walk(study_path):
            for file in files:
                file_path = os.path.join(dir_name, file)
                zip.write(file_path, file_path.replace(cfg.output_path, ""))

    #Delete old transmart data
    log("Removing old data...", log_type.INFO)
    stdin, stdout, stderr = client.exec_command(cd_docker_cmd + remove_old_data_cmd, get_pty=True)
    for line in stdout:#Wait for EOF
        l = line.strip("\n")
        print(l)

    time.sleep(0.5)

    #Upload data to listener directory
    log("Uploading dataset...", log_type.INFO)
    log_progress_bar(0.0)
    sftp = client.open_sftp()
    sftp.put(compressed_path, cfg.incoming_data_path + "../" + cfg.study_id + ".zip", callback=lambda a, b: log_progress_bar(float(a) / float(b)), confirm=True)
    sftp.rename(cfg.incoming_data_path + "../" + cfg.study_id + ".zip", cfg.incoming_data_path + cfg.study_id + ".zip")
    sftp.close()

    #Display import log
    log("Displaying tmbatch log...", log_type.INFO)
    stdin, stdout, stderr = client.exec_command(cd_docker_cmd + "docker-compose logs -f --tail 0 tmbatch")
    for line in stdout:#Wait for EOF
        l = line.strip("\n")
        print(l)
        if "Cleaning up workspace ... ready. Waiting for new files." in l:
            break

    client.close()