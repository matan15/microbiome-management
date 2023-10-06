import sys
import os

parent_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(parent_dir)

import requests
from .config import *
import pandas as pd
import tkinter as tk

headers = {"Content-Type": "application/x-ndjson"}

index_name = "fungi-api-test-mt"

# Elasticsearch configuration
es_url = f'https://{ES_user}:{ES_password}@{ES_host}/{index_name}/_bulk/'

def fetch_and_index_data(progress_var: tk.DoubleVar, percentage_label: tk.Label, status_label: tk.Label, num_files):
    progress_counter = 0
    status_label.config(text="Uploading...")
    try:
        for file in os.listdir(f"{parent_dir}/../kitDataMerger/merged_asv_data"):
            # Index data into Elasticsearch
            df = pd.read_csv(f"{parent_dir}/../kitDataMerger/merged_asv_data/{file}")
            records = df.to_dict(orient='records')
            bulk_str = ''
            for rec in records:
                bulk_str += '{"index": {"_index": "' + index_name + '"}}\n' + str(rec).replace("'", '"') + "\n"

            es_response = requests.post(es_url, data=bulk_str, headers=headers)

            progress_counter += 1
            progress = (progress_counter / num_files) * 100
            progress_var.set(progress)
            percentage_label.config(text=(('%.2f ' % progress) + '%'))

            # Handle errors or log success
            if es_response.status_code != 200:
                print(f"Failed to index: {es_response.text}")
            else:
                print(f"Indexed successfully")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    fetch_and_index_data()
