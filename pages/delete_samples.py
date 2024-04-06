from tkinter import ttk
import tkinter as tk
import threading
from tkinter.messagebox import showerror, showinfo, askyesno

import logging

from google.cloud import firestore
from google.oauth2 import service_account
from google.cloud.firestore import FieldFilter

from utils import get_google_creds

# Get the credentials from .env file
creds = get_google_creds()

# Create google credentials object
credentials = service_account.Credentials.from_service_account_info(creds)

# Connect to the database
db = firestore.Client(
    project=creds["project_id"], credentials=credentials, database="microbiome"
)

kit_number_entry = None
submit_button = None
status_label = None
selected_type = None
progress_var = None
percentage_label = None
type_dropdown = None


def delete_samples(notebook):
    # Attempt to convert the kit number to an integer; display an error if not a valid number
    try:
        selected_kit = int(kit_number_entry.get())
    except ValueError:
        showerror(
            "Not Valid Kit ID",
            "You have been entered a kit id that is not a number. please enter a valid kit id.",
        )
        logging.error(
            f"Not Valid Kit ID ({kit_number_entry.get()}). You have been entered a kit id that is not a number. please enter a valid kit id."
        )
        return

    # If the kit number is not provided or not a valid number, return without performing any action
    if not selected_kit:
        return

    # Ask for user confirmation before proceeding with the deletion operation
    if not askyesno(
        "Confirm delete",
        f"Are you sure you want to delete All the {selected_type.get() if selected_type.get() != 'All' else ''} records in the kit {selected_kit}",
    ):
        return

    # Disable all the buttons to prevent user interaction
    for i in range(0, 7):
        if i == 2:
            continue
        notebook.tab(i, state=tk.DISABLED)
    kit_number_entry.config(state=tk.DISABLED)
    submit_button.config(state=tk.DISABLED)
    type_dropdown.config(state=tk.DISABLED)

    # Step 6: Update status label
    status_label.config(text="Deleting...")

    if selected_type.get() != "All":
        # if the user don't want to delete all the data but a specific Kingdom, the fuction will create a query with a filter
        query = (
            db.collection("microbiome")
            .where(filter=FieldFilter("Kingdom", "==", selected_type.get()))
            .where(filter=FieldFilter("kit_id", "==", selected_kit))
        )
    else:
        # If the user selects "All", then the function will query all the data
        query = db.collection("microbiome")

    # Create a data generator object
    records_to_delete = query.stream()

    # Count total amount of records
    total_records = 0
    for record in records_to_delete:
        total_records += 1

    # If the total amount is 0, re-enable back all the buttons and show an error message
    if total_records == 0:
        kit_number_entry.config(state=tk.NORMAL)
        submit_button.config(state=tk.NORMAL)
        for i in range(0, 7):
            if i == 2:
                continue
            notebook.tab(i, state=tk.NORMAL)
        showerror(
            title="No records found",
            message="No records found matching these creterias.",
        )
        return

    count = 0

    # If there are records, the function will delete them
    for record in query.stream():
        record.reference.delete()
        count += 1
        progress = (count / total_records) * 100
        progress_var.set(progress)
        percentage_label.config(text=(("%.2f " % progress) + "%"))

    # Update status label and display success message
    status_label.config(text="The Kit has been deleted")
    showinfo("The kit has been deleted", "The kit has been deleted successfully.")

    # Log deletion operation as a success
    logging.info(f"The kit {selected_kit} has been deleted successfully.")

    # Re-enable back all the buttons
    kit_number_entry.config(state=tk.NORMAL)
    submit_button.config(state=tk.NORMAL)
    type_dropdown.config(state=tk.NORMAL)
    for i in range(0, 7):
        if i == 2:
            continue
        notebook.tab(i, state=tk.NORMAL)


def start_processing(notebook):
    # Call the delete_samples function as a sub-process
    threading.Thread(target=lambda: delete_samples(notebook)).start()


def delete_samples_gui(root, notebook):
    global kit_number_entry, submit_button, status_label, selected_type, progress_var, percentage_label, type_dropdown
    title_label = ttk.Label(
        root, text="Delete Kit", font=("Helvetica", 16, "bold"), background="#dcdad5"
    )
    title_label.pack(pady=10)

    selected_type = tk.StringVar()
    selected_type.set("Fungi")
    type_dropdown = ttk.OptionMenu(
        root, selected_type, "Fungi", "Fungi", "Bacteria", "Archaea", "Eukaryota", "All"
    )
    type_dropdown.pack(pady=10)

    kit_label = ttk.Label(
        root, text="Enter the Kit ID:", font=("Helvetica", 12), background="#dcdad5"
    )
    kit_label.pack(pady=10)

    kit_number_entry = ttk.Entry(root, width=40, font=("Helvetica", 12))
    kit_number_entry.pack(pady=10)

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

    status_label = ttk.Label(
        root, text="", font=("Helvetica", 12), background="#dcdad5"
    )
    status_label.pack(pady=10)

    submit_button = tk.Button(
        root,
        text="Delete",
        font=("Helvetica", 12),
        command=lambda: start_processing(notebook),
        background="red",
        fg="white",
    )
    submit_button.pack()
