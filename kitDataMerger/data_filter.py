import os

import re
import shutil
import tkinter as tk

def filter(data_dir: str, progress_var: tk.DoubleVar, percentage_label: tk.Label, status_label: tk.Label, sample_type):
    # If the destination direcorty already exists, delete it
    if os.path.exists(f'./kitDataMerger/filtered_data'):
        shutil.rmtree(f'./kitDataMerger/filtered_data')

    # Initialise a filtered-file counter to track progress
    progress_counter = 0

    # Count how many files to be filtered are there
    num_files = sum([len(files) for root_dir, cur_dir, files in os.walk(data_dir) if 'ASV' in root_dir]) if sample_type == "Fungi" else sum([1 for _ in os.listdir(data_dir)])
    
    # Set the progress bar text label
    status_label.config(text='Filtering data...')

    # For each and every raw data directory, create a twin direcory in the destination directory
    os.makedirs(f'./kitDataMerger/filtered_data')
    if sample_type == "Fungi":
        for dirname in os.listdir(data_dir):
            # Try to read the ASV directory from the raw data
            try:
                # Iterate through all the files in the ASV directory
                for filename in os.listdir(f'{data_dir}/{dirname}/ASV'):

                    # If the filename matches the pattern (S[number][any other text]), copy it to the filtered data directory
                    if re.match(r'^S(\d+)_(Fr|R|S|F|L)(.*)', filename):
                        with open(f'./kitDataMerger/filtered_data/{filename}', 'w') as f:
                            shutil.copy2(f'{data_dir}/{dirname}/ASV/{filename}', f'./kitDataMerger/filtered_data/{filename.upper() if not "Fr" in filename else filename}')

                    # Count the file as "filtered", calculate and update the progress
                    progress_counter += 1
                    progress = (progress_counter / num_files) * 100
                    progress_var.set(progress)
                    percentage_label.config(text=(('%.2f ' % progress) + '%'))

            # If there is no ASV directory, alert the user
            except FileNotFoundError:
                percentage_label.config(text='0%')
                return False  # As an error
    elif sample_type == "Bacteria":
        for filename in os.listdir(data_dir):
            if re.match(r'^S(\d+)_(Fr|R|S|F|L)*', filename):
                with open(f'./kitDataMerger/filtered_data/{filename}', 'w') as f:
                    shutil.copy2(f'{data_dir}/{filename}', f'./kitDataMerger/{filename.upper() if not "Fr" in filename else filename}')

            progress_counter += 1
            progress = (progress_counter / num_files) * 100
            progress_var.set(progress)
            percentage_label.config(text=(('%.2f' % progress) + "%"))

    return True  # As a success
