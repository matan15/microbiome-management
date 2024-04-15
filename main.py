import os
import sys

import customtkinter as ctk

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
    root = ctk.CTk()
    root.attributes('-topmost', True)

    image = ctk.CTkImage(
        light_image=Image.open("static//icons//plant.ico").resize((256, 256), Image.LANCZOS),
        dark_image=Image.open("static//icons//plant.ico").resize((256, 256), Image.LANCZOS),
        size=(256, 256)
    )

    height, width = 430, 600
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry("{}x{}+{}+{}".format(width, height, x, y))
    root.overrideredirect(True)

    root.configure(fg_color="#2F6C60")

    root.resizable(False, False)

    heading = ctk.CTkLabel(
        root,
        text="Microbiome Management",
        fg_color="#2F6C60",
        font=("Trebuchet Ms", 18, "bold"),
        text_color="#FFFFFF",
        justify="center"
    )
    heading.pack(pady=20)

    bg_image = ctk.CTkLabel(root, text="", image=image, fg_color="#2F6C60", justify="center")
    bg_image.pack(pady=10)

    progress_label = ctk.CTkLabel(
        root,
        text="Loading...",
        font=("Trebuchet Ms", 13, "bold"),
        text_color="#FFFFFF",
        bg_color="#2F6C60",
        justify="center"
    )
    progress_label.pack(pady=10)

    progress = ctk.CTkProgressBar(
        root,
        orientation="horizontal",
        width=300,
        mode="determinate",
    )
    progress.pack()

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
            progress.set(counter / total)
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

    root = ctk.CTk()
    root.title("Microbiome Management")
    ctk.set_appearance_mode("light") 
    root._state_before_windows_set_titlebar_color = "zoomed"

    notebook = ctk.CTkTabview(root)
    notebook.pack(fill="both", expand=True)

    notebook.add("Documentation")
    notebook.add("Upload Samples")
    notebook.add("Delete Kit")
    notebook.add("Delete All Data")
    notebook.add("Get all the data")
    notebook.add("Get Kit")
    notebook.add("Update Credentials")

    documentation_gui(notebook.tab("Documentation"))
    upload_samples_gui(notebook.tab("Upload Samples"), notebook)
    delete_samples_gui(notebook.tab("Delete Kit"), notebook)
    delete_all_data_gui(notebook.tab("Delete All Data"), notebook)
    get_all_data_gui(notebook.tab("Get all the data"), notebook)
    get_kit_gui(notebook.tab("Get Kit"), notebook)
    update_credentials_gui(notebook.tab("Update Credentials"), notebook)

    root.mainloop()


if __name__ == "__main__":
    loading_screen()
    menu()
