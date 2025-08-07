import subprocess

command = ['streamlit', 'run', r'C:\Users\PsyLab-6028\Documents\GitHub\fMRIprepStreamlitPub\streamlit-paramiko.py']
process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

for line in process.stdout:
    print(line, end='')  # Print Streamlit output to the console

process.wait()