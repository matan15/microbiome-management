import tkinter as tk
import customtkinter as ctk
from tkinter.messagebox import showerror, showinfo
from tkinter.filedialog import askdirectory

import threading

import os
import logging

import csv

from utils import get_google_creds
from google.cloud import firestore
from google.cloud.firestore import FieldFilter
from google.oauth2 import service_account

# Getting credentials from .env file
creds = get_google_creds()

# Create google credentials object
credentials = service_account.Credentials.from_service_account_info(creds)

# Connect to the database
db = firestore.Client(
    project=creds["project_id"], credentials=credentials, database="microbiome"
)


def write_dicts_to_csv(dir_path, data, kit_id):
    """
    Save the "data" about the kit id "kit_id" to the "dir_path" as csv file
    """
    fieldnames = data[max(range(len(data)), key=lambda i: len(data[i].keys()))].keys()

    with open(
        os.path.join(dir_path, f"kit_{kit_id}_data.csv"), newline="", mode="a+"
    ) as csvfile:
        csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        csv_writer.writeheader()
        csv_writer.writerows(data)


kit_number_entry = None
status_label = None
progress_var = None
progress_bar = None
submit_button = None
location_entry = None
select_dir_button = None
percently_label = None
location_var = None
kit_number_var = None


def get_kit(notebook):
    """
    Get specific kit data from the database by kit id
    """

    # Step 1: Retrieve selected directory
    selected_dir = location_var.get()

    # Step 2: Retrieve kit number, display error if not a valid number
    try:
        selected_kit = int(kit_number_var.get())
    except ValueError:
        # Except "bad" kit id (not a number)
        showerror(
            "Not Valid Kit ID",
            "You have been entered a kit id that is not a number. please enter a valid kit id.",
        )
        logging.error(
            f"Not Valid Kit ID ({kit_number_var.get()}). You have been entered a kit id that is not a number. please enter a valid kit id."
        )
        return

    # If the kit id value is empty, then the function won't do anything
    if not selected_kit:
        return

    # Disable the buttons to avoid user interaction during the data downloading process
    notebook.configure(state="disabled")
    kit_number_entry.configure(state="disabled")
    select_dir_button.configure(state="disabled")
    submit_button.configure(state="disabled")
    location_entry.configure(state="disabled")

    status_label.configure(text="Initializing connection...")

    # Get the data as a Generator
    records_to_get = (
        db.collection("microbiome")
        .where(filter=FieldFilter("kit_id", "==", selected_kit))
        .stream()
    )

    progress_counter = 0

    # Count total number of records
    records_to_get = [r for r in records_to_get]
    total_records = len(records_to_get)

    # If there is no records, then show an error and enable back the buttons
    if len(records_to_get) == 0:
        showerror("No records found", "There are no records found.")
        status_label.configure(text="No records found in Google")
        location_entry.configure(state="normal")
        select_dir_button.configure(state="normal")
        submit_button.configure(state="normal")
        kit_number_entry.configure(state="normal")
        notebook.configure(state="normal")
        return

    # Create a list of records as dictionaries
    status_label.configure(text="Getting Data...")
    records = []
    for record in records_to_get:
        records.append(record.to_dict())
        progress_counter += 1
        progress = progress_counter / total_records
        progress_var.set(progress)
        percentage_label.configure(text=(("%.2f" % (progress * 100)) + "%"))

    # Call the function that saving the data as a csv file
    write_dicts_to_csv(selected_dir, records, selected_kit)

    status_label.configure(text="The data has been saved!")

    # Display success massage
    showinfo(
        "The file saved successfully",
        f"The file was saved successfully in {selected_dir}",
    )

    # Log success message
    logging.info(f"The file was saved successfullt in {selected_dir}")

    # Re-enable back all the buttons
    notebook.configure(state="normal")
    location_entry.configure(state="normal")
    select_dir_button.configure(state="normal")
    submit_button.configure(state="normal")
    kit_number_entry.configure(state="normal")



def start_processing(notebook):
    # Call the get_kit function as a sub-process
    threading.Thread(target=lambda: get_kit(notebook)).start()


def select_dir():
    # Ask for a directory and pasting the path in the field
    dir_path = askdirectory()
    location_entry.delete(0, tk.END)
    location_entry.insert(0, dir_path)


def get_kit_gui(root, notebook):
    global kit_number_entry, status_label, progress_var, progress_bar, submit_button, location_entry, select_dir_button, percentage_label, location_var, kit_number_var
    title_label = ctk.CTkLabel(
        root, text="Get kit", font=("Helvetica", 16, "bold")
    )
    title_label.pack(pady=10)

    kit_label = ctk.CTkLabel(
        root, text="Enter the Kit ID:", font=("Helvetica", 12)
    )
    kit_label.pack(pady=10)

    kit_number_var = ctk.StringVar()
    kit_number_entry = ctk.CTkEntry(root, width=300, font=("Helvetica", 12), textvariable=kit_number_var)
    kit_number_entry.pack(pady=10)

    location_label = ctk.CTkLabel(
        root,
        text="Select a folder where you want to save samples:",
        font=("Helvetica", 12)
    )
    location_label.pack(pady=10)

    location_var = ctk.StringVar()
    location_entry = ctk.CTkEntry(root, width=300, font=("Helvetica", 12), textvariable=location_var)
    location_entry.pack(pady=10)

    select_dir_button = ctk.CTkButton(
        root,
        text="Browse",
        command=select_dir,
        fg_color=("#007acc", "#007acc"),
        text_color=("white", "white"),
        font=("Helvetica", 12),
    )
    select_dir_button.pack(pady=10)

    status_label = ctk.CTkLabel(
        root, text="", font=("Helvetica", 12)
    )
    status_label.pack(pady=10)

    progress_var = ctk.DoubleVar()
    progress_bar = ctk.CTkProgressBar(
        root, width=300, variable=progress_var, mode="determinate", orientation="horizontal"
    )
    progress_bar.pack(pady=10)

    percentage_label = ctk.CTkLabel(
        root, text="0%", font=("Helvetica", 12), 
    )
    percentage_label.pack()

    status_label = ctk.CTkLabel(
        root, text="", font=("Helvetica", 12), 
    )
    status_label.pack()

    submit_button = ctk.CTkButton(
        root,
        text="Submit",
        command=lambda: start_processing(notebook),
        fg_color=("#4CAF50", "#4CAF50"),
        text_color=("white", "white"),
        font=("Helvetica", 12),
        hover=True,
        corner_radius=5
    )
    submit_button.pack(pady=10)
