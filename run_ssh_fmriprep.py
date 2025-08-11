import paramiko
from rich import print
import os
from pathlib import Path
import sys



def parse_cli():
    # very small parser – no external deps
    args = sys.argv[1:]
    host, user, pw = args[:3]
    remain        = args[3:]

    # grab flag blocks
    subj_idx = remain.index("--subjects") if "--subjects" in remain else None
    task_idx = remain.index("--tasks")    if "--tasks"    in remain else None
    anat_only = "--anat-only" in remain

    if anat_only == 0:
        anat_only = True
    else:
        anat_only = False

    subjects = remain[subj_idx+1 : task_idx or len(remain)] if subj_idx is not None else []
    tasks    = remain[task_idx+1 :]                           if task_idx is not None else []

    return host, user, pw, subjects, tasks, anat_only


def main(user, host, password, subjects=None, tasks=None, anat_only=False):
    # Initialize the SSH client
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"[cyan]Connecting to {host} as {user}...[/cyan]")


    try:
        # Connect to the remote server
        print(f"Connecting to {host} as {user}...")
        client.connect(host, username=user, password=password)

        remote_dir = "fMRIprep"
        tasks_flag = " ".join(f"-t {t}" for t in tasks)

        if not subjects:
            cmd = (
                f"cd {remote_dir} && "
                f"sudo fmriprep-docker /home/fibrostudy/fMRIprep/selectedSubs /media/psylab-6028/DATA/fMRIprep_outputs participant {tasks_flag} {'--anat-only' if anat_only else ''} --fs-license-file /home/fibrostudy/fMRIprep/license.txt -w /media/Data/work/ --low-mem --nthreads 8 --ignore slicetiming --skip_bids_validation &&"
                f"echo '[fMRIprep finished OK]'"
            )

            print(f"[cyan]Executing command: {cmd}[/cyan]")
            stdin, stdout, stderr = client.exec_command(cmd, get_pty=True)

            # Provide password for sudo
            stdin.write(password + "\n")
            stdin.flush()

            # Collect output
            print("[green]Output:[/green]")
            print(stdout.read().decode())
            
            # Check for errors
            if (err := stderr.read().decode()):
                print(f"[red]Errors:[/red]\n{err}")
            
            # cmd = (
            #     f"cd {remote_dir} && "
            #     f"sudo ./fmri-run.sh {tasks_flag} {'--anat-only' if anat_only else ''} && "
            #     f"echo '[fMRIprep finished OK]'"
            # )

            # print(f"[cyan]Executing command: {cmd}[/cyan]")
            # stdin, stdout, stderr = client.exec_command(cmd, get_pty=True)

            # print(stdout.read().decode())
            # if (err := stderr.read().decode()):
            #     print(f"[red]Errors:[/red]\n{err}")
            
            # # Run fMRIprep command
            # command = f'cd fMRIprep; sudo ./fmri-run.sh {"--anat-only" if anat_only else ""}; echo "fMRIprep ran successfully!"'
            # print(f"Executing command: {command}")
            # stdin, stdout, stderr = client.exec_command(command, get_pty=True)
        
            # # Provide password for sudo
            # stdin.write(password + "\n")
            # stdin.flush()

            # # Collect output
            # output = stdout.read().decode()
            # errors = stderr.read().decode()
            # print(f"[green]Output:[/green]\n{output}")
            # if errors:
            #     print(f"[red]Errors:[/red]\n{errors}")
        else:
            remote_file = f"{remote_dir}/subjects.txt"

            print("[cyan]Uploading subjects.txt...[/cyan]")
            with client.open_sftp() as sftp:
                with sftp.file(remote_file, 'w') as f:
                    f.write('\n'.join(subjects) + '\n')
            
            cmd_prep_ids = (
                f"IDS=$(tr '\n' ' ' < {remote_file}) && "
                f"cd {remote_dir} && "
                f"sudo fmriprep-docker /home/fibrostudy/fMRIprep/selectedSubs /media/psylab-6028/DATA/fMRIprep_outputs participant $IDS {tasks_flag} "
                f"{'--anat-only' if anat_only else ''} --fs-license-file /home/fibrostudy/fMRIprep/license.txt -w /media/Data/work/ --low-mem --nthreads 8 --ignore slicetiming --skip_bids_validation && "
                f"echo '[fMRIprep finished OK]'"
            )

            # cmd_prep_ids = (
            #     f"IDS=$(tr '\n' ' ' < {remote_file}) && "
            #     f"cd {remote_dir} && "
            #     f"sudo ./fmri-run.sh --participant-label $IDS {tasks_flag} "
            #     f"{'--anat-only' if anat_only else ''} && "
            #     f"echo '[fMRIprep finished OK]'"
            # )

            print(f"[cyan]Executing command: \n{cmd_prep_ids}[/cyan]")
            stdin, stdout, stderr = client.exec_command(cmd_prep_ids, get_pty=True)

            # Provide password for sudo
            stdin.write(password + "\n")
            stdin.flush()

            print("[green]Output:[/green]")
            print(stdout.read().decode())
            err = stderr.read().decode()
            if err:
                print(f"[red]Errors:[/red]\n{err}")

    except paramiko.AuthenticationException as e:
        print(f"[red]Authentication failed: {e}[/red]")
    except Exception as e:
        print(f"[red]An error occurred: {e}[/red]")
    finally:
        client.close()
        print("Connection closed.")


if __name__ == "__main__":
        # host = os.getenv('HOST')
        # user = os.getenv('USER')
        # password = os.getenv('PASSWORD')
        # subjects = sys.argv[1:] if len(sys.argv) > 1 else None
        # anat_only = '--anat-only' in sys.argv
    h,u,p,subs,tasks,anat_only = parse_cli()

    print(f"User: {u}, Host: {h}")
    main(u, h, p, subs, tasks, anat_only)
