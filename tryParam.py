import streamlit as st
from paramiko import SSHClient, AutoAddPolicy
from rich import print, pretty, inspect
import subprocess
pretty.install()
import os
import subprocess


host = os.getenv('HOST')
user = os.getenv('USER')
password = os.getenv('PASSWORD')

def upload_directory(sftp, local_path, remote_path):
    """Recursively upload a directory with all its files and subdirectories."""
    # Ensure the remote directory exists
    try:
        sftp.mkdir(remote_path)
    except IOError:  # Directory already exists
        pass

    for item in os.listdir(local_path):
        local_item_path = os.path.join(local_path, item)
        remote_item_path = f"{remote_path}/{item}".replace("\\", "//")  # Ensure proper path format for remote
        
        
        if os.path.isdir(remote_item_path):
            # Recursively upload subdirectories
            upload_directory(sftp, remote_item_path, local_item_path)
        else:
            # Upload individual file
            sftp.put(remote_item_path, local_item_path)
            print(f"Uploaded: {local_item_path} to {remote_item_path}")
            
            
folder_path = r'E:\\Fibro\\prep_outputs'

os.mkdir(folder_path)

list_of_subjects_transfer = []
list_of_transfered= []


client = SSHClient() 

known_hosts_path = os.path.expanduser('~/.ssh/known_hosts')
client.load_host_keys(known_hosts_path)
client.load_system_host_keys()

client.set_missing_host_key_policy(AutoAddPolicy())

client.connect(host, username=user, password=password)



sftp_session = client.open_sftp()
client.set_log_channel('DEBUG')

sftp_session.chdir('fMRIprep/outputs')

selected_subject = r'sub-266'
sub_folder = os.path.join(folder_path)
upload_directory(sftp_session, sub_folder, 'fMRIprep/')
# sftp_session.put(fr'{folder_path}\\{selected_subject}', f'{selected_subject}')

print(f'List of files: {sftp_session.listdir()}')

list_of_transfered = [f for f in sftp_session.listdir() if f.startswith('sub-')]

client.close()
sftp_session.close()