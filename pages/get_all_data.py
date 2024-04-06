import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askdirectory
from tkinter.messagebox import showinfo, showerror

import threading

import os

import csv

import logging

from utils import get_google_creds
from google.cloud import firestore
from google.oauth2 import service_account

# Get credentials from the .env file
creds = get_google_creds()

# Create a Google credentials object
credentials = service_account.Credentials.from_service_account_info(creds)

# Connect to the database
db = firestore.Client(
    project=creds["project_id"], credentials=credentials, database="microbiome"
)

location_entry = None
select_dir_button = None
submit_button = None
percentage_label = None
progress_var = None
status_label = None


def write_dicts_to_csv(dir_path, data):
    """
    Writes a list of dictionaries to a CSV file in the specified directory.

    Args:
        dir_path (str): The directory path where the CSV file should be saved.
        data (list): A list of dictionaries to be written to the CSV file.

    Returns:
        None
    """
    fieldnames = data[max(range(len(data)), key=lambda i: len(data[i].keys()))].keys()

    with open(
        os.path.join(dir_path, "microbiome_data.csv"), newline="", mode="a+"
    ) as csvfile:
        csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        csv_writer.writeheader()
        csv_writer.writerows(data)


def get_data(notebook):
    # Retrieve selected directory
    selected_dir = location_entry.get()

    # If the directory is not provided, return without performing any action
    if not selected_dir:
        return

    # Disable all the buttons to avoid user interaction.
    for i in range(0, 7):
        if i == 4:
            continue
        notebook.tab(i, state=tk.DISABLED)
    location_entry.config(state=tk.DISABLED)
    select_dir_button.config(state=tk.DISABLED)
    submit_button.config(state=tk.DISABLED)

    status_label.config(text="Initalizing connection...")

    # Get records from the database
    records_to_get = db.collection("microbiome").stream()

    progress_counter = 0

    # Count total records
    records_to_get = [r for r in records_to_get]
    total_records = len(records_to_get)

    # If the total records is 0, show error message and re-enable back all the buttons
    if total_records == 0:
        showerror("No records found", "There are no records found.")
        for i in range(0, 7):
            if i == 4:
                continue
            notebook.tab(i, state=tk.NORMAL)
        status_label.config(text="")
        logging.info("No records found in Google.")
        location_entry.config(state=tk.NORMAL)
        select_dir_button.config(state=tk.NORMAL)
        submit_button.config(state=tk.NORMAL)
        return

    status_label.config(text="Getting data...")

    # Create a list of all the records as dictionaries
    records = []
    for record in records_to_get:
        records.append(record.to_dict())
        progress_counter += 1
        progress = (progress_counter / total_records) * 100
        progress_var.set(progress)
        percentage_label.config(text=(("%.2f" % progress) + "%"))

    # Write the retrieved data to a CSV file in the selected directory
    write_dicts_to_csv(selected_dir, records)

    # Update status label to indicate successful data retrieval and file saving
    status_label.config(text="The file was saved successfully.")

    # Display information message indicating successful file save
    showinfo(
        "The file saved successfully",
        f"The file was saved successfully in {selected_dir}",
    )

    # Log success message
    logging.info(f"The file was saved successfully in {selected_dir}")

    # Re-enable Tkinter widgets for future operations
    for i in range(0, 7):
        if i == 4:
            continue
        notebook.tab(i, state=tk.NORMAL)
    location_entry.config(state=tk.NORMAL)
    select_dir_button.config(state=tk.NORMAL)
    submit_button.config(state=tk.NORMAL)


def select_dir():
    # Ask for a directory and pasting the path in the field
    dir_path = askdirectory()
    location_entry.delete(0, tk.END)
    location_entry.insert(0, dir_path)


def start_processing(notebook):
    # call the get_data function as a sub-process
    threading.Thread(target=lambda: get_data(notebook)).start()


def get_all_data_gui(root, notebook):
    global location_entry, select_dir_button, submit_button, progress_var, percentage_label, status_label
    title_label = ttk.Label(
        root,
        text="Get All Samples",
        font=("Helvetica", 16, "bold"),
        background="#dcdad5",
    )
    title_label.pack(pady=10)

    location_label = ttk.Label(
        root,
        text="Select a folder where you want to save samples:",
        font=("Helvetica", 12),
        background="#dcdad5",
    )
    location_label.pack(pady=10)

    location_entry = ttk.Entry(root, width=40, font=("Helvetica", 12))
    location_entry.pack(pady=10)

    select_dir_button = tk.Button(
        root,
        text="Browse",
        command=select_dir,
        background="#007acc",
        fg="white",
        font=("Helvetica", 12),
    )
    select_dir_button.pack(pady=10)

    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(
        root, length=300, variable=progress_var, mode="determinate"
    )
    progress_bar.pack(pady=10)

    percentage_label = ttk.Label(
        root, text="0%", font=("Helvetica", 12), background="#dcdad5"
    )
    percentage_label.pack()

    status_label = ttk.Label(
        root, text="", font=("Helvetica", 12), background="#dcdad5"
    )
    status_label.pack()

    submit_button = tk.Button(
        root,
        text="Submit",
        command=lambda: start_processing(notebook),
        background="#4CAF50",
        fg="white",
        font=("Helvetica", 12),
    )
    submit_button.pack(pady=10)
