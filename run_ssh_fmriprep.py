import paramiko
from rich import print


def main(user, host, password):
    # Initialize the SSH client
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Connect to the remote server
        print(f"Connecting to {host} as {user}...")
        client.connect(host, username=user, password=password)

        # Run fMRIprep command
        command = 'cd fMRIprep; sudo ./fmri-run.sh; echo "fMRIprep ran successfully!"'
        print(f"Executing command: {command}")
        stdin, stdout, stderr = client.exec_command(command, get_pty=True)
        
        # Provide password for sudo
        stdin.write(password + "\n")
        stdin.flush()

        # Collect output
        output = stdout.read().decode()
        errors = stderr.read().decode()
        print(f"[green]Output:[/green]\n{output}")
        if errors:
            print(f"[red]Errors:[/red]\n{errors}")

    except paramiko.AuthenticationException as e:
        print(f"[red]Authentication failed: {e}[/red]")
    except Exception as e:
        print(f"[red]An error occurred: {e}[/red]")
    finally:
        client.close()
        print("Connection closed.")


if __name__ == "__main__":
    host = '132.74.68.175'
    user = 'fibrostudy'
    password = '8X-Zpp!!'
    print(f"User: {user}, Host: {host}")
    main(user, host, password)
