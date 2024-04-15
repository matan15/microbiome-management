from tkhtmlview import HTMLLabel
import markdown
import tempfile
import os
import customtkinter as ctk

def documentation_gui(root):
    """
    This function creates a GUI for displaying documentation. The GUI consists of a title label and HTML frame.

    Args:
        root (tkinter.Tk): The root window of the GUI.

    Returns:
        None

    """
    title_label = ctk.CTkLabel(
        root, text="Documentation", font=("Helvetica", 16, "bold")
    )
    title_label.pack(pady=10)
    # Read the contents of the README.md file
    with open("README.md", "r") as f:
        content = f.read()

    # Convert the Markdown content to HTML
    m_html = markdown.markdown(content).replace(
        "/static/images/screenshot.png", f"{os.getcwd()}/static/images/screenshot.png"
    )

    # Create a temporary file to store the HTML
    temp_fd, temp_html_path = tempfile.mkstemp(suffix=".html", text=True)
    with os.fdopen(temp_fd, "w") as f:
        f.write(m_html)

    # Create an HTML label to display the documentation
    html_label = HTMLLabel(root, html="<h1>Documentation</h1>", background="#dcdad5")
    html_label.pack(fill="both", expand=True)

    # Load the HTML into the HTML label
    with open(temp_html_path, "r") as html_file:
        html_label.set_html(html_file.read())
