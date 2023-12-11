from elasticsearch import Elasticsearch
import dotenv
import os
from tkinter import ttk
import tkinter as tk
import threading
from tkinter.messagebox import showerror, showinfo, askyesno

import logging

dotenv.load_dotenv(dotenv.find_dotenv())

kit_number_entry = None
submit_button = None
status_label = None
selected_type = None

def delete_samples(notebook):
    """
    Deletes all records in Elasticsearch associated with a specified kit ID and optional kingdom type.

    This function performs the following steps:
    1. Attempts to convert the kit number from the kit_number_entry to an integer; displays an error if not a valid number.
    2. If the kit number is not provided or not a valid number, the function returns without performing any action.
    3. Asks for user confirmation before proceeding with the deletion operation.
    4. If the user chooses not to proceed, the function returns without performing any action.
    5. Establishes a connection to Elasticsearch using specified cloud ID, username, and password.
    6. Disables certain Tkinter widgets to prevent multiple deletion requests.
    7. Displays a "Deleting..." message in the status label.
    8. Constructs the body of the delete_by_query request based on the specified kit ID and optional kingdom type.
    9. Executes the delete_by_query operation on the "fungi" index in Elasticsearch.
    10. Updates the status label to indicate successful deletion.
    11. Displays an information message indicating the successful deletion of the specified kit.
    12. Logs the deletion operation as a success.
    13. Re-enables the Tkinter widgets for future operations.

    :return: None
    """
    # Step 1: Attempt to convert the kit number to an integer; display an error if not a valid number
    try:
        selected_kit = int(kit_number_entry.get())
    except ValueError:
        showerror("Not Valid Kit ID", "You have been entered a kit id that is not a number. please enter a valid kit id.")
        logging.error(f"Not Valid Kit ID ({kit_number_entry.get()}). You have been entered a kit id that is not a number. please enter a valid kit id.")
        return 
    
    # Step 2: If the kit number is not provided or not a valid number, return without performing any action
    if not selected_kit:
        return

    # Step 3: Ask for user confirmation before proceeding with the deletion operation
    if not askyesno("Confirm delete", f"Are you sure you want to delete All the {selected_type.get() if selected_type.get() != 'All' else ''} records in the kit {selected_kit}"): return

    # Step 4: Establish connection to Elasticsearch
    es = Elasticsearch(
        cloud_id=os.environ.get("cloud_id"),
        http_auth=(os.environ.get("user"), os.environ.get("password"))
    )

    # Step 5: Disable certain Tkinter widgets
    for i in range(0, 7):
        if i == 2:
            continue
        notebook.tab(i, state=tk.DISABLED)
    kit_number_entry.config(state=tk.DISABLED)
    submit_button.config(state=tk.DISABLED)

    # Step 6: Update status label
    status_label.config(text="Deleting...")

    # Step 7: Construct the body of the delete_by_query request
    body_request = {
        "query": {
            "match": {
                'Kit ID': selected_kit
            }
        }
    }

    # Step 8: Add optional kingdom type to the delete_by_query request
    if selected_type != "All":
        body_request["Kingdom"] = selected_type

    # Step 9: Execute delete_by_query operation on the index in Elasticsearch
    es.delete_by_query(index='microbiome', body=body_request)
    
    # Step 10: Update status label and display success message
    status_label.config(text="The Kit has been deleted")
    showinfo("The kit has been deleted", "The kit has been deleted successfully.")
    
    # Step 11: Log deletion operation as a success
    logging.info(f"The kit {selected_kit} has been deleted successfully.")

    # Step 12: Re-enable Tkinter widgets for future operations
    kit_number_entry.config(state=tk.NORMAL)
    submit_button.config(state=tk.NORMAL)
    for i in range(0, 7):
        if i == 2:
            continue
        notebook.tab(i, state=tk.NORMAL)


def start_processing(notebook):
    """
    Initiates a separate thread to start the sample deletion process using the delete_samples function.

    This function performs the following steps:
    1. Creates a new thread, targeting the delete_samples function, to perform sample deletion in the background.
    2. Starts the created thread to execute the delete_samples function concurrently.
    3. Allows the main thread to continue its operation without waiting for the deletion process to complete.

    Note: The use of threading allows for non-blocking execution, ensuring the responsiveness of the user interface
    during time-consuming operations like sample deletion.

    :return: None
    """
    threading.Thread(target=lambda: delete_samples(notebook)).start()

def delete_samples_gui(root, notebook):
    global kit_number_entry, submit_button, status_label, selected_type
    title_label = ttk.Label(root, text='Delete Kit', font=('Helvetica', 16, 'bold'), background="#dcdad5")
    title_label.pack(pady=10)

    selected_type = tk.StringVar()
    selected_type.set("Fungi")
    type_dropdown = ttk.OptionMenu(root, selected_type, "Fungi", "Fungi", "Bacteria", "All")
    type_dropdown.pack(pady=10)

    kit_label = ttk.Label(root, text="Enter the Kit ID:", font=('Helvetica', 12), background="#dcdad5")
    kit_label.pack(pady=10)

    kit_number_entry = ttk.Entry(root, width=40, font=('Helvetica', 12))
    kit_number_entry.pack(pady=10)

    status_label = ttk.Label(root, text='', font=('Helvetica', 12), background="#dcdad5")
    status_label.pack(pady=10)

    submit_button = tk.Button(root, text='Delete', font=('Helvetica', 12), command=lambda: start_processing(notebook), background='red', fg='white')
    submit_button.pack()