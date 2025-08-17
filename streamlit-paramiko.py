import streamlit as st
from paramiko import SSHClient, AutoAddPolicy
from rich import print, pretty, inspect
import subprocess
pretty.install()
import os
import webview
from flask import Flask
from dotenv import load_dotenv
import stat
from datetime import datetime
import posixpath

import subprocess

st.set_page_config(page_title='fMRIprep management', page_icon=':brain:', layout='wide')

load_dotenv()  

# Load environment variables from .env file
host = os.getenv('HOST')
user = os.getenv('USER')
password = os.getenv('PASSWORD')

def _ensure_remote_dir(sftp, remote_dir: str):
    remote_dir = remote_dir.replace("\\", "/").rstrip("/")
    if not remote_dir:
        return
    parts = [p for p in remote_dir.split("/") if p]
    path = "/" if remote_dir.startswith("/") else ""
    for p in parts:
        path = posixpath.join(path, p) if path else p
        try:
            sftp.stat(path)
        except IOError:
            sftp.mkdir(path)

def main():
    host = os.getenv('HOST')
    user = os.getenv('USER')
    password = os.getenv('PASSWORD')
    user_admin = os.getenv('USER_ADMIN')
    password_admin = os.getenv('PASSWORD_ADMIN')


    if 'selected_subject' not in st.session_state:
        st.session_state.selected_subject = None
        
    if 'selected_subjects_run' not in st.session_state:
        st.session_state.selected_subjects_run = None
        
    if 'selected_output_folder' not in st.session_state:
        st.session_state.selected_output_folder = None
        
    if 'list_of_transfered' not in st.session_state:
        st.session_state.list_of_transfered = []

    def download_directory(sftp, remote_path, local_path):
        """
        Recursively downloads a directory from the remote server to the local machine.

        Args:
            sftp: An active Paramiko SFTP session.
            remote_path: Path to the remote directory to download.
            local_path: Path to the local directory where files will be downloaded.
        """
        # Ensure the local directory exists
        if not os.path.exists(local_path):
            os.makedirs(local_path)
        if not is_remote_dir(sftp, remote_path):
            if 'html' in remote_path:
                try:
                    sftp.get(remote_path, local_path)
                    return
                except Exception as e:
                    print(f"No html file found at {remote_path}: {e}")
                    st.warning(f"No html file found at {remote_path}: {e}")
                    return
        # List all items in the remote directory
        for item in sftp.listdir(remote_path):
            remote_item_path = f"{remote_path}/{item}"
            local_item_path = os.path.join(local_path, item)

            try:
                # Check if the remote item is a directory
                if is_remote_dir(sftp, remote_item_path):
                    # Recursively download subdirectories
                    download_directory(sftp, remote_item_path, local_item_path)
                else:
                    # Download individual files
                    sftp.get(remote_item_path, local_item_path)
                    print(f"Downloaded file: {remote_item_path} to {local_item_path}")
            except Exception as e:
                print(f"Error downloading {remote_item_path}: {e}")


    def is_remote_dir(sftp, remote_path):
        """
        Checks if a remote path is a directory.

        Args:
            sftp: An active Paramiko SFTP session.
            remote_path: Path to check.

        Returns:
            bool: True if the path is a directory, False otherwise.
        """
        try:
            return stat.S_ISDIR(sftp.stat(remote_path).st_mode)
        except IOError:
            return False
                    
                    
    def _ensure_remote_dir(sftp, remote_dir: str):
        remote_dir = remote_dir.replace("\\", "/").rstrip("/")
        if not remote_dir:
            return
        parts = [p for p in remote_dir.split("/") if p]
        path = "/" if remote_dir.startswith("/") else ""
        for p in parts:
            path = posixpath.join(path, p) if path else p
            try:
                sftp.stat(path)
            except IOError:
                sftp.mkdir(path)

        
    def remove_remote_directory(sftp, remote_path):
        """Recursively remove a directory on the remote server."""
        for item in sftp.listdir_attr(remote_path):
            remote_item_path = f"{remote_path}/{item.filename}".replace("\\", "//")
            if stat.S_ISDIR(item.st_mode):
                remove_remote_directory(sftp, remote_item_path)
            else:
                sftp.remove(remote_item_path)
        sftp.rmdir(remote_path)

    def upload_directory(sftp, local_path, remote_path):
        """Recursively upload a directory with all its files and subdirectories."""
        # Ensure the remote directory does not exist
        local_dir = os.path.abspath(local_path)
        remote_dir = remote_path.replace("\\", "/").rstrip("/")
        
        if not os.path.isdir(local_dir):
            st.warning(f"Local path '{local_dir}' is not a directory.")
            return
        
        _ensure_remote_dir(sftp, remote_dir)
        try:
            sftp.stat(remote_path)
            remove_remote_directory(sftp, remote_path)
        except IOError:  # Directory does not exist
            pass

        # Create the remote directory
        sftp.mkdir(remote_path)

        for item in os.listdir(local_path):
            local_item_path = os.path.join(local_dir, item)
            remote_item_path = posixpath.join(remote_dir, item)  
            
            # remote_item_path = f"{remote_path}/{item}".replace("\\", "//")  # Ensure proper path format for remote

            if os.path.isdir(local_item_path):
                # Recursively upload subdirectories
                _ensure_remote_dir(sftp, remote_item_path)
                upload_directory(sftp, local_item_path, remote_item_path)
            elif os.path.isfile(local_item_path):
                _ensure_remote_dir(sftp, posixpath.dirname(remote_item_path))
                try:
                    sftp.put(local_item_path, remote_item_path)
                except IOError as e:
                    st.error(f"Failed to upload {local_item_path} to {remote_item_path}: {e}")
                    
            else:
                # Upload individual file
                sftp.put(local_item_path, remote_item_path)
                print(f"Uploaded: {local_item_path} to {remote_item_path}")
        st.write(f"Uploaded: {local_item_path} to {remote_item_path}")
        



    st.title('Streamlit fMRIprep management')



    st.write('Convert nifti to BIDS format')
    
    if st.button('Convert to BIDS'):
        command = rf'python "C:\Users\PsyLab-6028\Documents\GitHub\fMRIprepStreamlitPub\A stand alone .py" '
        # subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        
        # print('Conversion to BIDS format finished')
        with st.status('Converting to BIDS...', expanded=True) as status:
            log_placeholder = st.empty()
            log = ""
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                encoding='utf-8',
                errors='replace'
            )
            for line in iter(process.stdout.readline, ''):
                if not line:
                    break
                log += line
                log_placeholder.code(log)
            process.stdout.close()
            ret = process.wait()
            if ret == 0:
                status.update(label='Conversion finished', state='complete')
            else:
                status.update(label=f'Conversion failed (exit {ret})', state='error')

    st.write('This is a simple Streamlit app to manage fMRIprep on the server')

    st.write('Show available files on the fMRIpre folder of the server')

    list_fMRIprep_available_subs = []

    if st.button('Connect to server'):
        client = SSHClient() 
        
        
        

        known_hosts_path = os.path.expanduser('~/.ssh/known_hosts')
        client.load_host_keys(known_hosts_path)
        client.load_system_host_keys()

        client.set_missing_host_key_policy(AutoAddPolicy())
        print(f'Connecting to {host} as {user}')
        client.connect(host, username=user_admin, password=password_admin)



        sftp_session = client.open_sftp()
        client.set_log_channel('DEBUG')
        print(f'Current directory: {sftp_session.getcwd()}')
        sftp_session.chdir('..')
        sftp_session.chdir('..')
        sftp_session.chdir('media/psylab-6028/DATA/fMRIprep/fibro/selectedSubs/')
        # print(f'Current directory: {sftp_session.getcwd()}')  
        print(f'List of files: {sftp_session.listdir()}')
        
        list_fMRIprep_available_subs = [f for f in sftp_session.listdir() if f.startswith('sub-')]
        
        client.close()
        sftp_session.close()
        
    st.write('List of files in the fMRIprep folder')
    st.write(list_fMRIprep_available_subs)

    st.divider()

    st.write('Select a folder to transfer from the local machine to the server')

    folder_path = r'E:\Fibro\BIDS_output'

    list_subjects = os.listdir(folder_path)

    selected_subject = st.selectbox('Select a subject', list_subjects)

    if selected_subject != None:
        st.session_state.selected_subject = selected_subject
        
    list_of_subjects_transfer = []
    list_of_transfered= []

    if st.button('Transfer all'):
        client = SSHClient()
        
        known_hosts_path = os.path.expanduser('~/.ssh/known_hosts')
        client.load_host_keys(known_hosts_path)
        client.load_system_host_keys()
        
        client.set_missing_host_key_policy(AutoAddPolicy())
        
        client.connect(host, username=user_admin, password=password_admin)
        
        sftp_session = client.open_sftp()
        client.set_log_channel('DEBUG')
        
        sftp_session.chdir('..')
        sftp_session.chdir('..')
        sftp_session.chdir('media/psylab-6028/DATA/fMRIprep/fibro/selectedSubs/')
        
        sub_folders = [os.path.join(folder_path, f) for f in list_subjects if f.startswith('sub-')]
        remote_sub_folders = [f for f in list_subjects if f.startswith('sub-')]
        
        for sub_folder, remote_sub_folder in zip(sub_folders, remote_sub_folders):
            upload_directory(sftp_session, sub_folder, remote_sub_folder)
            
        list_of_transfered = [f for f in sftp_session.listdir() if f.startswith('sub-')]
        
        st.session_state.list_of_transfered = list_of_transfered
        
        client.close()
        sftp_session.close()


    if st.session_state.selected_subject != None and st.button('Transfer folder'):
        client = SSHClient() 
        
        known_hosts_path = os.path.expanduser('~/.ssh/known_hosts')
        client.load_host_keys(known_hosts_path)
        client.load_system_host_keys()

        client.set_missing_host_key_policy(AutoAddPolicy())

        client.connect(host, username=user_admin, password=password_admin)



        sftp_session = client.open_sftp()
        client.set_log_channel('DEBUG')
        sftp_session.chdir('..')
        sftp_session.chdir('..')
        sftp_session.chdir('media/psylab-6028/DATA/fMRIprep/fibro/selectedSubs/')
        
        sub_folder = os.path.join(folder_path, selected_subject)
        remote_sub_folder = f'{selected_subject}'
        upload_directory(sftp_session, sub_folder, remote_sub_folder)
        # sftp_session.put(fr'{folder_path}\\{selected_subject}', f'{selected_subject}')
        
        print(f'List of files: {sftp_session.listdir()}')
        
        list_of_transfered = [f for f in sftp_session.listdir() if f.startswith('sub-')]
        
        st.session_state.list_of_transfered = list_of_transfered
        
        client.close()
        sftp_session.close()
        
    st.write('Run fMRIprep on the server')
    
    st.write('Select the tasks to run fMRIprep on the server')

    tasks_list = []

    for sub in os.listdir(r'E:\Fibro\\BIDS_output'):
        if sub.endswith('.xlsx'):
            continue
        for file in os.listdir(os.path.join(r'E:\\Fibro\\BIDS_output', sub, 'func')):
            if file.endswith('.nii.gz'):
                task = file.split('_')[1]
                if 'task-' in task:
                    task = task.split('-')[1]
                    if 'bold' in task.lower():
                        task = task.split('_')[0]
                    if task not in tasks_list:
                        tasks_list.append(task)
    tasks_list.sort()
    st.session_state.tasks_list = tasks_list
    selected_tasks = st.multiselect('Select tasks', tasks_list)
    
    if selected_tasks != None:
        st.session_state.selected_tasks = selected_tasks

    st.write('Selected tasks: ', selected_tasks)

    if 'anat_only' not in st.session_state:
        st.session_state.anat_only = False

    
    st.session_state.anat_only = st.checkbox('Anatomical only', value=st.session_state.anat_only)

    if st.session_state.anat_only:
        st.write('Anatomical only selected')
    else:
        st.write('Anatomical and functional data will be processed')

    if 'list_of_transfered' not in st.session_state:
        st.session_state.list_of_transfered = []

    if 'load_available_subjects' not in st.session_state:
        st.session_state.load_available_subjects = False
        
    if st.button('Load available subjects'):
        client = SSHClient()
        known_hosts_path = os.path.expanduser('~/.ssh/known_hosts')
        client.load_host_keys(known_hosts_path)
        client.load_system_host_keys()
        client.set_missing_host_key_policy(AutoAddPolicy())
        client.connect(host, username=user_admin, password=password_admin)
        sftp_session = client.open_sftp()
        sftp_session.chdir('..')
        sftp_session.chdir('..')
        sftp_session.chdir('media/psylab-6028/DATA/fMRIprep/fibro/selectedSubs/')
        st.session_state.list_of_transfered = [f for f in sftp_session.listdir() if f.startswith('sub-')]
        print(f'List of files: {st.session_state.list_of_transfered}')
        client.close()
        sftp_session.close()
    if st.session_state.load_available_subjects:
        st.write('Available subjects on the server: ', st.session_state.list_of_transfered)

    if 'subjects_to_run' not in st.session_state:
        st.session_state.subjects_to_run = []
    
    st.write('Subjects to run fMRIprep on the server')
    st.session_state.subjects_to_run = st.multiselect('Select subjects', st.session_state.list_of_transfered if st.session_state.list_of_transfered else [])

    if st.button('Run fMRIprep'):
        # client = SSHClient() 
        
        # known_hosts_path = os.path.expanduser('~/.ssh/known_hosts')
        # client.load_host_keys(known_hosts_path)
        # client.load_system_host_keys()

        # client.set_missing_host_key_policy(AutoAddPolicy())

        # client.connect(host, username=user, password=password)
        
        # for selected_subject in st.session_state.selected_subjects_run:
        #     upload_directory(sftp_session, sub_folder, remote_sub_folder)
        #     stdin, stdout, stderr = client.exec_command(f'cd fMRIprep ; mv /home/fibrostudy/fMRIprep/{selected_subject} /home/fibrostudy/fMRIprep/selectedSubs/')
        
        # print(stdout.read().decode())

        # client.close()
        # stdin.close()
        # stdout.close()
        # stderr.close()
        helper = r"C:\Users\PsyLab-6028\Documents\GitHub\fMRIprepStreamlitPub\run_ssh_fmriprep.py"

        subjects = [x.split('-')[1] for x in st.session_state.subjects_to_run] or []
        tasks    = selected_tasks or []
        anat     = st.session_state.anat_only

        parts = [rf'python "{helper}"', host, user_admin, password_admin]

        if subjects:
            parts += ["--subjects"] + subjects
        if tasks:
            parts += ["--tasks"] + tasks
        if anat:
            parts += ["--anat-only"]  # bare flag, no 1/0

        # st.write('Running fMRIprep with the following command: ', " ".join(parts))
        command = " ".join(parts)

        process = subprocess.Popen(
            command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        # helper   = r"C:\Users\PsyLab-6028\Desktop\fMRIprepStreamlit\scripts\run_fMRIprep.py"
        # subject_flags = " ".join(st.session_state.subjects_to_run) if st.session_state.subjects_to_run else ""
        # task_flags    = " ".join(selected_tasks) if selected_tasks else ""
        # anat_only = '1' if st.session_state.anat_only else '0'

        # command = rf'python "{helper}" {host} {user} {password} ' \
        #     rf'--subjects {subject_flags} --tasks {task_flags} --anat-only {anat_only}'

        # command = rf'python "C:\Users\PsyLab-6028\Desktop\fMRIprepStreamlit\scripts\run_fMRIprep.py" {host} {user} {password} {" ".join(selected_tasks)}'
        # # else:
        # #     command = rf'python "C:\Users\PsyLab-6028\Desktop\fMRIprepStreamlit\scripts\run_fMRIprep.py" {host} {user} {password}'
        
        # # subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print(process.stdout.read().decode())
        print(process.stderr.read().decode())
        
        
    st.divider()

    st.write('If you think that the fMRIprep process is finished, you can check the output folder')
    if 'list_files_outputs' not in st.session_state:
        st.session_state.list_files_outputs = []
        
    if 'list_files_outputs_names' not in st.session_state:
        st.session_state.list_files_outputs_names = []
        
    if 'list_files_outputs_old' not in st.session_state:
        st.session_state.list_files_outputs_old = []
        
    if 'list_files_outputs_names_old' not in st.session_state:
        st.session_state.list_files_outputs_names_old = []
        
    # if st.button('Check output folder'):
    #     try:
    #         client = SSHClient()
    #         known_hosts_path = os.path.expanduser('~/.ssh/known_hosts')
    #         client.load_host_keys(known_hosts_path)
    #         client.load_system_host_keys()
    #         client.set_missing_host_key_policy(AutoAddPolicy())
    #         client.connect(host, username=user, password=password)
    #         sftp_session = client.open_sftp()
    #         sftp_session.chdir('fMRIprep/outputs/')
    #         st.session_state.list_files_outputs = [' '.join(str(file).split(' ')[-4:]) for file in sftp_session.listdir_attr()]
    #         st.session_state.list_files_outputs_names = [file for file in sftp_session.listdir()]
    #         print(f'List of files: {st.session_state.list_files_outputs}')
    #         client.close()
    #         sftp_session.close()
    #     except Exception as e:
    #         print(f'Error: {e}')
    if st.button('Check output folder'):
        try:
            # client = SSHClient()
            known_hosts_path = os.path.expanduser('~/.ssh/known_hosts')
            # client.load_host_keys(known_hosts_path)
            # client.load_system_host_keys()
            # client.set_missing_host_key_policy(AutoAddPolicy())
            # client.connect(host, username=user_admin, password=password_admin)
            # sftp_session = client.open_sftp()
            # sftp_session.chdir('fMRIprep/outputs/')
            # attrs_old = sorted(sftp_session.listdir_attr(), key=lambda a: a.st_mtime, reverse=True)
            # print(f'List of files: {sftp_session.listdir()}')
            # st.session_state.list_files_outputs_old = [
            #     f"{attr.filename} | size: {attr.st_size} | modified datetime: {datetime.fromtimestamp(attr.st_mtime).strftime('%Y-%m-%d %H:%M:%S')}"
            #     for attr in attrs_old
            # ]
            # st.session_state.list_files_outputs_names_old = [attr.filename for attr in attrs_old]
            # client.close()
            # sftp_session.close()
            client = SSHClient()
            client.load_host_keys(known_hosts_path)
            client.load_system_host_keys()
            client.set_missing_host_key_policy(AutoAddPolicy())
            client.connect(host, username=user_admin, password=password_admin)
            sftp_session = client.open_sftp()
            sftp_session.chdir('..')  # Navigate to the parent directory
            sftp_session.chdir('..')  # Navigate to the parent directory again
            sftp_session.chdir('media/psylab-6028/DATA/fMRIprep_outputs/')
            # sftp_session.chdir('media/psylab-6028/DATA/fMRIprep_outputs/')
            attrs = sorted(sftp_session.listdir_attr(), key=lambda a: a.st_mtime, reverse=True)
            print(f'List of files: {sftp_session.listdir()}')
            st.session_state.list_files_outputs = [
                f"{attr.filename} | size: {attr.st_size} | modified datetime: {datetime.fromtimestamp(attr.st_mtime).strftime('%Y-%m-%d %H:%M:%S')}"
                for attr in attrs
            ]
            st.session_state.list_files_outputs_names = [attr.filename for attr in attrs]
            print(f'List of files: {st.session_state.list_files_outputs}')
            client.close()
            sftp_session.close()
        except Exception as e:
            print(f'Error: {e}')
            
    st.divider()

    st.write('Select the output folder to use')
    
    

    st.write('To download the output folder, select the desired folder')

    selected_output_folder = (st.selectbox('Select a folder', st.session_state.list_files_outputs))

    if selected_output_folder != None:
        st.session_state.selected_output_folder = selected_output_folder

    if st.session_state.selected_output_folder != None and st.button('Download output folder'):
        client = SSHClient()
        known_hosts_path = os.path.expanduser('~/.ssh/known_hosts')
        client.load_host_keys(known_hosts_path)
        client.load_system_host_keys()
        client.set_missing_host_key_policy(AutoAddPolicy())
        client.connect(host, username=user_admin, password=password_admin)
        sftp_session = client.open_sftp()
        sftp_session.chdir('..')  # Navigate to the parent directory
        sftp_session.chdir('..')  # Navigate to the parent directory again
        sftp_session.chdir('/media/psylab-6028/DATA/fMRIprep_outputs')
        list_files = sftp_session.listdir()
        selected_output_folder = [x.split(' ')[0] for x in st.session_state.list_files_outputs if x.startswith(selected_output_folder)][0]
        if selected_output_folder.startswith('sub-'):
            if not os.path.exists(f'E:/Fibro/fMRIprep_output/{selected_output_folder}'):
                os.makedirs(f'E:/Fibro/fMRIprep_output/{selected_output_folder}')
                os.makedirs(f'E:/Fibro/fMRIprep_output/{selected_output_folder}/figures')
                os.makedirs(f'E:/Fibro/fMRIprep_output/{selected_output_folder}/func')
                os.makedirs(f'E:/Fibro/fMRIprep_output/{selected_output_folder}/log')
                
            download_directory(sftp_session, f'{selected_output_folder}/figures', f'E:/Fibro/fMRIprep_output/{selected_output_folder}/figures')
            download_directory(sftp_session, f'{selected_output_folder}/func', f'E:/Fibro/fMRIprep_output/{selected_output_folder}/func')
            download_directory(sftp_session, f'{selected_output_folder}/log', f'E:/Fibro/fMRIprep_output/{selected_output_folder}/log')
            # sftp_session.get(f'fMRIprep/outputs/{selected_output_folder}/figures', f'E:/Fibro/fMRIprep_output/{selected_output_folder}/figures')
            # sftp_session.get(f'fMRIprep/outputs/{selected_output_folder}/func', f'E:/Fibro/fMRIprep_output/{selected_output_folder}/func')
            download_directory(sftp_session, f'{selected_output_folder}/anat', f'E:/Fibro/fMRIprep_output/{selected_output_folder}/anat')
            download_directory(sftp_session, f'{selected_output_folder}.html', f'E:/Fibro/fMRIprep_output/{selected_output_folder}.html')
            # sftp_session.get(f'{selected_output_folder}.html', f'E:/Fibro/fMRIprep_output/{selected_output_folder}.html')
        elif selected_output_folder.endswith('.json'):
            sftp_session.get(selected_output_folder, f'E:/Fibro/fMRIprep_output/{selected_output_folder}')

        else:
            if not os.path.exists(f'E:/Fibro/fMRIprep_output/{selected_output_folder}'):
                os.makedirs(f'E:/Fibro/fMRIprep_output/{selected_output_folder}')
            download_directory(sftp_session, selected_output_folder, f'E:/Fibro/fMRIprep_output/{selected_output_folder}')

        client.close()
        sftp_session.close()
            


if __name__ == '__main__':
    
    main()




# print(f'Connected to {dir(sftp_session)}')

# stdin, stdout, stderr = client.exec_command('cd fMRIprep ; cat fmri-run.sh')
# print(stdout.read().decode())
# inspect(client, methods=True)
# client.close()
# sftp_session.close()
# stdin.close()
# stdout.close()
# stderr.close()