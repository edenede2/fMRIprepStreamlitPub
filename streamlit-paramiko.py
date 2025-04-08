import streamlit as st
from paramiko import SSHClient, AutoAddPolicy
from rich import print, pretty, inspect
import subprocess
pretty.install()
import os
import webview
from flask import Flask

import stat

import subprocess



host = '132.74.68.175'
user = 'fibrostudy'
password = '8X-Zpp!!'


def main():
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
        try:
            sftp.stat(remote_path)
            remove_remote_directory(sftp, remote_path)
        except IOError:  # Directory does not exist
            pass

        # Create the remote directory
        sftp.mkdir(remote_path)

        for item in os.listdir(local_path):
            local_item_path = os.path.join(local_path, item)
            remote_item_path = f"{remote_path}/{item}".replace("\\", "//")  # Ensure proper path format for remote

            if os.path.isdir(local_item_path):
                # Recursively upload subdirectories
                upload_directory(sftp, local_item_path, remote_item_path)
            else:
                # Upload individual file
                sftp.put(local_item_path, remote_item_path)
                print(f"Uploaded: {local_item_path} to {remote_item_path}")
        st.write(f"Uploaded: {local_item_path} to {remote_item_path}")
        



    st.title('Streamlit fMRIprep management')



    st.write('Convert nifti to BIDS format')
    
    if st.button('Convert to BIDS'):
        command = rf'python "C:\Users\PsyLab-6028\Desktop\fMRIprepStreamlit\A stand alone.py" '
        subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        
        print('Conversion to BIDS format finished')

    st.write('This is a simple Streamlit app to manage fMRIprep on the server')

    st.write('Show available files on the fMRIpre folder of the server')

    list_fMRIprep_available_subs = []

    if st.button('Connect to server'):
        client = SSHClient() 
        
        
        

        known_hosts_path = os.path.expanduser('~/.ssh/known_hosts')
        client.load_host_keys(known_hosts_path)
        client.load_system_host_keys()

        client.set_missing_host_key_policy(AutoAddPolicy())

        client.connect(host, username=user, password=password)



        sftp_session = client.open_sftp()
        client.set_log_channel('DEBUG')
        print(f'Current directory: {sftp_session.getcwd()}')
        sftp_session.chdir('fMRIprep/selectedSubs/')
        # print(f'Current directory: {sftp_session.getcwd()}')  
        print(f'List of files: {sftp_session.listdir()}')
        
        list_fMRIprep_available_subs = [f for f in sftp_session.listdir() if f.startswith('sub-')]
        
        client.close()
        sftp_session.close()
        
    st.write('List of files in the fMRIprep folder')
    st.write(list_fMRIprep_available_subs)

    st.divider()

    st.write('Select a folder to transfer from the local machine to the server')

    folder_path = r'E:\\Fibro\\BIDS_output'

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
        
        client.connect(host, username=user, password=password)
        
        sftp_session = client.open_sftp()
        client.set_log_channel('DEBUG')
        
        sftp_session.chdir('fMRIprep/selectedSubs/')
        
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

        client.connect(host, username=user, password=password)



        sftp_session = client.open_sftp()
        client.set_log_channel('DEBUG')
        
        sftp_session.chdir('fMRIprep/selectedSubs/')
        
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
        
        command = rf'python "C:\Users\PsyLab-6028\Desktop\fMRIprepStreamlit\scripts\run_fMRIprep.py" {host} {user} {password}'
        
        # subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print(process.stdout.read().decode())
        print(process.stderr.read().decode())
        
        
    st.divider()

    st.write('If you think that the fMRIprep process is finished, you can check the output folder')
    if 'list_files_outputs' not in st.session_state:
        st.session_state.list_files_outputs = []
        
    if 'list_files_outputs_names' not in st.session_state:
        st.session_state.list_files_outputs_names = []
        
    if st.button('Check output folder'):
        try:
            client = SSHClient()
            known_hosts_path = os.path.expanduser('~/.ssh/known_hosts')
            client.load_host_keys(known_hosts_path)
            client.load_system_host_keys()
            client.set_missing_host_key_policy(AutoAddPolicy())
            client.connect(host, username=user, password=password)
            sftp_session = client.open_sftp()
            sftp_session.chdir('fMRIprep/outputs/')
            st.session_state.list_files_outputs = [' '.join(str(file).split(' ')[-4:]) for file in sftp_session.listdir_attr()]
            st.session_state.list_files_outputs_names = [file for file in sftp_session.listdir()]
            print(f'List of files: {st.session_state.list_files_outputs}')
            client.close()
            sftp_session.close()
        except Exception as e:
            print(f'Error: {e}')
            
            
    st.divider()

    st.write('To download the output folder, select the desired folder')

    selected_output_folder = (st.selectbox('Select a folder', st.session_state.list_files_outputs)).split(' ')[-1]

    if selected_output_folder != None:
        st.session_state.selected_output_folder = selected_output_folder

    if st.session_state.selected_output_folder != None and st.button('Download output folder'):
        client = SSHClient()
        known_hosts_path = os.path.expanduser('~/.ssh/known_hosts')
        client.load_host_keys(known_hosts_path)
        client.load_system_host_keys()
        client.set_missing_host_key_policy(AutoAddPolicy())
        client.connect(host, username=user, password=password)
        sftp_session = client.open_sftp()
        sftp_session.chdir('fMRIprep/outputs/')
        list_files = sftp_session.listdir()
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
            sftp_session.get(f'{selected_output_folder}.html', f'E:/Fibro/fMRIprep_output/{selected_output_folder}.html')
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