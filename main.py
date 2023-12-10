import os
import sys

parent_dir = os.path.dirname(os.getcwd())
sys.path.append(parent_dir)

from tkinter.messagebox import showerror, showwarning
import requests as req
from set_config import get_config

def is_internet_available():
    try:
        response = req.get("https://www.google.com", timeout=5)
        response.raise_for_status()
        return True
    except req.RequestException:
        pass
    return False

def menu():
    import tkinter as tk
    from tkinter import ttk

    from pages.upload_samples import upload_samples_gui
    from pages.documentation import documentation_gui
    from pages.delete_samples import delete_samples_gui
    from pages.delete_all_data import delete_all_data_gui
    from pages.get_all_data import get_all_data_gui
    from pages.get_kit import get_kit_gui
    from pages.update_credentials import update_credentials_gui
    
    # Create the menu window
    root = tk.Tk()
    root.title("Kit Data Merger")
    icon = tk.PhotoImage(file="./static/icons/plant.ico")
    root.iconphoto(False, icon)

    # Set the window side to full screen
    root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}")

    root.state('zoomed')

    # Create a style
    style = ttk.Style()
    style.theme_use("clam")

    # Create a label
    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)

    # Create frams for each tab (button) in the sidebar
    documentation_frame = ttk.Frame(notebook, width=200, height=400)
    upload_frame = ttk.Frame(notebook, width=200, height=400)
    delete_kit_frame = ttk.Frame(notebook, width=200, height=400)
    delete_data_frame = ttk.Frame(notebook, width=200, height=400)
    get_data_frame = ttk.Frame(notebook, width=200, height=400)
    get_kit_frame = ttk.Frame(notebook, width=200, height=400)
    update_credentials_frame = ttk.Frame(notebook, width=200, height=400)

    # Add frames to the notebook
    notebook.add(documentation_frame, text="Documentation")
    notebook.add(upload_frame, text="Upload Samples")
    notebook.add(delete_kit_frame, text="Delete Kit")
    notebook.add(delete_data_frame, text="Delete All Data")
    notebook.add(get_data_frame, text="Get all the data")
    notebook.add(get_kit_frame, text="Get Kit")
    notebook.add(update_credentials_frame, text="Update Credentials")

    documentation_gui(documentation_frame)
    upload_samples_gui(upload_frame, notebook)
    delete_samples_gui(delete_kit_frame, notebook)
    delete_all_data_gui(delete_data_frame, notebook)
    get_all_data_gui(get_data_frame, notebook)
    get_kit_gui(get_kit_frame, notebook)
    update_credentials_gui(update_credentials_frame, notebook)

    root.mainloop()

if __name__ == "__main__":
    response = None
    while not os.path.exists(".env"):
        showerror("No credentials found", "It seems that you are running this program for the first time, So the program couldn't find any credentials. please answer on the question the will appear after you will click 'ok'.")
        response = get_config()

    while not is_internet_available():
        showwarning("Connection error", "The program is requiring internet connection. It seems that you are not connected to the internet, please check your connection and click ok")

    if response is None:
        menu()