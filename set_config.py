import tkinter as tk
from tkinter import ttk
import threading

IMS_API_KEY_entry = None
GOOGLE_TYPE_entry = None
GOOGLE_PROJECT_ID_entry = None
GOOGLE_PRIVATE_KEY_ID_entry = None
GOOGLE_PRIVATE_KEY_entry = None
GOOGLE_CLIENT_EMAIL_entry = None
GOOGLE_CLIENT_ID_entry = None
GOOGLE_AUTH_URI_entry = None
GOOGLE_TOKEN_URI_entry = None
GOOGLE_AUTH_PROVIDER_X509_CERT_URL_entry = None
GOOGLE_CLIENT_X509_CERT_URL_entry = None
GOOGLE_UNIVERSE_DOMAIN_entry = None
root = None
submit_btn = None


def registering_credentials():
    """
    The function gets the valuse from the form, and if they are not empty, it writes the credentials into a .env file
    """
    # If one of the form's fields is empty, stop the function
    if (
        IMS_API_KEY_entry.get() == ""
        or GOOGLE_TYPE_entry.get() == ""
        or GOOGLE_PROJECT_ID_entry.get() == ""
        or GOOGLE_PRIVATE_KEY_ID_entry.get() == ""
        or GOOGLE_PRIVATE_KEY_entry.get() == ""
        or GOOGLE_CLIENT_EMAIL_entry.get() == ""
        or GOOGLE_CLIENT_ID_entry.get() == ""
        or GOOGLE_AUTH_URI_entry.get() == ""
        or GOOGLE_TOKEN_URI_entry.get() == ""
        or GOOGLE_AUTH_PROVIDER_X509_CERT_URL_entry.get() == ""
        or GOOGLE_CLIENT_X509_CERT_URL_entry.get() == ""
        or GOOGLE_UNIVERSE_DOMAIN_entry.get() == ""
    ):
        return

    # Disable all the fields and buttons to prevent user interaction
    submit_btn.config(state="disabled")
    GOOGLE_TYPE_entry.config(state="disabled")
    GOOGLE_PROJECT_ID_entry.config(state="disabled")
    GOOGLE_PRIVATE_KEY_ID_entry.config(state="disabled")
    GOOGLE_PRIVATE_KEY_entry.config(state="disabled")
    GOOGLE_CLIENT_EMAIL_entry.config(state="disabled")
    GOOGLE_CLIENT_ID_entry.config(state="disabled")
    GOOGLE_AUTH_URI_entry.config(state="disabled")
    GOOGLE_TOKEN_URI_entry.config(state="disabled")
    GOOGLE_AUTH_PROVIDER_X509_CERT_URL_entry.config(state="disabled")
    GOOGLE_CLIENT_X509_CERT_URL_entry.config(state="disabled")
    GOOGLE_UNIVERSE_DOMAIN_entry.config(state="disabled")

    # Write all the credentials in a .env file
    with open(".env", "w") as envFile:
        envFile.write(
            f"""# IMS
API_KEY="{IMS_API_KEY_entry.get()}"

# GOOGLE
type="{GOOGLE_TYPE_entry.get()}"
project_id="{GOOGLE_PROJECT_ID_entry.get()}"
private_key_id="{GOOGLE_PRIVATE_KEY_ID_entry.get()}"
private_key="{GOOGLE_PRIVATE_KEY_entry.get()}"
client_email="{GOOGLE_CLIENT_EMAIL_entry.get()}"
client_id="{GOOGLE_CLIENT_ID_entry.get()}"
auth_uri="{GOOGLE_AUTH_URI_entry.get()}"
token_uri="{GOOGLE_TOKEN_URI_entry.get()}"
auth_provider_x509_cert_url="{GOOGLE_AUTH_PROVIDER_X509_CERT_URL_entry.get()}"
client_x509_cert_url="{GOOGLE_CLIENT_X509_CERT_URL_entry.get()}"
universe_domain="{GOOGLE_UNIVERSE_DOMAIN_entry.get()}"
"""
        )

    # Re-enable back all the fields and buttons
    submit_btn.config(state="enabled")
    GOOGLE_TYPE_entry.config(state="enabled")
    GOOGLE_PROJECT_ID_entry.config(state="enabled")
    GOOGLE_PRIVATE_KEY_ID_entry.config(state="enabled")
    GOOGLE_PRIVATE_KEY_entry.config(state="enabled")
    GOOGLE_CLIENT_EMAIL_entry.config(state="enabled")
    GOOGLE_CLIENT_ID_entry.config(state="enabled")
    GOOGLE_AUTH_URI_entry.config(state="enabled")
    GOOGLE_TOKEN_URI_entry.config(state="enabled")
    GOOGLE_AUTH_PROVIDER_X509_CERT_URL_entry.config(state="enabled")
    GOOGLE_CLIENT_X509_CERT_URL_entry.config(state="enabled")
    GOOGLE_UNIVERSE_DOMAIN_entry.config(state="enabled")

    # Quit from the window
    root.destroy()
    root.quit()


def on_close():
    """
    If the credentials form closed, it will destroy the window.
    """
    root.destroy()
    root.quit()


def get_config():
    """
    Credentials form GUI
    """
    global root, submit_btn, IMS_API_KEY_entry, GOOGLE_TYPE_entry, GOOGLE_PROJECT_ID_entry, GOOGLE_PRIVATE_KEY_ID_entry, GOOGLE_PRIVATE_KEY_entry, GOOGLE_CLIENT_EMAIL_entry, GOOGLE_CLIENT_ID_entry, GOOGLE_AUTH_URI_entry, GOOGLE_TOKEN_URI_entry, GOOGLE_AUTH_PROVIDER_X509_CERT_URL_entry, GOOGLE_CLIENT_X509_CERT_URL_entry, GOOGLE_UNIVERSE_DOMAIN_entry

    root = tk.Tk()

    root.protocol("WM_DELETE_WINDOW", on_close)

    root.resizable(False, False)

    heading = ttk.Label(root, text="Credentials Update", font=("Helvetica", 16, "bold"))
    heading.grid(row=0, column=0, columnspan=2, pady=10)

    IMS_heading = ttk.Label(root, text="IMS", font=("Helvetica", 14, "bold"))
    IMS_heading.grid(row=1, column=0, sticky="W")

    IMS_API_KEY_label = ttk.Label(root, text="API KEY", font=("Helvetica", 12))
    IMS_API_KEY_label.grid(row=2, column=0, sticky="W")

    IMS_API_KEY_entry = ttk.Entry(root)
    IMS_API_KEY_entry.grid(row=2, column=1, pady=5)

    GOOGLE_heading = ttk.Label(root, text="GOOGLE", font=("Helvetica", 14, "bold"))
    GOOGLE_heading.grid(row=3, column=0, sticky="W")

    GOOGLE_TYPE_label = ttk.Label(root, text="type", font=("Helvetica", 12))
    GOOGLE_TYPE_label.grid(row=4, column=0, sticky="W")

    GOOGLE_TYPE_entry = ttk.Entry(root)
    GOOGLE_TYPE_entry.grid(row=4, column=1)

    GOOGLE_PROJECT_ID_label = ttk.Label(root, text="project id", font=("Helvetica", 12))
    GOOGLE_PROJECT_ID_label.grid(row=5, column=0, sticky="W")

    GOOGLE_PROJECT_ID_entry = ttk.Entry(root)
    GOOGLE_PROJECT_ID_entry.grid(row=5, column=1)

    GOOGLE_PRIVATE_KEY_ID_label = ttk.Label(
        root, text="private key id", font=("Helvetica", 12)
    )
    GOOGLE_PRIVATE_KEY_ID_label.grid(row=6, column=0, sticky="W")

    GOOGLE_PRIVATE_KEY_ID_entry = ttk.Entry(root)
    GOOGLE_PRIVATE_KEY_ID_entry.grid(row=6, column=1)

    GOOGLE_PRIVATE_KEY_label = ttk.Label(
        root, text="private key", font=("Helvetica", 12)
    )
    GOOGLE_PRIVATE_KEY_label.grid(row=7, column=0, sticky="W")

    GOOGLE_PRIVATE_KEY_entry = ttk.Entry(root)
    GOOGLE_PRIVATE_KEY_entry.grid(row=7, column=1)

    GOOGLE_CLIENT_EMAIL_label = ttk.Label(
        root, text="client email", font=("Helvetica", 12)
    )
    GOOGLE_CLIENT_EMAIL_label.grid(row=8, column=0, sticky="W")

    GOOGLE_CLIENT_EMAIL_entry = ttk.Entry(root)
    GOOGLE_CLIENT_EMAIL_entry.grid(row=8, column=1)

    GOOGLE_CLIENT_ID_label = ttk.Label(root, text="client id", font=("Helvetica", 12))
    GOOGLE_CLIENT_ID_label.grid(row=9, column=0, sticky="W")

    GOOGLE_CLIENT_ID_entry = ttk.Entry(root)
    GOOGLE_CLIENT_ID_entry.grid(row=9, column=1)

    GOOGLE_AUTH_URI_label = ttk.Label(root, text="auth URI", font=("Helvetica", 12))
    GOOGLE_AUTH_URI_label.grid(row=10, column=0, sticky="W")

    GOOGLE_AUTH_URI_entry = ttk.Entry(root)
    GOOGLE_AUTH_URI_entry.grid(row=10, column=1)

    GOOGLE_TOKEN_URI_label = ttk.Label(root, text="token URI", font=("Helvetica", 12))
    GOOGLE_TOKEN_URI_label.grid(row=11, column=0, sticky="W")

    GOOGLE_TOKEN_URI_entry = ttk.Entry(root)
    GOOGLE_TOKEN_URI_entry.grid(row=11, column=1)

    GOOGLE_AUTH_PROVIDER_X509_CERT_URL_label = ttk.Label(
        root, text="auth provider x509 cert URL", font=("Helvetica", 12)
    )
    GOOGLE_AUTH_PROVIDER_X509_CERT_URL_label.grid(row=12, column=0, sticky="W")

    GOOGLE_AUTH_PROVIDER_X509_CERT_URL_entry = ttk.Entry(root)
    GOOGLE_AUTH_PROVIDER_X509_CERT_URL_entry.grid(row=12, column=1)

    GOOGLE_CLIENT_X509_CERT_URL_label = ttk.Label(
        root, text="client x509 cert URL", font=("Helvetica", 12)
    )
    GOOGLE_CLIENT_X509_CERT_URL_label.grid(row=13, column=0, sticky="W")

    GOOGLE_CLIENT_X509_CERT_URL_entry = ttk.Entry(root)
    GOOGLE_CLIENT_X509_CERT_URL_entry.grid(row=13, column=1)

    GOOGLE_UNIVERSE_DOMAIN_label = ttk.Label(
        root, text="universe domain", font=("Helvetica", 12)
    )
    GOOGLE_UNIVERSE_DOMAIN_label.grid(row=14, column=0, sticky="W")

    GOOGLE_UNIVERSE_DOMAIN_entry = ttk.Entry(root)
    GOOGLE_UNIVERSE_DOMAIN_entry.grid(row=14, column=1)

    submit_btn = ttk.Button(
        root,
        text="Submit",
        command=lambda: threading.Thread(target=registering_credentials).start(),
    )
    submit_btn.grid(row=15, column=0, columnspan=2, pady=5)

    root.mainloop()
