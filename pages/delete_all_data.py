import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo, askyesno

from elasticsearch import Elasticsearch

import dotenv
import os

import threading

import logging

dotenv.load_dotenv(dotenv.find_dotenv())

submit_button = None
status_label = None

def delete_data(notebook):
    """
    Deletes all data from Elasticsearch index.

    This function performs the following steps:
    1. Asks the user for confirmation before proceeding with the deletion operation.
    2. If the user chooses not to proceed, the function returns without performing any action.
    3. Disables the submit button to prevent multiple deletion requests.
    4. Displays a "deleting..." message in the status label.
    5. Establishes a connection to Elasticsearch using specified cloud ID, username, and password.
    6. Deletes all data from the index using the delete_by_query method.
    7. Updates the status label to indicate successful deletion.
    8. Displays an information message indicating the successful deletion.
    9. Logs the deletion operation as a success.
    10. Re-enables the submit button for future operations.

    :return: None
    """
    # Step 1: Ask for user confirmation
    if not askyesno("Are you sure?", "Are you sure you want to delete all the data? Note that there is no way to cancel this operation."):
        return 

    # Step 2: Disable submit button
    for i in range(0, 7):
        notebook.tab(i, state=tk.DISABLED)
    submit_button.config(state=tk.DISABLED)

    # Step 3: Update status label
    status_label.config(text="deleting...")

    # Step 4: Establish connection to Elasticsearch
    es = Elasticsearch(
        cloud_id=os.environ.get("cloud_id"),
        http_auth=(os.environ.get("user"), os.environ.get("password"))
    )

    # Step 5: Delete all data from the index
    es.delete_by_query(index="microbiome", body={
        "query": {
            "match_all": {}
        }
    })

    # Step 6: Update status label and display success message
    status_label.config(text="The data has been deleted successfully.")
    showinfo("The data has been deleted", "The data has been deleted successfully.")
    
    # Step 7: Log deletion operation as a success
    logging.info("The data has been deleted successfully.")

    # Step 8: Re-enable submit button
    submit_button.config(state=tk.NORMAL)
    for i in range(0, 7):
        if i == 3:
            continue
        notebook.tab(i, state=tk.NORMAL)


def start_processing(notebook):
    """
    Initiates a separate thread to start the data deletion process using the delete_data function.

    This function performs the following steps:
    1. Creates a new thread, targeting the delete_data function, to perform data deletion in the background.
    2. Starts the created thread to execute the delete_data function concurrently.
    3. Allows the main thread to continue its operation without waiting for the deletion process to complete.

    Note: The use of threading allows for non-blocking execution, ensuring the responsiveness of the user interface
    during time-consuming operations like data deletion.

    :return: None
    """
    threading.Thread(target=lambda: delete_data(notebook)).start()

def delete_all_data_gui(root, notebook):
    """
    This function creates a GUI for deleting all the data from an Elasticsearch index.

    Args:
        root (tkinter.Tk): The root window of the GUI.

    Returns:
        None
    """
    global submit_button, status_label

    # Create the title label for the GUI
    title_label = ttk.Label(root, text='Delete All the data', font=('Helvetica', 16, 'bold'), background="#dcdad5")
    title_label.pack(pady=10)

    # Create the warning label for the GUI
    warning_label = ttk.Label(root, text="WARNING: All the data will be deleted", font=('Helvetica', 14, 'bold'), foreground="red", background="#dcdad5")
    warning_label.pack(pady=10)

    # Create the status label for the GUI
    status_label = ttk.Label(root, text='', font=('Helvetica', 12), background="#dcdad5")
    status_label.pack(pady=10)

    # Create the submit button for the GUI
    submit_button = tk.Button(root, text='Delete', font=('Helvetica', 12), command=lambda: start_processing(notebook), background='red', fg='white')
    submit_button.pack()