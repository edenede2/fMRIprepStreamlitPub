# fMRIprep Streamlit Application

A user-friendly Streamlit application for managing fMRI preprocessing workflows using fMRIprep. This tool streamlines the process of converting neuroimaging data to BIDS format, transferring datasets to a remote server, running fMRIprep, and retrieving results.

## Overview

This application provides a web-based interface to:

1. Convert raw neuroimaging data to BIDS format
2. Transfer BIDS-formatted datasets to a remote processing server
3. Run fMRIprep preprocessing pipelines remotely
4. Monitor processing status
5. Download and manage results

## Features

- **BIDS Conversion**: Automatically convert neuroimaging datasets into BIDS-compliant format
- **Data Transfer**: Securely transfer data between local machine and remote server
- **Remote Processing**: Execute fMRIprep preprocessing on powerful remote servers
- **Results Management**: Download, view, and organize preprocessing results

## Requirements

- Python 3.7+
- Streamlit
- Paramiko (for SSH connections)
- Rich (for improved terminal output)
- Flask (for web components)

## Setup

1. Clone the repository:
```bash
git clone https://github.com/edenede2/fMRIprepStreamlitPub.git
cd fMRIprepStreamlitPub
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with your server credentials:
```
HOST=your_server_hostname
USER=your_username
PASSWORD=your_password
```

## Usage

1. Start the Streamlit app:
```bash
streamlit run streamlit-paramiko.py
```

2. Use the web interface to:
   - Convert data to BIDS format
   - Select and transfer subjects to the processing server
   - Run fMRIprep on the selected data
   - Download and view results

## Scripts

- `streamlit-paramiko.py`: Main Streamlit application
- `run_fMRIprep.py`: Script for executing fMRIprep on the remote server
- `run_ssh_fmriprep.py`: Handles SSH connections for remote execution
- `A stand alone.py`: Converts neuroimaging data to BIDS format

## fMRIprep

This application uses [fMRIprep](https://fmriprep.org/), a robust preprocessing pipeline for functional MRI data. The preprocessing includes:

- Anatomical data preprocessing (brain extraction, tissue segmentation, spatial normalization)
- Functional data preprocessing (motion correction, co-registration, confound estimation)
- Generation of comprehensive visual reports

## Output

The fMRIprep output includes:
- Preprocessed functional and anatomical data
- Confound files for downstream analysis
- Visual HTML reports for quality assessment
- Transformation matrices for spatial normalization

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
