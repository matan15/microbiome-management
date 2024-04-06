import os
import sys

import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk

# set the project directory as a main work directory
parent_dir = os.path.dirname(os.getcwd())
sys.path.append(parent_dir)

from tkinter.messagebox import showerror, showwarning
import requests as req
from set_config import get_config


def is_internet_available():
    """
    The function checks if the user connected to the Internet. The program is requiring connection to the Internet.
    """
    try:
        response = req.get("https://www.google.com", timeout=5)
        response.raise_for_status()
        return True
    except req.RequestException:
        pass
    return False


def loading_screen():
    """
    Loading GUI while checking if the user is connected to the Internet and the program has the needed credentials.
    """
    root = tk.Tk()

    image = ImageTk.PhotoImage(
        Image.open("static//icons//plant.ico").resize((256, 256), Image.LANCZOS)
    )

    height, width = 430, 600
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry("{}x{}+{}+{}".format(width, height, x, y))
    root.overrideredirect(True)

    root.config(background="#2F6C60")

    root.resizable(False, False)

    heading = tk.Label(
        root,
        text="Microbiome Management",
        bg="#2F6C60",
        font=("Trebuchet Ms", 15, "bold"),
        fg="#FFFFFF",
    )
    heading.place(x=180, y=25)

    bg_image = tk.Label(root, image=image, bg="#2F6C60")
    bg_image.place(x=180, y=65)

    progress_label = tk.Label(
        root,
        text="Loading...",
        font=("Trebuchet Ms", 13, "bold"),
        fg="#FFFFFF",
        bg="#2F6C60",
    )
    progress_label.place(x=110, y=340)

    progress = ttk.Style()
    progress.theme_use("clam")
    progress.configure("red.Horizontal.TProgressbar", background="#108cff")

    progress = ttk.Progressbar(
        root,
        orient=tk.HORIZONTAL,
        length=400,
        mode="determinate",
        style="red.Horizontal.TProgressbar",
    )
    progress.place(x=110, y=370)

    counter = 0

    def top():
        root.withdraw()
        root.destroy()

    def load():
        nonlocal counter
        steps = [
            "Checking credentials",
            "Checking credentials",
            "Checking Internet connection",
        ]
        total = 2
        if counter <= total:
            txt = (
                "Loading... %.2f" % ((counter / total) * 100) + "%"
            ) + f" ({steps[counter]})"
            progress_label.configure(text=txt)
            if counter == 0:
                # Check if there are credentials, if there are no credentials, show an error and open credentials form.
                if not os.path.exists(".env"):
                    showerror(
                        "No credentials found",
                        "It seems that you are running this program for the first time, So the program couldn't find any credentials. please answer on the question the will appear after you will click 'ok'.",
                    )
                    get_config()
            elif counter == 1:
                # If there was an error or the user didn't fill the credentials form, display an error to the user and quit the program.
                if not os.path.exists(".env"):
                    showerror(
                        "No credentials found",
                        "No credentials found, The program can't work without credentials. Please close this window, run again the program and fill the credentials.",
                    )
                    root.withdraw()
                    root.destroy()
                    sys.exit()
            elif counter == 2:
                # If the user is not connected to the internet, display an error message to the user until the user will connect to the internet.
                while not is_internet_available():
                    showwarning(
                        "Connection error",
                        "The program is requiring internet connection. It seems that you are not connected to the internet, please check your connection and click ok",
                    )
            progress["value"] = (counter / total) * 100
            counter += 1
            root.after(1000, load)
        else:
            top()

    load()

    root.mainloop()


def menu():
    """
    The function Initializing the main screen of the program with notebook (tabs to navigate between actions).
    """
    from pages.upload_samples import upload_samples_gui
    from pages.documentation import documentation_gui
    from pages.delete_samples import delete_samples_gui
    from pages.delete_all_data import delete_all_data_gui
    from pages.get_all_data import get_all_data_gui
    from pages.get_kit import get_kit_gui
    from pages.update_credentials import update_credentials_gui

    root = tk.Tk()
    root.title("Microbiome Management")
    icon = tk.PhotoImage(file="./static/icons/plant.ico")
    root.iconphoto(False, icon)

    root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}")

    root.state("zoomed")

    style = ttk.Style()
    style.theme_use("clam")

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)

    documentation_frame = ttk.Frame(notebook, width=200, height=400)
    upload_frame = ttk.Frame(notebook, width=200, height=400)
    delete_kit_frame = ttk.Frame(notebook, width=200, height=400)
    delete_data_frame = ttk.Frame(notebook, width=200, height=400)
    get_data_frame = ttk.Frame(notebook, width=200, height=400)
    get_kit_frame = ttk.Frame(notebook, width=200, height=400)
    update_credentials_frame = ttk.Frame(notebook, width=200, height=400)

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
    loading_screen()
    menu()
