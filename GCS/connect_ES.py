from elasticsearch import Elasticsearch, helpers
import os

import pandas as pd
import dotenv

dotenv.load_dotenv(dotenv.find_dotenv())

# Establish connection to Elasticsearch
es = Elasticsearch(
    cloud_id=os.environ.get("cloud_id"),
    http_auth=(os.environ.get("user"), os.environ.get("password"))
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
            split_cords = raw_cords.split(',')
        except AttributeError:
            return
        return {"lat": float(split_cords[0]), "lon": float(split_cords[1])}
    return None

def _save_docs(progress_var, percentage_label, num_files, index_name):
    """
    Save documents from CSV files to Elasticsearch index.

    Parameters:
    - progress_var: Tkinter variable for tracking progress.
    - percentage_label: Tkinter label for displaying progress percentage.
    - num_files: Total number of CSV files to process.
    - index_name: Name of the Elasticsearch index.

    Returns:
    None
    """
    documents = []
    progress_counter = 0
    progress_var.set(0)
    percentage_label.config(text=(('%.2f ' % 0) + '%'))
    for file in os.listdir(f"./kitDataMerger/Fungi_meta_data"):
        # Index data into Elasticsearch
        df = pd.read_csv(f"./kitDataMerger/Fungi_meta_data/{file}", encoding="utf-16", sep="\t")
        records = df.to_dict(orient='records')
        for rec in records:
            for key, value in rec.items():
                if pd.isnull(value) or str(value).lower() == 'nan' or value == '__':
                    rec[key] = None
            rec['count_F'] = int(rec['F'] > 0)
            rec['count_R'] = int(rec['R'] > 0)
            rec['count_S'] = int(rec['S'] > 0)
            rec['count_Fr'] = int(rec['Fr'] > 0)
            try:
                cords = _parse_cords(rec['Coordination'])
                if cords:
                    rec['Coordination'] = cords
                else:
                    rec.pop('Coordination')
            except KeyError:
                break
            documents.append({
                '_index': index_name,
                **rec
            })

        progress_counter += 1
        progress = (progress_counter / num_files) * 100
        progress_var.set(progress)
        percentage_label.config(text=(('%.2f ' % progress) + '%'))
    
    # Bulk insert documents into Elasticsearch
    helpers.bulk(es, documents)

def index_exists(index_name):
    """
    Check if an Elasticsearch index exists.

    Parameters:
    - index_name: Name of the Elasticsearch index.

    Returns:
    True if the index exists, False otherwise.
    """

    return es.indices.exists(index=index_name)

def fetch_and_index_data(progress_var, percentage_label, status_label, num_files, index_name="microbiome"):
    """
    Fetches data from CSV files and indexes it into Elasticsearch.

    Parameters:
    - progress_var: Tkinter variable for tracking progress.
    - percentage_label: Tkinter label for displaying progress percentage.
    - status_label: Tkinter label for displaying status messages.
    - num_files: Total number of CSV files to process.
    - index_name: Name of the Elasticsearch index (default is "microbiome").

    Returns:
    None
    """
    status_label.config(text="Uploading...")
    
    # Create index if it does not exist
    if not index_exists(index_name):
        mapping = {
            "properties": {
                "Coordination": {
                    "type": "geo_point",
                },
                "R": {
                    "type": "double"
                },
                "S": {
                    "type": "double"
                },
                "F": {
                    "type": "double"
                },
                "Fr": {
                    "type": "double"
                }
            }
        }
        es.indices.create(index=index_name, mappings=mapping)
    
    # Save documents to Elasticsearch
    _save_docs(progress_var=progress_var, percentage_label=percentage_label, num_files=num_files, index_name=index_name)
