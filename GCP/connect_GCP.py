from google.cloud import firestore
from google.oauth2 import service_account

import os

import pandas as pd

from utils import get_google_creds

# Get credentials from the .env file
creds = get_google_creds()

# Create google credentials object
credentials = service_account.Credentials.from_service_account_info(creds)

# Connect to the database
db = firestore.Client(
    project=creds["project_id"], credentials=credentials, database="microbiome"
)


def _parse_cords(raw_cords):
    """
    Parse raw coordinates string into a dictionary with 'lat' and 'lon' keys.

    Parameters:
    - raw_cords: A string containing latitude and longitude separated by a comma.

    Returns:
    A dictionary with 'lat' and 'lon' keys representing parsed coordinates.
    If parsing is unsuccessful or raw_cords is None, returns None.
    """

    if not raw_cords is None:
        try:
            split_cords = raw_cords.split(",")
        except AttributeError:
            return
        return {"lat": float(split_cords[0]), "lon": float(split_cords[1])}
    return None


def _save_docs(progress_var, percentage_label, num_files, index_name):
    """
    Save documents from CSV files to Google Storage index.

    Parameters:
    - progress_var: Tkinter variable for tracking progress.
    - percentage_label: Tkinter label for displaying progress percentage.
    - num_files: Total number of CSV files to process.
    - index_name: Name of the Google Storage index.

    Returns:
    None
    """
    progress_counter = 0
    progress_var.set(0)
    percentage_label.configure(text=(("%.2f " % 0) + "%"))
    for file in os.listdir(f"./kitDataMerger/microbiome-public"):
        # read the csv file
        df = pd.read_csv(
            f"./kitDataMerger/microbiome-public/{file}", encoding="utf-16", sep="\t"
        )
        records = df.to_dict(orient="records")
        for rec in records:
            for key, value in rec.items():
                # Replace all the null, nan, and __ values with None
                if pd.isnull(value) or str(value).lower() == "nan" or value == "__":
                    rec[key] = None
            rec["count_F"] = int(rec["F"] > 0)
            rec["count_R"] = int(rec["R"] > 0)
            rec["count_S"] = int(rec["S"] > 0)
            rec["count_Fr"] = int(rec["Fr"] > 0)
            rec["count_L"] = int(rec["L"] > 0)
            try:
                # Parse Coordinates
                cords = _parse_cords(rec["Coordination"])
                if cords:
                    rec["Coordination"] = cords
                else:
                    rec.pop("Coordination")
            except KeyError:
                break

            # Index the data to google storage
            update_time, rec_ref = db.collection(index_name).add(rec)

        progress_counter += 1
        progress = progress_counter / num_files
        progress_var.set(progress)
        percentage_label.configure(text=(("%.2f " % (progress * 100)) + "%"))


def fetch_and_index_data(
    progress_var, percentage_label, status_label, num_files, index_name="microbiome"
):
    """
    Fetches data from CSV files and indexes it into Google Storage.

    Parameters:
    - progress_var: Tkinter variable for tracking progress.
    - percentage_label: Tkinter label for displaying progress percentage.
    - status_label: Tkinter label for displaying status messages.
    - num_files: Total number of CSV files to process.
    - index_name: Name of the Google Storage index (default is "microbiome").

    Returns:
    None
    """
    status_label.configure(text="Uploading...")

    # Save documents to Google Storage
    _save_docs(
        progress_var=progress_var,
        percentage_label=percentage_label,
        num_files=num_files,
        index_name=index_name,
    )
