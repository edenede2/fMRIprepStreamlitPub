
import os
import csv
import json
import shutil
import re
import tkinter as tk
from tkinter import filedialog
import pandas as pd
import numpy as np


def get_folder_path():
    root = tk.Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory()
    return folder_path

def main():
    
    # create a dataframe to save the data about the participents and in the end save it as a excel file
    df = pd.DataFrame(columns=['Id', 'type', 'T1w nifti', 'T1w json', 'T1wa nifti', 'T1wa json', 
                                 'T2w nifti', 'T2w json', 'T2wa nifti', 'T2wa json', 
                                 'Rest nifti', 'Rest json', 'Rest SBRef nifti',
                                 'Rest SBRef json', 'Flares nifti', 'Flares json', 
                                 'Flares SBRef nifti', 'Flares SBRef json',
                                 'Reward nifti', 'Reward json', 'Reward SBRef nifti',
                                 'Reward SBRef json', 'Callibration nifti', 'Callibration json',
                                 'Callibration SBRef nifti', 'Callibration SBRef json',
                                 'Callibration_a nifti', 'Callibration_a json',
                                 'Callibration_a SBRef nifti', 'Callibration_a SBRef json',
                                 'Localizer nifti', 'Localizer json', 'Localizer SBRef nifti',
                                 'Localizer SBRef json', 'Localizer_a nifti', 'Localizer_a json',
                                 'Localizer_a SBRef nifti', 'Localizer_a SBRef json',
                                 'magnitude1 nifti', 'magnitude1 json', 'magnitude2 nifti',
                                 'magnitude2 json', 'phasediff1 nifti', 'phasediff1 json',
                                 'phasediff2 nifti', 'phasediff2 json', 'phasediff1_a nifti',
                                 'phasediff1_a json', 'phasediff2_a nifti', 'phasediff2_a json',
                                 'magnitude1_a nifti', 'magnitude1_a json', 'magnitude2_a nifti',
                                 'magnitude2_a json'])
    
    df_folders = pd.DataFrame(columns=['Id', 'anat', 'func', 'fmap', 'misc'])

    
    Subjects = 0
    HC = 0
    FM = 0
    T1w = 0
    T1wa = 0
    T2w = 0
    T2wa = 0
    Rest = 0
    Flares = 0
    Reward = 0
    Callibration = 0
    Localizer = 0
    magnitude1 = 0
    magnitude2 = 0
    phasediff1 = 0
    phasediff2 = 0
    magnitude1_a = 0
    magnitude2_a = 0
    phasediff1_a = 0
    phasediff2_a = 0
    
    df_summary = pd.DataFrame({'Subjects': [Subjects], 'HC': [HC], 
                               'FM': [FM], 'T1w': [T1w], 'T1wa': [T1wa], 
                               'T2w': [T2w], 'T2wa': [T2wa], 'Rest': [Rest], 
                               'Flares': [Flares], 'Reward': [Reward], 
                               'Callibration': [Callibration], 'Localizer': [Localizer], 
                               'magnitude1': [magnitude1], 'magnitude2': [magnitude2], 
                               'phasediff1': [phasediff1], 'phasediff2': [phasediff2], 
                               'magnitude1_a': [magnitude1_a], 'magnitude2_a': [magnitude2_a], 
                               'phasediff1_a': [phasediff1_a], 'phasediff2_a': [phasediff2_a]})
    raw_data = pd.read_excel('E:\Fibro\Raw_Data_04_11_24.xlsx')
    
    # Get the path of the folder that include the subjects folders.
    folder_path = r'E:\Fibro'
    
    subjects_folders_dict = {}
    
    for dir in os.listdir(folder_path):
        if re.search(r'.sub_\d{3}', dir):
            subjects_folders_dict[f"{dir.split('.')[2]}"] = dir
        else:
            continue
    
    # subjects_files_dict = {}
    output_folder = os.path.join(folder_path, 'BIDS_output')

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    for sub, dir in subjects_folders_dict.items():


        if re.search(r'sub-\d{3}', sub):
            old_sub = sub.replace('sub-', 'sub_')
            type = raw_data.loc[raw_data['Subject'] == old_sub, 'type'].values[0]
        else:
            type = raw_data.loc[raw_data['Subject'] == sub, 'type'].values[0]
        
        if type == 'HC':
            new_sub = sub.replace('sub_', 'sub-')
            df.loc[new_sub, 'type'] = 'HC'
            HC += 1
        
                
        elif type == 'FM':
            new_sub = sub.replace('sub_', 'sub-')
            df.loc[new_sub, 'type'] = 'FM'
            FM += 1
                    
        Subjects += 1
        subjects_folders_dict[sub] = {'files':{'nii.gz': [], 'json': []}, 'dir': dir}
        for file in os.listdir(os.path.join(folder_path, dir)):
            if re.search(r'.nii.gz', file):
                subjects_folders_dict[sub]['files']['nii.gz'].append(file)
                print(f"File {file} is a nifti file")
            elif re.search(r'.json', file):
                subjects_folders_dict[sub]['files']['json'].append(file)
                print(f"File {file} is a json file")
            else:
                print(f"File {file} is not a nifti or json file")
                


        if re.search(r'sub_\d{3}', sub):
            sub_name = sub.replace('sub_', 'sub-')
        
        sub_output_folder = os.path.join(output_folder, sub_name)
        
        if not os.path.exists(sub_output_folder):
            os.makedirs(sub_output_folder)
            
        anat_folder = os.path.join(sub_output_folder, 'anat')
        func_folder = os.path.join(sub_output_folder, 'func')
        fmap_folder = os.path.join(sub_output_folder, 'fmap')
        misc_folder = os.path.join(sub_output_folder, 'misc')
        
        if not os.path.exists(anat_folder):
            os.makedirs(anat_folder)
        if not os.path.exists(func_folder):
            os.makedirs(func_folder)
        if not os.path.exists(fmap_folder):
            os.makedirs(fmap_folder)
        if not os.path.exists(misc_folder):
            os.makedirs(misc_folder)
            
        for format, names in subjects_folders_dict[sub]['files'].items():
            for name in names:
                if format == 'nii.gz':
                    ext = '.nii.gz'
                elif format == 'json':
                    ext = '.json'
                else:
                    ext = None
                    print(f"File {name} is not a nifti or json file so the extension is not found")
                
                if sub == 'sub_931':
                    print(f"File {name} is in sub_931")
                elif sub == 'sub-931':
                    print(f"File {name} is in sub_931")
                if re.search(r'T1w', name):
                    scan = 'T1w'
                    if re.search(r'MPR', name):
                        scan_ext = 'MPR'
                    else:
                        scan_ext = None
                elif re.search(r't2', name):
                    if re.search(r'midlinea', name):
                        scan = 'T2wa'
                        scan_ext = None
                    elif re.search(r'midline', name):
                        scan = 'T2w'
                        scan_ext = None
                    else:
                        scan = 'T2w'
                        scan_ext = None

                elif re.search(r'localizer', name):
                    scan = 'BOLD'
                    scan_ext = 'Localizer'
                    if re.search(r'SBRef', name):
                        sbref = 'SBRef'
                    else:
                        sbref = None
                
                elif re.search(f'BOLD{ext}', name) or re.search(f'BOLD_SBRef{ext}', name):
                    scan = 'BOLD'
                    if re.search(r'Task', name) or re.search(r'rsfMRI', name) or re.search(r'flares', name) or re.search(r'Flares', name) or re.search(r'Reward', name) or re.search(r'Card', name) or re.search(r'task', name) :
                        scan_ext = 'Task'
                        if re.search(r'rsfMRI', name):
                            task = 'Rest'
                            if re.search(r'SBRef', name):
                                sbref = 'SBRef'
                            else:
                                sbref = None
                        elif re.search(r'rest', name):
                            task = 'Rest'
                            if re.search(r'SBRef', name):
                                sbref = 'SBRef'
                            else:
                                sbref = None
                        
                        elif re.search(r'flares', name):
                            task = 'Flares'
                            if re.search(r'SBRef', name):
                                sbref = 'SBRef'
                            else:
                                sbref = None
                        elif re.search(r'Flares', name):
                            task = 'Flares'
                            if re.search(r'SBRef', name):
                                sbref = 'SBRef'
                            else:
                                sbref = None
                        elif re.search(r'Reward', name) or re.search(r'Card', name):
                            task = 'Reward'
                            if re.search(r'SBRef', name):
                                sbref = 'SBRef'
                            else:
                                sbref = None
                        elif re.search(r'reward', name):
                            task = 'Reward'
                            if re.search(r'SBRef', name):
                                sbref = 'SBRef'
                            else:
                                sbref = None
                        else:
                            task = None
                            scan_ext = None
                            sbref = None
                            print(f"File {name} task's is not found")
                    elif re.search(r'Callibration', name):
                        scan_ext = 'Callibration'
                        if re.search(f'SBRef{ext}', name):
                            sbref = 'SBRef'
                        elif re.search(f'SBRefa{ext}', name):
                            sbref = 'SBRef'
                            scan_ext = 'Callibration_a'
                        else:
                            sbref = None
                    elif re.search(r'localizer', name):
                        scan_ext = 'Localizer'
                        if re.search(r'SBRef', name):
                            sbref = 'SBRef'
                        else:
                            sbref = None
                    else:
                        scan_ext = None
                        print(f"File {name} is BOLD but the scan type is not found")
                elif re.search(r'BOLD_SBRefa', name):
                    scan = 'BOLD'
                    if re.search(r'Task', name) or re.search(r'rsfMRI', name) or re.search(r'flares', name) or re.search(r'Flares', name) or re.search(r'Reward', name) or re.search(r'Card', name) or re.search(r'task', name) :
                        scan_ext = 'Task'
                        if re.search(r'rsfMRI', name):
                            task = 'Rest_a'
                            if re.search(r'SBRef', name):
                                sbref = 'SBRef'
                            else:
                                sbref = None
                        elif re.search(r'flares', name):
                            task = 'Flares_a'
                            if re.search(r'SBRef', name):
                                sbref = 'SBRef'
                            else:
                                sbref = None
                        elif re.search(r'Reward', name) or re.search(r'Card', name):
                            task = 'Reward_a'
                            if re.search(r'SBRef', name):
                                sbref = 'SBRef'
                            else:
                                sbref = None
                        else:
                            task = None
                            scan_ext = None
                            sbref = None
                            print(f"File {name} task's is not found")
                    elif re.search(r'Callibration', name):
                        scan_ext = 'Callibration_a'
                        if re.search(f'SBRef{ext}', name):
                            sbref = 'SBRef'
                        elif re.search(f'SBRefa{ext}', name):
                            sbref = 'SBRef'
                            scan_ext = 'Callibration_a'
                        else:
                            sbref = None
                    elif re.search(r'localizer', name):
                        scan_ext = 'Localizer_a'
                        if re.search(r'SBRef', name):
                            sbref = 'SBRef'
                        else:
                            sbref = None
                elif re.search(r'BOLDa', name):
                    scan = 'BOLD'
                    if re.search(r'Task', name) or re.search(r'rsfMRI', name):
                        scan_ext = 'Task'
                        if re.search(r'rsfMRI', name):
                            task = 'Rest_a'
                            if re.search(r'SBRef', name):
                                sbref = 'SBRef'
                            else:
                                sbref = None
                        elif re.search(r'Flares', name):
                            task = 'Flares_a'
                            if re.search(r'SBRef', name):
                                sbref = 'SBRef'
                            else:
                                sbref = None
                        elif re.search(r'Reward', name) or re.search(r'Card', name):
                            task = 'Reward_a'
                            if re.search(r'SBRef', name):
                                sbref = 'SBRef'
                            else:
                                sbref = None
                        else:
                            task = None
                            scan_ext = None
                            sbref = None
                            print(f"File {name} task's is not found")
                    elif re.search(r'Callibration', name):
                        scan_ext = 'Callibration_a'
                        if re.search(f'SBRef{ext}', name):
                            sbref = 'SBRef'
                        elif re.search(f'SBRefa{ext}', name):
                            sbref = 'SBRef'
                            scan_ext = 'Callibration_a'
                        else:
                            sbref = None
                    elif re.search(r'localizer', name):
                        scan_ext = 'Localizer_a'
                        if re.search(r'SBRef', name):
                            sbref = 'SBRef'
                        else:
                            sbref = None
                    else:
                        scan_ext = None
                        print(f"File {name} is BOLD but the scan type is not found")
                        
                elif re.search(r'FieldMapping', name) or re.search(r'fieldmap', name):
                    scan = 'fMAP'
                    if re.search(f'e1{ext}', name):
                        scan_ext = 'magnitude1'
                    elif re.search(f'e1a{ext}', name):
                        scan_ext = 'magnitude1_a'
                    elif re.search(f'e2{ext}', name):
                        scan_ext = 'magnitude2'
                    elif re.search(f'e2a{ext}', name):
                        scan_ext = 'magnitude2_a'
                    elif re.search(f'2_ph{ext}', name):
                        scan_ext = 'phasediff2'
                    elif re.search(f'2_pha{ext}', name):
                        scan_ext = 'phasediff2_a'
                    elif re.search(f'1_ph{ext}', name):
                        scan_ext = 'phasediff1'
                    elif re.search(f'1_pha{ext}', name):
                        scan_ext = 'phasediff1_a'
                    else:
                        scan_ext = None
                        print(f"File {name} is fMAP but the scan type is not found")
                else:
                    scan = None
                    print(f"File {name} is not an T1w, BOLD or fMAP file")

                    
                if scan == 'T1w':
                    if scan_ext == 'MPR':
                        BIDS_folder = 'misc'
                    else:
                        BIDS_folder = 'anat'
                    
                elif scan == 'BOLD':
                    if scan_ext == 'Task':
                        if sbref == 'SBRef':
                            BIDS_folder = 'misc'
                        else:
                            BIDS_folder = 'func'
                        
                    elif scan_ext == 'Callibration':
                        BIDS_folder = 'misc'
                    elif scan_ext == 'Localizer':
                        BIDS_folder = 'misc'
                    elif scan_ext == 'Callibration_a':
                        BIDS_folder = 'misc'
                    elif scan_ext == 'Localizer_a':
                        BIDS_folder = 'misc'
                    else:
                        print(f"File {name} is BOLD but the complimantary folder is not found")
                elif scan == 'fMAP':
                    BIDS_folder = 'fmap'
                elif scan == 'T2w':
                    BIDS_folder = 'misc'
                elif scan == 'T2wa':
                    BIDS_folder = 'misc'
                    
                else:
                    BIDS_folder = 'misc'
                    print(f"File {name} is not T1w, Task, Calibration, Localizer, T2w, or fMAP so it will be saved in the misc folder")
                
                final_output_path = os.path.join(sub_output_folder, BIDS_folder)
                
                
                if re.search(r'sub_\d{3}', sub):
                    sub = sub.replace('sub_', 'sub-')
                
                df.loc[sub, 'Id'] = sub
                

                
                if scan == 'T1w':
                    T1w += 1
                    if scan_ext == 'MPR':
                        new_name = f"{sub}-MPR_T1w{ext}"
                        shutil.copy(os.path.join(folder_path, dir, name), final_output_path)
                        os.rename(os.path.join(final_output_path, name), os.path.join(final_output_path, new_name))
                        
                        if ext == '.json':
                            if pd.isna(df.loc[sub, 'T1w json']):
                                df.loc[sub, 'T1w json'] = 1
                            else:
                                df.loc[sub, 'T1w json'] += 1
                        elif ext == '.nii.gz':
                            if pd.isna(df.loc[sub, 'T1w nifti']):
                                df.loc[sub, 'T1w nifti'] = 1
                            else:
                                df.loc[sub, 'T1w nifti'] += 1
                    else:
                        new_name = f"{sub}_T1w{ext}"
                        shutil.copy(os.path.join(folder_path, dir, name), final_output_path)
                        os.rename(os.path.join(final_output_path, name), os.path.join(final_output_path, new_name))
                        if ext == '.json':
                            if pd.isna(df.loc[sub, 'T1w json']):
                                df.loc[sub, 'T1w json'] = 1
                            else:
                                df.loc[sub, 'T1w json'] += 1
                        elif ext == '.nii.gz':
                            if pd.isna(df.loc[sub, 'T1w nifti']):
                                df.loc[sub, 'T1w nifti'] = 1
                            else:
                                df.loc[sub, 'T1w nifti'] += 1
                                
                elif scan == 'T2w':
                    T2w += 1
                    new_name = f"{sub}_T2w{ext}"
                    shutil.copy(os.path.join(folder_path, dir, name), final_output_path)
                    os.rename(os.path.join(final_output_path, name), os.path.join(final_output_path, new_name))
                    if ext == '.json':
                        if pd.isna(df.loc[sub, 'T2w json']):
                            df.loc[sub, 'T2w json'] = 1
                        else:
                            df.loc[sub, 'T2w json'] += 1
                    elif ext == '.nii.gz':
                        if pd.isna(df.loc[sub, 'T2w nifti']):
                            df.loc[sub, 'T2w nifti'] = 1
                        else:
                            df.loc[sub, 'T2w nifti'] += 1
                elif scan == 'T2wa':
                    T2wa += 1
                    new_name = f"{sub}_T2wa{ext}"
                    shutil.copy(os.path.join(folder_path, dir, name), final_output_path)
                    os.rename(os.path.join(final_output_path, name), os.path.join(final_output_path, new_name))
                    if ext == '.json':
                        if pd.isna(df.loc[sub, 'T2wa json']):
                            df.loc[sub, 'T2wa json'] = 1
                        else:
                            df.loc[sub, 'T2wa json'] += 1
                    elif ext == '.nii.gz':
                        if pd.isna(df.loc[sub, 'T2wa nifti']):
                            df.loc[sub, 'T2wa nifti'] = 1
                        else:
                            df.loc[sub, 'T2wa nifti'] += 1
                elif scan == 'BOLD':
                    if scan_ext == 'Task':
                        if task == 'Rest':
                            Rest += 1
                        elif task == 'Flares':
                            Flares += 1
                        elif task == 'Reward':
                            Reward += 1
                        
                        if sbref == 'SBRef':
                            new_name = f"{sub}_task-{task}_sbref{ext}"
                            shutil.copy(os.path.join(folder_path, dir, name), final_output_path)
                            os.rename(os.path.join(final_output_path, name), os.path.join(final_output_path, new_name))
                            if ext == '.json':
                                if pd.isna(df.loc[sub, f'{task} SBRef json']):
                                    df.loc[sub, f'{task} SBRef json'] = 1
                                else:
                                    df.loc[sub, f'{task} SBRef json'] += 1
                            elif ext == '.nii.gz':
                                if pd.isna(df.loc[sub, f'{task} SBRef nifti']):
                                    df.loc[sub, f'{task} SBRef nifti'] = 1
                                else:
                                    df.loc[sub, f'{task} SBRef nifti'] += 1
                        else:
                            
                            new_name = f"{sub}_task-{task}_bold{ext}"
                            shutil.copy(os.path.join(folder_path, dir, name), final_output_path)
                            os.rename(os.path.join(final_output_path, name), os.path.join(final_output_path, new_name))
                            if ext == '.json':
                                if pd.isna(df.loc[sub, f'{task} json']):
                                    df.loc[sub, f'{task} json'] = 1
                                else:
                                    df.loc[sub, f'{task} json'] += 1
                            elif ext == '.nii.gz':
                                if pd.isna(df.loc[sub, f'{task} nifti']):
                                    df.loc[sub, f'{task} nifti'] = 1
                                else:
                                    df.loc[sub, f'{task} nifti'] += 1
                    elif scan_ext == 'Callibration':
                        Callibration += 1
                        if sbref == 'SBRef':
                            new_name = f"{sub}_callibration_sbref{ext}"
                            shutil.copy(os.path.join(folder_path, dir, name), final_output_path)
                            os.rename(os.path.join(final_output_path, name), os.path.join(final_output_path, new_name))
                            if ext == '.json':
                                if pd.isna(df.loc[sub, 'Callibration SBRef json']):
                                    df.loc[sub, 'Callibration SBRef json'] = 1
                                else:
                                    df.loc[sub, 'Callibration SBRef json'] += 1
                            elif ext == '.nii.gz':
                                if pd.isna(df.loc[sub, 'Callibration SBRef nifti']):
                                    df.loc[sub, 'Callibration SBRef nifti'] = 1
                                else:
                                    df.loc[sub, 'Callibration SBRef nifti'] += 1
                        else:
                            new_name = f"{sub}_callibration{ext}"
                            shutil.copy(os.path.join(folder_path, dir, name), final_output_path)
                            os.rename(os.path.join(final_output_path, name), os.path.join(final_output_path, new_name))
                            if ext == '.json':
                                if pd.isna(df.loc[sub, 'Callibration json']):
                                    df.loc[sub, 'Callibration json'] = 1
                                else:
                                    df.loc[sub, 'Callibration json'] += 1
                            elif ext == '.nii.gz':
                                if pd.isna(df.loc[sub, 'Callibration nifti']):
                                    df.loc[sub, 'Callibration nifti'] = 1
                                else:
                                    df.loc[sub, 'Callibration nifti'] += 1
                    elif scan_ext == 'Callibration_a':
                        Callibration += 1
                        if sbref == 'SBRef':
                            new_name = f"{sub}_callibration_a_sbref{ext}"
                            shutil.copy(os.path.join(folder_path, dir, name), final_output_path)
                            os.rename(os.path.join(final_output_path, name), os.path.join(final_output_path, new_name))
                            if ext == '.json':
                                if pd.isna(df.loc[sub, 'Callibration_a SBRef json']):
                                    df.loc[sub, 'Callibration_a SBRef json'] = 1
                                else:
                                    df.loc[sub, 'Callibration_a SBRef json'] += 1
                            elif ext == '.nii.gz':
                                if pd.isna(df.loc[sub, 'Callibration_a SBRef nifti']):
                                    df.loc[sub, 'Callibration_a SBRef nifti'] = 1
                                else:
                                    df.loc[sub, 'Callibration_a SBRef nifti'] += 1
                        else:
                            new_name = f"{sub}_callibration_a{ext}"
                            shutil.copy(os.path.join(folder_path, dir, name), final_output_path)
                            os.rename(os.path.join(final_output_path, name), os.path.join(final_output_path, new_name))
                            if ext == '.json':
                                if pd.isna(df.loc[sub, 'Callibration_a json']):
                                    df.loc[sub, 'Callibration_a json'] = 1
                                else:
                                    df.loc[sub, 'Callibration_a json'] += 1
                            elif ext == '.nii.gz':
                                if pd.isna(df.loc[sub, 'Callibration_a nifti']):
                                    df.loc[sub, 'Callibration_a nifti'] = 1
                                else:
                                    df.loc[sub, 'Callibration_a nifti'] += 1
                    elif scan_ext == 'Localizer':
                        Localizer += 1
                        if sbref == 'SBRef':
                            new_name = f"{sub}_localizer_sbref{ext}"
                            shutil.copy(os.path.join(folder_path, dir, name), final_output_path)
                            os.rename(os.path.join(final_output_path, name), os.path.join(final_output_path, new_name))
                            if ext == '.json':
                                if pd.isna(df.loc[sub, 'Localizer SBRef json']):
                                    df.loc[sub, 'Localizer SBRef json'] = 1
                                else:
                                    df.loc[sub, 'Localizer SBRef json'] += 1
                            elif ext == '.nii.gz':
                                if pd.isna(df.loc[sub, 'Localizer SBRef nifti']):
                                    df.loc[sub, 'Localizer SBRef nifti'] = 1
                                else:
                                    df.loc[sub, 'Localizer SBRef nifti'] += 1
                                    
                        else:
                            new_name = f"{sub}_localizer{ext}"
                            shutil.copy(os.path.join(folder_path, dir, name), final_output_path)
                            os.rename(os.path.join(final_output_path, name), os.path.join(final_output_path, new_name))
                            if ext == '.json':
                                if pd.isna(df.loc[sub, 'Localizer json']):
                                    df.loc[sub, 'Localizer json'] = 1
                                else:
                                    df.loc[sub, 'Localizer json'] += 1
                            elif ext == '.nii.gz':
                                if pd.isna(df.loc[sub, 'Localizer nifti']):
                                    df.loc[sub, 'Localizer nifti'] = 1
                                else:
                                    df.loc[sub, 'Localizer nifti'] += 1
                                    
                    elif scan_ext == 'Localizer_a':
                        Localizer += 1
                        if sbref == 'SBRef':
                            new_name = f"{sub}_localizer_a_sbref{ext}"
                            shutil.copy(os.path.join(folder_path, dir, name), final_output_path)
                            os.rename(os.path.join(final_output_path, name), os.path.join(final_output_path, new_name))
                            if ext == '.json':
                                if pd.isna(df.loc[sub, 'Localizer_a SBRef json']):
                                    df.loc[sub, 'Localizer_a SBRef json'] = 1
                                else:
                                    df.loc[sub, 'Localizer_a SBRef json'] += 1
                            elif ext == '.nii.gz':
                                if pd.isna(df.loc[sub, 'Localizer_a SBRef nifti']):
                                    df.loc[sub, 'Localizer_a SBRef nifti'] = 1
                                else:
                                    df.loc[sub, 'Localizer_a SBRef nifti'] += 1
                        else:
                            new_name = f"{sub}_localizer_a{ext}"
                            shutil.copy(os.path.join(folder_path, dir, name), final_output_path)
                            os.rename(os.path.join(final_output_path, name), os.path.join(final_output_path, new_name))
                            if ext == '.json':
                                if pd.isna(df.loc[sub, 'Localizer_a json']):
                                    df.loc[sub, 'Localizer_a json'] = 1
                                else:
                                    df.loc[sub, 'Localizer_a json'] += 1
                            elif ext == '.nii.gz':
                                if pd.isna(df.loc[sub, 'Localizer_a nifti']):
                                    df.loc[sub, 'Localizer_a nifti'] = 1
                                else:
                                    df.loc[sub, 'Localizer_a nifti'] += 1
                    else:
                        print(f"File {name} is BOLD but the scan type is not found")
                elif scan == 'fMAP':
                    if scan_ext == 'magnitude1':
                        magnitude1 += 1
                    elif scan_ext == 'magnitude2':
                        magnitude2 += 1
                    elif scan_ext == 'phasediff1':
                        phasediff1 += 1
                    elif scan_ext == 'phasediff2':
                        phasediff2 += 1
                    elif scan_ext == 'magnitude1_a':
                        magnitude1_a += 1
                    elif scan_ext == 'magnitude2_a':
                        magnitude2_a += 1
                    elif scan_ext == 'phasediff1_a':
                        phasediff1_a += 1
                    elif scan_ext == 'phasediff2_a':
                        phasediff2_a += 1
                        
                    new_name = f"{sub}_{scan_ext}{ext}"
                    shutil.copy(os.path.join(folder_path, dir, name), final_output_path)
                    os.rename(os.path.join(final_output_path, name), os.path.join(final_output_path, new_name))
                    if ext == '.json':
                        if pd.isna(df.loc[sub, f'{scan_ext} json']):
                            df.loc[sub, f'{scan_ext} json'] = 1
                        else:
                            df.loc[sub, f'{scan_ext} json'] += 1
                    elif ext == '.nii.gz':
                        if pd.isna(df.loc[sub, f'{scan_ext} nifti']):
                            df.loc[sub, f'{scan_ext} nifti'] = 1
                        else:
                            df.loc[sub, f'{scan_ext} nifti'] += 1
                else:
                    new_name = f"{sub}_misc-{name}{ext}"
                    print(f"File {name} is not T1w, Task, Calibration, Localizer, T2w, or fMAP so it will be saved in the misc folder")
                    shutil.copy(os.path.join(folder_path, dir, name), final_output_path)
                    os.rename(os.path.join(final_output_path, name), os.path.join(final_output_path, new_name))
    for i in os.listdir(output_folder):
        if re.search(r'sub-', i):
            df_folders.loc[i, 'Id'] = i
            for j in os.listdir(os.path.join(output_folder, i)):
                if re.search(r'anat', j):
                    for k in os.listdir(os.path.join(output_folder, i, j)):
                        if pd.isna(df_folders.loc[i, 'anat']):
                            df_folders.loc[i, 'anat'] = 1
                        else:
                            df_folders.loc[i, 'anat'] += 1
                elif re.search(r'func', j):
                    for k in os.listdir(os.path.join(output_folder, i, j)):
                        if pd.isna(df_folders.loc[i, 'func']):
                            df_folders.loc[i, 'func'] = 1
                        else:
                            df_folders.loc[i, 'func'] += 1
                elif re.search(r'fmap', j):
                    for k in os.listdir(os.path.join(output_folder, i, j)):
                        if pd.isna(df_folders.loc[i, 'fmap']):
                            df_folders.loc[i, 'fmap'] = 1
                        else:
                            df_folders.loc[i, 'fmap'] += 1
                elif re.search(r'misc', j):
                    for k in os.listdir(os.path.join(output_folder, i, j)):
                        if pd.isna(df_folders.loc[i, 'misc']):
                            df_folders.loc[i, 'misc'] = 1
                        else:
                            df_folders.loc[i, 'misc'] += 1
                else:
                    print(f"Folder {j} is not an anat, func, fmap, or misc folder")
    
    df_summary['Subjects'] = Subjects
    df_summary['HC'] = HC
    df_summary['FM'] = FM
    df_summary['T1w'] = T1w
    df_summary['T1wa'] = T1wa
    df_summary['T2w'] = T2w
    df_summary['T2wa'] = T2wa
    df_summary['Rest'] = Rest
    df_summary['Flares'] = Flares
    df_summary['Reward'] = Reward
    df_summary['Callibration'] = Callibration
    df_summary['Localizer'] = Localizer
    df_summary['magnitude1'] = magnitude1
    df_summary['magnitude2'] = magnitude2
    df_summary['phasediff1'] = phasediff1
    df_summary['phasediff2'] = phasediff2
    df_summary['magnitude1_a'] = magnitude1_a
    df_summary['magnitude2_a'] = magnitude2_a
    df_summary['phasediff1_a'] = phasediff1_a
    df_summary['phasediff2_a'] = phasediff2_a
    
    # transpose the df_summary dataframe
    df_summary = df_summary.T
    
    # create excel file with 3 sheets, each sheet is a dataframe 
    with pd.ExcelWriter(os.path.join(output_folder, 'BIDS_output.xlsx')) as writer:
        df.to_excel(writer, sheet_name='Data')
        df_folders.to_excel(writer, sheet_name='Folders Summary')
        df_summary.to_excel(writer, sheet_name='Summary')
                    
                
            
    



if __name__ == '__main__':
    main()
    