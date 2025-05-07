import sys
import os
from rich import print
import subprocess
import argparse
from paramiko import SSHClient, AutoAddPolicy
import time as ti


def main(user, host, password):
    client = SSHClient() 
    
    known_hosts_path = os.path.expanduser('~/.ssh/known_hosts')
    client.load_host_keys(known_hosts_path)
    client.load_system_host_keys()

    client.set_missing_host_key_policy(AutoAddPolicy())

    client.connect(host, username=user, password=password)
    
    stdin, stdout, stderr = client.exec_command(f'cd fMRIprep ; ls ; pwd')

    if stdout.channel.recv_exit_status() == 0:
        print('[bold green]Connected to the server![/bold green]')
    else:
        print('[bold red]Failed to connect to the server![/bold red]')
        sys.exit(1)
        
    for line in stdout:
        print(line.strip())
        
        
    command = 'cd fMRIprep; sudo ./fmri-run.sh; echo "fMRIprep ran successfully!"'
    print(f"Executing command: {command}")
    stdin, stdout, stderr = client.exec_command(command, get_pty=True)
    
    for line in stdout:
        print(line.strip())
    
    if stderr:
        print(stderr.read())
        ti.sleep(7)
    
    if stdout.channel.recv_exit_status() == 0:
        print('[bold green]fMRIprep ran successfully![/bold green]')
        client.close()
        stdout.close()
        stderr.close()
        stdin.close()
    else:
        print('[bold red]fMRIprep failed to run![/bold red]')
        client.close()
        stdout.close()
        stderr.close()
        stdin.close()
        
if __name__ == '__main__':
    # parser = argparse.ArgumentParser(description='Run fMRIprep on a remote server.')
    # parser.add_argument('user', type=str, help='Username for the remote server.')
    # parser.add_argument('host', type=str, help='Host address for the remote server.')
    # parser.add_argument('password', type=str, help='Password for the remote server.')
    # args = parser.parse_args()
    
    user = sys.argv[2]
    host = sys.argv[1]
    password = sys.argv[3]
    print(f'User: {user}, Host: {host}, Password: {password}')
    main(user, host, password)
    
    
    
        
    