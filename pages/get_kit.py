import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror, showinfo
from tkinter.filedialog import askdirectory

from elasticsearch import Elasticsearch

import threading

import dotenv
import os

import logging

import csv

def write_dicts_to_csv(dir_path, data):
    fieldnames = data[max(range(len(data)), key=lambda i: len(data[i].keys()))].keys()

    with open(os.path.join(dir_path, "kibana_data.csv"), newline="", mode="a+") as csvfile:
        csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        csv_writer.writeheader()
        csv_writer.writerows(data)

dotenv.load_dotenv(dotenv.find_dotenv())

kit_number_entry = None
status_label = None
progress_var = None
progress_bar = None
submit_button = None
location_entry = None
select_dir_button = None
percently_label = None

def get_kit(notebook):
    """
    Retrieves data from Elasticsearch based on a specified kit ID.

    This function performs the following steps:
    1. Retrieves the selected directory from a Tkinter entry widget.
    2. Attempts to retrieve the kit number from a Tkinter entry widget; if unsuccessful, displays an error message.
    3. Establishes a connection to Elasticsearch using specified cloud ID, username, and password.
    4. Disables certain Tkinter widgets to prevent user interaction during data retrieval.
    5. Sends a search query to Elasticsearch to retrieve data for the specified kit ID.
    6. Displays an error message if no records are found, and re-enables disabled Tkinter widgets.
    7. Retrieves data from search results and updates a progress bar accordingly.
    8. Continues scrolling through Elasticsearch results until all records are retrieved.
    9. Clears the scroll ID to release resources on the Elasticsearch server.
    10. Displays a success message with the selected directory where the file was saved.
    11. Logs the success message.

    :return: None
    """

    # Step 1: Retrieve selected directory
    selected_dir = location_entry.get()

    # Step 2: Retrieve kit number, display error if not a valid number
    try:
        selected_kit = kit_number_entry.get()
    except ValueError:
        showerror("Not Valid Kit ID", "You have been entered a kit id that is not a number. please enter a valid kit id.")
        logging.error(f"Not Valid Kit ID ({kit_number_entry.get()}). You have been entered a kit id that is not a number. please enter a valid kit id.")
        return
    
    if not selected_kit:
        return
    

    # Step 3: Establish connection to Elasticsearch
    es = Elasticsearch(
        cloud_id=os.environ.get("cloud_id"),
        http_auth=(os.environ.get("user"), os.environ.get("password"))
    )

    # Step 4: Disable certain Tkinter widgets
    notebook.config([0, 1, 2, 3, 4, 5, 6], state=tk.DISABLED)
    kit_number_entry.config(state=tk.DISABLED)
    submit_button.config(state=tk.DISABLED)

    # Step 5: Send search query to Elasticsearch
    status_label.config(text="Getting Data...")
    res = es.search(index="microbiome", body={
        "size": 1000,
        "query": {
            "match": {
                "Kit ID": selected_kit
            }
        }
    }, scroll="1m")

    # Step 6: Display error if no records found, re-enable disabled Tkinter widgets
    if res['hits']['total']['value'] == 0:
        showerror("No records found", "There are no records found.")
        status_label.config(text="No records found in Elasticsearch")
        location_entry.config(state=tk.NORMAL)
        select_dir_button.config(state=tk.NORMAL)
        submit_button.config(state=tk.NORMAL)
        return
    
    # Step 7: Retrieve data from search results and update progress bar
    progress_counter = 0
    total_records = res['hits']['total']['value']
    scroll_id = res['_scroll_id']
    hits = res['hits']['hits']
    data = []

    for hit in hits:
        data.append(hit['_source'])
        progress_counter += 1
        progress = (progress_counter / total_records) * 100
        progress_var.set(progress)
        percentage_label.config(text=(('%.2f' % progress) + '%'))

    # Step 8: Continue scrolling through Elasticsearch results until all records are retrieved
    while hits:
        res = es.scroll(scroll_id=scroll_id, scroll="1m")
        hits = res['hits']['hits']

        for hit in hits:
            data.append(hit['_source'])
            progress_counter += 1
            progress = (progress_counter / total_records) * 100
            progress_var.set(progress)
            percentage_label.config(text=(('%.2f' % progress) + '%'))

    # Step 9: Clear the scroll ID to release resources on the Elasticsearch server
    es.clear_scroll(scroll_id=scroll_id)

    # Step 10: Display success message
    showinfo("The file saved successfully", f"The file was saved successfully in {selected_dir}")
    
    # Step 11: Log success message
    logging.info(f"The file was saved successfullt in {selected_dir}")

    # Step 12: Re-enable Tkinter widgets
    notebook.config([0, 1, 2, 3, 4, 5, 6], state=tk.NORMAL)
    location_entry.config(state=tk.NORMAL)
    select_dir_button.config(state=tk.NORMAL)
    submit_button.config(state=tk.NORMAL)
    

def start_processing(notebook):
    """
    Initiates a separate thread to start the kit data retrieval process using the get_kit function.

    Overview:
    1. Creates a new thread, targeting the get_kit function, to perform kit data retrieval in the background.
    2. Starts the created thread to execute the get_kit function concurrently.
    3. Allows the main thread to continue its operation without waiting for the retrieval process to complete.

    Note: The use of threading allows for non-blocking execution, ensuring the responsiveness of the user interface
    during time-consuming operations like kit data retrieval from Elasticsearch.

    :return: None
    """
    threading.Thread(target=lambda: get_kit(notebook)).start()

def select_dir():
    # Ask for a directory and pasting the path in the field
    dir_path = askdirectory()
    location_entry.delete(0, tk.END)
    location_entry.insert(0, dir_path)

def get_kit_gui(root, notebook):
    global kit_number_entry, status_label, progress_var, progress_bar, submit_button, location_entry, select_dir_button, percentage_label
    title_label = ttk.Label(root, text='Get kit', font=('Helvetica', 16, 'bold'), background="#dcdad5")
    title_label.pack(pady=10)

    kit_label = ttk.Label(root, text="Enter the Kit ID:", font=('Helvetica', 12), background="#dcdad5")
    kit_label.pack(pady=10)

    kit_number_entry = ttk.Entry(root, width=40, font=('Helvetica', 12))
    kit_number_entry.pack(pady=10)

    location_label = ttk.Label(root, text="Select a folder where you want to save samples:", font=('Helvetica', 12), background="#dcdad5")
    location_label.pack(pady=10)

    location_entry = ttk.Entry(root, width=40, font=('Helvetica', 12))
    location_entry.pack(pady=10)

    select_dir_button = tk.Button(root, text='Browse', command=select_dir, background='#007acc', fg='white',
                              font=('Helvetica', 12))
    select_dir_button.pack(pady=10)

    status_label = ttk.Label(root, text='', font=('Helvetica', 12), background="#dcdad5")
    status_label.pack(pady=10)

    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(root, length=300, variable=progress_var, mode='determinate')
    progress_bar.pack(pady=10)

    percentage_label = ttk.Label(root, text='0%', font=('Helvetica', 12), background="#dcdad5")
    percentage_label.pack()

    status_label = ttk.Label(root, text='', font=('Helvetica', 12), background="#dcdad5")
    status_label.pack()

    submit_button = tk.Button(root, text='Submit', command=lambda: start_processing(notebook), background='#4CAF50', fg='white',
                              font=('Helvetica', 12))
    submit_button.pack(pady=10)



