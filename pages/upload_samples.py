import os

import shutil
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter.messagebox import showinfo, showerror, showwarning

import logging
from datetime import datetime

from GCP.connect_GCP import fetch_and_index_data

from kitDataMerger.data_filter import filter
from kitDataMerger.file_merger import merge_data
from kitDataMerger.meta_data_merger import merge_meta_data
from kitDataMerger.meteorology.get_weather import update_weather
from kitDataMerger.fungi.update_fungi_ids import update_fungi_ids

log_file_path = (
    f"./logs/kit_data_merger-{datetime.now().strftime('%d-%m-%Y-%H.%M.%S')}.log"
)
logging.basicConfig(
    filename=log_file_path,
    level=logging.DEBUG,
    filemode="a+",
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%d/%m/%Y %I:%M:%S %p",
)

logger = logging.getLogger(__name__)

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
status_sub_label = None
generate_check = None
selected_type = None
samples_type_optionbox = None


def upload_samples(notebook):
    # Getting the data dir path, meta data file path and the upload type
    selected_dir = dir_entry.get()
    selected_meta = meta_entry.get()
    upload_type = selected_type.get()

    # Making sure that the data dir path and meta data file path are not empty
    if not selected_dir or not selected_meta:
        return

    # Disable all the buttons to avoid user interaction during the upload.
    for i in range(0, 7):
        if i == 1:
            continue
        notebook.tab(i, state=tk.DISABLED)
    submit_button.config(state=tk.DISABLED)
    select_dir_button.config(state=tk.DISABLED)
    select_meta_button.config(state=tk.DISABLED)
    dir_entry.config(state=tk.DISABLED)
    meta_entry.config(state=tk.DISABLED)
    generate_check.config(state=tk.DISABLED)
    samples_type_optionbox.config(state=tk.DISABLED)

    # Initializing the progress bar
    percentage_label.config(text="0%")
    status_label.config(text="Working...")

    # If the upload type is Fungi, the program will also search for ids of the Fungis
    if upload_type == "Fungi":
        status_label.config(text="Geting Fungi Ids")
        update_fungi_ids(selected_dir, progress_var, percentage_label)

    if filter(
        (
            selected_dir
            if upload_type != "Fungi"
            else "./kitDataMerger/fungi/data/microbiome-public"
        ),
        progress_var,
        percentage_label,
        status_label,
        upload_type,
    ):

        # Merge samples
        num_files = merge_data(
            progress_var, percentage_label, status_label, upload_type
        )

        # Updating the meteorologic data
        status_label.config(text="Getting weather:")
        if not update_weather(
            selected_meta, 32, progress_var, percentage_label, status_sub_label
        ):
            shutil.rmtree("./kitDataMerger/merged_asv_data")
            return

        # Merge the meta data with the samples
        merge_meta_data()

        # Uploading of the data if the user chose to upload it.
        if check_var.get() == 1:
            fetch_and_index_data(
                progress_var,
                percentage_label,
                status_label,
                num_files,
                index_name="microbiome",
            )

        status_label.config(text="Saving data...")
        status_sub_label.config(text="")

        bad_dir = True
        # Ask for a new destination if merged data already exists in the selected one
        while bad_dir:
            try:
                # Ask for a directory and copy all the public data to the destination
                path = filedialog.askdirectory()
                os.makedirs(f"{path}/microbiome-output/microbiome-public-data")
                for filename in os.listdir(f"kitDataMerger/microbiome-public"):
                    with open(
                        f"{path}/microbiome-output/microbiome-public-data/{filename}",
                        "w",
                    ) as f:
                        shutil.copy2(
                            f"kitDataMerger/microbiome-public/{filename}",
                            f"{path}/microbiome-output/microbiome-public-data/{filename}",
                        )

                # If the upload type is a fungi, the function will also copy the private data (lab data)
                if upload_type == "Fungi":
                    os.makedirs(f"{path}/microbiome-output/microbiome-private-data")
                    for seq_folder in os.listdir(
                        f"kitDataMerger/fungi/data/microbiome-private"
                    ):
                        for filename in os.listdir(
                            f"kitDataMerger/fungi/data/microbiome-private/{seq_folder}"
                        ):
                            with open(
                                f"{path}/microbiome-output/microbiome-private-data/{filename}",
                                "w",
                            ) as f:
                                shutil.copy2(
                                    f"kitDataMerger/fungi/data/microbiome-private/{seq_folder}/{filename}",
                                    f"{path}/microbiome-output/microbiome-private-data/{filename}",
                                )
                # Remove the work directories
                shutil.rmtree(f"./kitDataMerger/merged_asv_data")
                shutil.rmtree(f"./kitDataMerger/microbiome-public")
                if upload_type == "Fungi":
                    shutil.rmtree(f"./kitDataMerger/fungi/data")
                os.remove(f"./kitdataMerger/meteorology/meta_data_final.csv")

                # Alert the users when the files have been saved successfully
                showinfo(
                    "Saved successfully",
                    "The files have been save successfully as 'microbiome-data' directory.",
                )

                bad_dir = False

            # In case of a "bad" directory
            except FileExistsError:
                showerror(
                    "Cannot save the data",
                    "It seems there is already merged data in the selected directory,"
                    " please delete/move it or choose a different directory and then try again.",
                )
                bad_dir = True
                continue

        # Update the status message when all the files have been merged
        status_label.config(text="All files has been generated!")
        status_sub_label.config(text="")

    else:
        # Alert if there was any problem with filtering the data
        showerror(
            "There was a problem",
            "There was a problem with filtering the data, please try again later.",
        )

    # Alert if there was any error in the log file
    with open(log_file_path, "r") as log_file:
        content = log_file.read()
        if "ERROR" in content:
            showwarning(
                "Some errors occured",
                f"There was some errors while processing and uploading the data, check the log file '{os.path.abspath(log_file_path)}'",
            )

    # Enabeling back all the buttons
    submit_button.config(state=tk.NORMAL)
    select_dir_button.config(state=tk.NORMAL)
    select_meta_button.config(state=tk.NORMAL)
    dir_entry.config(state=tk.NORMAL)
    meta_entry.config(state=tk.NORMAL)
    generate_check.config(state=tk.NORMAL)
    samples_type_optionbox.config(state=tk.NORMAL)
    for i in range(0, 7):
        if i == 1:
            continue
        notebook.tab(i, state=tk.NORMAL)


def start_processing(notebook):
    # Start the main function (upload_samples) with a subprocess
    progress_var.set(0)
    threading.Thread(target=lambda: upload_samples(notebook)).start()


def select_dir():
    # Ask for a directory and pasting the path in the field
    dir_path = filedialog.askdirectory()
    dir_entry.delete(0, tk.END)
    dir_entry.insert(0, dir_path)


def select_file():
    # Ask for a file and pasting the path in the field
    file_path = filedialog.askopenfilename()
    meta_entry.delete(0, tk.END)
    meta_entry.insert(0, file_path)


def upload_samples_gui(root, notebook):
    global dir_entry, meta_label, meta_entry, select_meta_button, select_dir_button, submit_button, progress_var, progress_bar, percentage_label, status_label, check_var, status_sub_label, generate_check, selected_type, samples_type_optionbox

    # Create a title for the application
    title_label = ttk.Label(
        root,
        text="Upload Samples",
        font=("Helvetica", 16, "bold"),
        background="#dcdad5",
    )
    title_label.pack(pady=10)

    samples_type_label = ttk.Label(
        root,
        text="Select type of samples:",
        font=("Helvetica", 14),
        background="#dcdad5",
    )
    samples_type_label.pack(pady=10)

    # Radio buttons to choose the type of the sample
    selected_type = tk.StringVar()
    selected_type.set("Fungi")
    samples_type_optionbox = ttk.OptionMenu(
        root, selected_type, "Fungi", "Fungi", "Bacteria"
    )
    samples_type_optionbox.pack(pady=10)

    # Create a label widget for the directory entry
    dir_label = ttk.Label(
        root, text="Select a directory:", font=("Helvetica", 14), background="#dcdad5"
    )
    dir_label.pack(pady=10)

    # Create an entry widget to display the selected directory path
    dir_entry = ttk.Entry(root, width=40, font=("Helvetica", 12))
    dir_entry.pack(pady=10)

    # Create a button to select a directory
    select_dir_button = tk.Button(
        root,
        text="Browse",
        command=select_dir,
        background="#007acc",
        fg="white",
        font=("Helvetica", 12),
    )
    select_dir_button.pack(pady=10)

    # Create a label widget for the Meta Data File
    meta_label = ttk.Label(
        root,
        text="Select a meta data file:",
        font=("Helvetica", 14),
        background="#dcdad5",
    )
    meta_label.pack(pady=10)

    # Create an entry widget to display the selected file path
    meta_entry = ttk.Entry(root, width=40, font=("Helvetica", 12))
    meta_entry.pack(pady=10)

    # Create a button to select a file
    select_meta_button = tk.Button(
        root,
        text="Browse",
        command=select_file,
        background="#007acc",
        fg="white",
        font=("Helvetica", 12),
    )
    select_meta_button.pack(pady=10)

    # Create Submit button
    submit_button = tk.Button(
        root,
        text="Submit",
        command=lambda: start_processing(notebook),
        background="#4CAF50",
        fg="white",
        font=("Helvetica", 12),
    )
    submit_button.pack(pady=10)

    # Create a progress bar
    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(
        root, length=300, variable=progress_var, mode="determinate"
    )
    progress_bar.pack(pady=10)

    # Create a label to display the progress percentage
    percentage_label = ttk.Label(
        root, text="0%", font=("Helvetica", 12), background="#dcdad5"
    )
    percentage_label.pack()

    # Create a label to display the status message
    status_label = ttk.Label(
        root, text="", font=("Helvetica", 12), background="#dcdad5"
    )
    status_label.pack()

    status_sub_label = ttk.Label(
        root, text="", font=("Helvetica", 12), background="#dcdad5"
    )
    status_sub_label.pack()

    # Create a checkbox to generate a command bulk
    check_var = tk.IntVar()
    generate_check = tk.Checkbutton(
        root,
        text="Upload Samples",
        variable=check_var,
        onvalue=1,
        offvalue=0,
        font=("Helvetica", 14),
        background="#dcdad5",
    )
    generate_check.pack()
