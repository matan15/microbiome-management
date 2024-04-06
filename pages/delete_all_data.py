import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo, askyesno

import threading

import logging

from utils import get_google_creds
from google.cloud import firestore
from google.cloud.firestore import FieldFilter
from google.oauth2 import service_account

# Get credentials from .env file
creds = get_google_creds()

# Create google credentials object
credentials = service_account.Credentials.from_service_account_info(creds)

# Connect to the database
db = firestore.Client(
    project=creds["project_id"], credentials=credentials, database="microbiome"
)

submit_button = None
status_label = None
selected_type = None
progress_var = None
percentage_label = None
type_dropdown = None


def delete_data(notebook):
    # Ask for user confirmation
    if not askyesno(
        "Are you sure?",
        "Are you sure you want to delete all the data? Note that there is no way to cancel this operation.",
    ):
        return

    # Disable buttons to prevent user interaction during deletion process
    for i in range(0, 7):
        if i == 3:
            continue
        notebook.tab(i, state=tk.DISABLED)
    submit_button.config(state=tk.DISABLED)
    type_dropdown.config(state=tk.DISABLED)

    # Update status label
    status_label.config(text="deleting...")

    if selected_type.get() == "All":
        # If the user selected "All" in the deletion type, the function will query all the data
        query = db.collection("microbiome")
    else:
        # If the user selected a specific Kingdom to delete, the function will query all the data with this Kingdom
        query = db.collection("microbiome").where(
            filter=FieldFilter("Kingdom", "==", selected_type.get())
        )

    # Create records generator object
    records_to_delete = query.stream()

    count = 0
    # Count total amount of records to delete
    total_records = sum(1 for _ in records_to_delete)

    batch = db.batch()

    # Delete the records in batches
    while True:
        deleted = 0
        for doc in query.limit(500).stream():
            doc_ref = db.collection("microbiome").document(doc.id)
            batch.delete(doc_ref)
            count += 1
            deleted += 1
            progress = (count / total_records) * 100
            progress_var.set(progress)
            percentage_label.config(text=(("%.2f " % progress) + "%"))

        if deleted == 0:
            break
        batch.commit()

    # Update status label and display success message
    status_label.config(text="The data has been deleted successfully.")
    showinfo("The data has been deleted", "The data has been deleted successfully.")

    # Log deletion operation as a success
    logging.info("The data has been deleted successfully.")

    # Re-enable the buttons back
    submit_button.config(state=tk.NORMAL)
    type_dropdown.config(state=tk.NORMAL)
    for i in range(0, 7):
        if i == 3:
            continue
        notebook.tab(i, state=tk.NORMAL)


def start_processing(notebook):
    # Call the deletion function as a sub-process
    threading.Thread(target=lambda: delete_data(notebook)).start()


def delete_all_data_gui(root, notebook):
    global submit_button, status_label, selected_type, progress_var, percentage_label, type_dropdown

    # Create the title label for the GUI
    title_label = ttk.Label(
        root,
        text="Delete All the data",
        font=("Helvetica", 16, "bold"),
        background="#dcdad5",
    )
    title_label.pack(pady=10)

    # Create the warning label for the GUI
    warning_label = ttk.Label(
        root,
        text="WARNING: All the data will be deleted",
        font=("Helvetica", 14, "bold"),
        foreground="red",
        background="#dcdad5",
    )
    warning_label.pack(pady=10)

    selected_type = tk.StringVar()
    selected_type.set("Fungi")
    type_dropdown = ttk.OptionMenu(
        root, selected_type, "Fungi", "Fungi", "Bacteria", "Archaea", "Eukaryota", "All"
    )
    type_dropdown.pack(pady=10)

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

    # Create the status label for the GUI
    status_label = ttk.Label(
        root, text="", font=("Helvetica", 12), background="#dcdad5"
    )
    status_label.pack(pady=10)

    # Create the submit button for the GUI
    submit_button = tk.Button(
        root,
        text="Delete",
        font=("Helvetica", 12),
        command=lambda: start_processing(notebook),
        background="red",
        fg="white",
    )
    submit_button.pack()
