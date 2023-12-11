import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror, showinfo

import dotenv
import os

import threading

import logging

dotenv.load_dotenv(dotenv.find_dotenv())

cloud_id_entry = None
user_entry = None
password_entry = None
api_key_entry = None

def update_credentials(notebook):
    """
    Update Elasticsearch and IMS API credentials in the .env file based on the user input.

    This function is triggered by the 'Submit' button. It validates the provided values for Cloud ID, user name,
    password, and API_KEY. If all values are valid, it updates the .env file with the entered credentials.

    Returns:
        None
    """
    for i in range(0, 7):
        if i == 6:
            continue
        notebook.tab(i, state=tk.DISABLED)
    if not cloud_id_entry.get() or not user_entry.get() or not password_entry.get() or not api_key_entry.get():
        showerror("Error in credentials", "One or more values are not valid.")
        logging.error("Error in credentials: One or more values are not valid.")
        return

    with open(".env", 'w') as envfile:
        envfile.write(f"""
# ELASTICSEARCH
cloud_id={cloud_id_entry.get()}
user={user_entry.get()}
password={password_entry.get()}

#IMS
API_KEY={api_key_entry.get()}
""")
    showinfo("Credentials updated", "The credentials has been updated successfully.")
    logging.info("The credentials has been updated successfully.")
    for i in range(0, 7):
        if i == 6:
            continue
        notebook.tab(i, state=tk.NORMAL)


def start_processing(notebook):
    """
    Start a new thread to update credentials asynchronously.

    This function is triggered by the 'Submit' button. It creates a new thread to execute the 'update_credentials'
    function asynchronously.

    Returns:
        None
    """
    threading.Thread(target=lambda: update_credentials(notebook)).start()

def update_credentials_gui(root, notebook):
    """
    Create a GUI window for updating Elasticsearch and IMS API credentials.

    This function initializes a Tkinter window with entry fields for Cloud ID, user name, password, and API_KEY.
    It also provides a 'Submit' button to trigger the credential update process.

    Args:
        root (tk.Tk): The Tkinter root window.

    Returns:
        None
    """
    global cloud_id_entry, user_entry, password_entry, api_key_entry
    title_label = ttk.Label(root, text='Update Credentials', font=('Helvetica', 16, 'bold'), background="#dcdad5")
    title_label.pack(pady=10)

    cloud_id_label = ttk.Label(root, text="Enter the Cloud ID:", font=('Helvetica', 12), background="#dcdad5")
    cloud_id_label.pack(pady=10)

    cloud_id_entry = ttk.Entry(root, width=40, font=('Helvetica', 12))
    cloud_id_entry.insert(0, os.environ.get("cloud_id") if "cloud_id" in os.environ.keys() else '')
    cloud_id_entry.pack(pady=10)

    user_label = ttk.Label(root, text="Enter the user name:", font=('Helvetica', 12), background="#dcdad5")
    user_label.pack(pady=10)

    user_entry = ttk.Entry(root, width=40, font=('Helvetica', 12))
    user_entry.insert(0, os.environ.get("user") if "user" in os.environ.keys() else '')
    user_entry.pack(pady=10)

    password_label = ttk.Label(root, text="Enter the password:", font=('Helvetica', 12), background="#dcdad5")
    password_label.pack(pady=10)

    password_entry = ttk.Entry(root, width=40, font=('Helvetica', 12))
    password_entry.insert(0, os.environ.get("password") if "password" in os.environ.keys() else '')
    password_entry.pack(pady=10)

    api_key_label = ttk.Label(root, text="Enter the Cloud ID:", font=('Helvetica', 12), background="#dcdad5")
    api_key_label.pack(pady=10)

    api_key_entry = ttk.Entry(root, width=40, font=('Helvetica', 12))
    api_key_entry.insert(0, os.environ.get("API_KEY") if "API_KEY" in os.environ.keys() else '')
    api_key_entry.pack(pady=10)

    submit_button = tk.Button(root, text='Submit', command=lambda: start_processing(notebook), background='#4CAF50', fg='white',
                              font=('Helvetica', 12))
    submit_button.pack(pady=10)