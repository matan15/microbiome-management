import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askdirectory
from tkinter.messagebox import showinfo, showerror

import threading

from elasticsearch import Elasticsearch

import dotenv
import os

import csv

import logging

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

    with open(os.path.join(dir_path, "kibana_data.csv"), newline="", mode='a+') as csvfile:
        csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        csv_writer.writeheader()
        csv_writer.writerows(data)

def get_data(notebook):
    """
    Retrieves data from Elasticsearch and saves it to a CSV file.

    Overview:
    1. Retrieves the selected directory from a Tkinter entry widget.
    2. If the directory is not provided, returns without performing any action.
    3. Disables certain Tkinter widgets to prevent multiple data retrieval requests.
    4. Loads environment variables from a .env file using python-dotenv.
    5. Establishes a connection to Elasticsearch using specified cloud ID, username, and password.
    6. Sends a search query to Elasticsearch to retrieve data for all records in the "fungi" index.
    7. Displays an error message if no records are found, and re-enables disabled Tkinter widgets.
    8. Retrieves data from search results and updates a progress bar accordingly.
    9. Continues scrolling through Elasticsearch results until all records are retrieved.
    10. Clears the scroll ID to release resources on the Elasticsearch server.
    11. Writes the retrieved data to a CSV file in the selected directory.
    12. Updates the status label to indicate successful data retrieval and file saving.
    13. Displays an information message indicating the successful file save.
    14. Logs the success message.
    15. Re-enables Tkinter widgets for future operations.

    Note: This code assumes the existence of Tkinter widgets (e.g., location_entry, select_dir_button, submit_button, etc.)
    and proper setup of Elasticsearch connection parameters.

    :return: None
    """
    # Step 1: Retrieve selected directory
    selected_dir = location_entry.get()
    
    # Step 2: If the directory is not provided, return without performing any action
    if not selected_dir:
        return

    # Step 3: Disable certain Tkinter widgets
    notebook.config([0, 1, 2, 3, 4, 5, 6], state=tk.DISABLED)
    location_entry.config(state=tk.DISABLED)
    select_dir_button.config(state=tk.DISABLED)
    submit_button.config(state=tk.DISABLED)

    # Step 4: Load environment variables from a .env file using python-dotenv
    dotenv.load_dotenv(dotenv.find_dotenv())

    status_label.config(text="Getting data...")

    # Step 5: Establish connection to Elasticsearch
    es = Elasticsearch(
        cloud_id=os.environ.get("cloud_id"),
        http_auth=(os.environ.get("user"), os.environ.get("password"))
    )

    # Step 6: Send search query to Elasticsearch
    res = es.search(index="microbiome", body={
        "size": 1000,
        "query": {
            "match_all": {}
        }
    }, scroll='1m')
    
    # Step 7: Display error if no records found, re-enable disabled Tkinter widgets
    if res['hits']['total']['value'] == 0:
        showerror("No records found", "There are no records found.")
        status_label.config(text="")
        logging.info("No records found in Elasticsearch.")
        location_entry.config(state=tk.NORMAL)
        select_dir_button.config(state=tk.NORMAL)
        submit_button.config(state=tk.NORMAL)
        return

    # Step 8: Retrieve data from search results and update progress bar
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
        percentage_label.config(text=(('%.2f' % progress) + "%"))
    
    # Step 9: Continue scrolling through Elasticsearch results until all records are retrieved
    while hits:
        res = es.scroll(scroll_id=scroll_id, scroll="1m")
        hits = res['hits']['hits']

        for hit in hits:
            data.append(hit['_source'])
            progress_counter += 1
            progress = (progress_counter / total_records) * 100
            progress_var.set(progress)
            percentage_label.config(text=(('%.2f' % progress) + "%"))
    
    # Step 10: Clear the scroll ID to release resources on the Elasticsearch server
    es.clear_scroll(scroll_id=scroll_id)

    # Step 11: Write the retrieved data to a CSV file in the selected directory
    write_dicts_to_csv(selected_dir, data)

    # Step 12: Update status label to indicate successful data retrieval and file saving
    status_label.config(text="The file was saved successfully.")

    # Step 13: Display information message indicating successful file save
    showinfo("The file saved successfully", f"The file was saved successfully in {selected_dir}")
    
    # Step 14: Log success message
    logging.info(f"The file was saved successfully in {selected_dir}")

    # Step 15: Re-enable Tkinter widgets for future operations
    notebook.config([0, 1, 2, 3, 4, 5, 6], state=tk.NORMAL)
    location_entry.config(state=tk.NORMAL)
    select_dir_button.config(state=tk.NORMAL)
    submit_button.config(state=tk.NORMAL)

def select_dir():
    # Ask for a directory and pasting the path in the field
    dir_path = askdirectory()
    location_entry.delete(0, tk.END)
    location_entry.insert(0, dir_path)

def start_processing(notebook):
    """
    Initiates a separate thread to start the data retrieval process using the get_data function.

    Overview:
    1. Creates a new thread, targeting the get_data function, to perform data retrieval in the background.
    2. Starts the created thread to execute the get_data function concurrently.
    3. Allows the main thread to continue its operation without waiting for the retrieval process to complete.

    Note: The use of threading allows for non-blocking execution, ensuring the responsiveness of the user interface
    during time-consuming operations like data retrieval from Elasticsearch.

    :return: None
    """
    threading.Thread(target=lambda: get_data(notebook)).start()

def get_all_data_gui(root, notebook):
    global location_entry, select_dir_button, submit_button, progress_var, percentage_label, status_label
    title_label = ttk.Label(root, text='Get All Samples', font=('Helvetica', 16, 'bold'), background="#dcdad5")
    title_label.pack(pady=10)

    location_label = ttk.Label(root, text="Select a folder where you want to save samples:", font=('Helvetica', 12), background="#dcdad5")
    location_label.pack(pady=10)

    location_entry = ttk.Entry(root, width=40, font=('Helvetica', 12))
    location_entry.pack(pady=10)

    select_dir_button = tk.Button(root, text='Browse', command=select_dir, background='#007acc', fg='white',
                              font=('Helvetica', 12))
    select_dir_button.pack(pady=10)

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