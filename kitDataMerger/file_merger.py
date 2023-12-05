import os

import re
import shutil
import tkinter as tk

import pandas as pd

def merge_data(progress_var: tk.DoubleVar, percentage_label: tk.Label, status_label: tk.Label):
    # If the destination directory already exists, delete it
    if os.path.exists(f'./kitDataMerger/merged_asv_data'):
        shutil.rmtree(f'./kitDataMerger/merged_asv_data')

    # Initialise a merged-file counter to track progress
    progress_counter = 0

    # Count how many files to be merged are there
    num_files = sum([len(files) for root_dir, cur_dir, files in os.walk(f'./kitDataMerger/filtered_data')])

    # Set the progress bar text label
    status_label.config(text='Merging data...')

    # For each and every filtered data directory, create a twin directory in the destination directory
    os.makedirs(f'./kitDataMerger/merged_asv_data')

    # Create a dictionary that will hold the merged data in the future, in the following format:
    # {
    #   kit_id: {
    #       bacteria_id: {
    #           'F': f_prob,
    #           'R': r_prob,
    #           'Fr': fr_prob,
    #           'S': s_prob
    #       }
    #   }
    # }

    mdata = {}

    # Iterate through all the filtered files
    for filename in os.listdir(f'./kitDataMerger/filtered_data'):

        # Clean filename from extension and irrelevent info
        clean_filename = filename.split('.')[0].split('_')[0]

        # Use a RegEx pattern to split the clean filename into two groups - kit id and sample category (F, R, Fr, S)
        match = re.search(r'S(\d+)([A-Za-z]+)', clean_filename)

        # In case of a split error, count the file as "merged" and continue to the next one
        if not match:
            progress_counter += 1
            continue

        kit_id = match.group(1)
        sample = match.group(2)
        sample = sample.upper() if sample != "Fr" else sample

        # Use Pandas to read the filtered data
        df = pd.read_csv(f'./kitDataMerger/filtered_data/{filename}')

        # Format the data into a dictionary
        df_dict = df.to_dict(orient='index')

        # Iterate through the data and pour it into the merged data dictionary
        # (the data is stored by line numbers which are redundant in this case, so iterate values only)
        for v in df_dict.values():
            mdata.setdefault(kit_id, {}).setdefault(v.get('id'), {'F': 0, 'R': 0, 'S': 0, 'Fr': 0})[
                sample] = v.get('prob')

        # Count the file as "merged", calculate and update the progress
        progress_counter += 1
        progress = (progress_counter / num_files) * 100
        progress_var.set(progress)
        percentage_label.config(text=(('%.2f ' % progress) + '%'))

    shutil.rmtree(f'./kitDataMerger/filtered_data')
    return _save_to_csv(mdata)

def _sum_prob(d):
    '''
    Sums the prob values of each
    '''
    ret = {'F': 0, 'R': 0, 'S': 0, 'Fr': 0}
    for id, probs in d.items():
        for sample in ret.keys():
            ret[sample] += probs[sample]
    return ret


def _save_to_csv(mdata):
    m_files_counter = 0
    for kit, d in mdata.items():
        m_files_counter += 1
        prob_sum = _sum_prob(d)
        formatted_data = {'kit_id': [], 'Kingdom': [], 'Philum': [], 'Class': [], 'Order': [], 'Family': [], 'Genus': [],
            'Species': [], 'F': [], 'R': [], 'S': [], 'Fr': []}

        samples = ['F', 'R', 'S', 'Fr']

        for id, probs in d.items():
            # Split the id column to column code and the data
            id = id.split(';')
            id = [s.split('__') for s in id]

            # Add the data to a dict
            formatted_data['kit_id'].append(kit)
            formatted_data['Kingdom'].append(id[0][1].replace('_', ' ') if id[0][1] != '' else '__')
            formatted_data['Philum'].append(id[1][1].replace('_', ' ') if id[1][1] != '' else '__')
            formatted_data['Class'].append(id[2][1].replace('_', ' ') if id[2][1] != '' else '__')
            formatted_data['Order'].append(id[3][1].replace('_', ' ') if id[3][1] != '' else '__')
            formatted_data['Family'].append(id[4][1].replace('_', ' ') if id[4][1] != '' else '__')
            formatted_data['Genus'].append(id[5][1].replace('_', ' ') if id[5][1] != '' else '__')
            formatted_data['Species'].append(id[6][1].replace('_', ' ') if id[6][1] != '' else '__')
            for sample in samples:
                try:
                    formatted_data[sample].append(float(probs[sample] / prob_sum[sample]))
                except ZeroDivisionError:
                    formatted_data[sample].append(0)


        # Convert the dict to a CSV file
        formatted_df = pd.DataFrame.from_dict(formatted_data)
        formatted_df.to_csv(path_or_buf=f'./kitDataMerger/merged_asv_data/S_{kit}_Fungi.csv', index=False)
    return m_files_counter

