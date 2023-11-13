from AWS.connect_ES import fetch_and_index_data

import os
import sys

parent_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(parent_dir)

import shutil
import threading
import tkinter as tk
from tkinter import filedialog
from tkinter.messagebox import showinfo, showerror
from tkinter.ttk import Progressbar

from kitDataMerger.data_filter import filter
from kitDataMerger.file_merger import merge_data
from kitDataMerger.meta_data_merger import merge_meta_data

dir_entry = None
select_dir_button = None
submit_button = None
progress_var = None
progress_bar = None
percentage_label = None
status_label = None
check_var = None
meta_label = None
meta_entry = None
select_meta_button = None

def perform_actions():
    # Get the value of the field (the path)
    selected_dir = dir_entry.get()
    selected_meta = meta_entry.get()
    if not selected_dir or not selected_meta:
        return

    # Disable the "Browse" and "Submit" buttons
    submit_button.config(state=tk.DISABLED)
    select_dir_button.config(state=tk.DISABLED)
    select_meta_button.config(state=tk.DISABLED)

    # Call the filter and merge functions
    if filter(selected_dir, progress_var, percentage_label, status_label):

        # Initialising the progress bar
        percentage_label.config(text='0%')
        status_label.config(text='Working...')

        # Merge files
        num_files = merge_data(progress_var, percentage_label, status_label)

        merge_meta_data(selected_meta)

        if check_var.get() == 1:
            fetch_and_index_data(progress_var, percentage_label, status_label, num_files)

        # Update the status message when all the files have been merged
        status_label.config(text='All files has been generated!')

        bad_dir = True
        # Ask for a new destination if merged data already exists in the selected one
        while bad_dir:
            try:
                # Ask for a directory and copy all the data to the destination
                path = filedialog.askdirectory()
                os.makedirs(f"{path}/merged_asv_data")
                for filename in os.listdir(f'{parent_dir}/kitDataMerger/merged_asv_data'):
                    with open(f'{path}/merged_asv_data/{filename}', 'w') as f:
                        shutil.copy2(f'{parent_dir}/kitDataMerger/merged_asv_data/{filename}',
                                     f'{path}/merged_asv_data/{filename}')

                shutil.rmtree(f"{parent_dir}/kitDataMerger/merged_asv_data")

                # Enable the buttons once again
                submit_button.config(state=tk.NORMAL)
                select_dir_button.config(state=tk.NORMAL)
                select_meta_button.config(state=tk.NORMAL)

                # Alert the users when the files have been saved successfully
                showinfo("Saved successfully", "The files have been save successfully as 'merged_asv_data' directory.")

                bad_dir = False

            # In case of a "bad" directory
            except FileExistsError:
                showerror('Cannot save the data',
                          'It seems there is already merged data in the selected directory,'
                          ' please delete/move it or choose a different directory and then try again.')
                bad_dir = True
                continue


    else:
        # Show a message if there is no ASV directory
        status_label.config(text='No ASV directory')

    submit_button.config(state=tk.NORMAL)
    select_dir_button.config(state=tk.NORMAL)


def start_processing():
    # Start the main function (perform_actions) with a subprocess
    progress_var.set(0)
    threading.Thread(target=perform_actions).start()


def select_dir():
    # Ask for a directory and pasting the path in the field
    dir_path = filedialog.askdirectory()
    dir_entry.delete(0, tk.END)
    dir_entry.insert(0, dir_path)

def select_file():
    file_path = filedialog.askopenfilename()
    meta_entry.delete(0, tk.END)
    meta_entry.insert(0, file_path)

def run_gui():
    global dir_entry, meta_label, meta_entry, select_meta_button, select_dir_button, submit_button, progress_var, progress_bar, percentage_label, status_label, check_var
    # Create the main window
    root = tk.Tk()
    root.title('Samples Merger')

    # Set the size and the color of the window
    root.geometry('400x515')
    root.configure(bg='#f0f0f0')

    # Create a title for the application
    title_label = tk.Label(root, text='Samples Merger', font=('Helvetica', 16, 'bold'))
    title_label.pack(pady=10)

    # Create a label widget for the directory entry
    dir_label = tk.Label(root, text='Select a directory:', font=('Helvetica', 14))
    dir_label.pack(pady=10)

    # Create an entry widget to display the selected directory path
    dir_entry = tk.Entry(root, width=40, font=('Helvetica', 12))
    dir_entry.pack(pady=10)

    # Create a button to select a directory
    select_dir_button = tk.Button(root, text='Browse', command=select_dir, bg='#007acc', fg='white',
                              font=('Helvetica', 12))
    select_dir_button.pack(pady=10)

    # Create a label widget for the Meta Data File
    meta_label = tk.Label(root, text='Select a meta data file:', font=('Helvetica', 14))
    meta_label.pack(pady=10)

    # Create an entry widget to display the selected file path
    meta_entry = tk.Entry(root, width=40, font=('Helvetica', 12))
    meta_entry.pack(pady=10)

    # Create a button to select a file
    select_meta_button = tk.Button(root, text='Browse', command=select_file, bg='#007acc', fg='white', font=('Helvetica', 12))
    select_meta_button.pack(pady=10)


    # Create Submit button
    submit_button = tk.Button(root, text='Submit', command=start_processing, bg='#4CAF50', fg='white',
                              font=('Helvetica', 12))
    submit_button.pack(pady=10)

    # Create a progress bar
    progress_var = tk.DoubleVar()
    progress_bar = Progressbar(root, length=300, variable=progress_var, mode='determinate')
    progress_bar.pack(pady=10)

    # Create a label to display the progress percentage
    percentage_label = tk.Label(root, text='0%', font=('Helvetica', 12))
    percentage_label.pack()

    # Create a label to display the status message
    status_label = tk.Label(root, text='', font=('Helvetica', 12))
    status_label.pack()

    # Create a checkbox to generate a command bulk
    check_var = tk.IntVar()
    generate_check = tk.Checkbutton(root, text="Upload to OpenSearch", variable=check_var, onvalue=1, offvalue=0, font=('Helvetica', 14))
    generate_check.pack()

    # run the application
    root.mainloop()

if __name__ == '__main__':
    run_gui()