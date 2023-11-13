import os
import sys

parent_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(parent_dir)


from opensearchpy import OpenSearch
import pandas as pd
from .config import *
import logging

logger = logging.getLogger('ES')

client = OpenSearch(
    hosts=[{'host': ES_host, 'port': ES_port}],
    http_compress=True,
    http_auth=(ES_user, ES_password),
    use_ssl=True,
    verify_certs=True,
    ssl_assert_hostname=False,
    ssl_show_warn=False
)

def _parse_cords(raw_cords):
    try:
        split_cords = raw_cords.split(',')
    except AttributeError:
        return
    return {"lat": float(split_cords[0]), "lon": float(split_cords[1])}

def _create_index(client, mappings, index_name):
    if not client.indices.exists(index=index_name):
        client.indices.create(index=index_name, body=mappings)

def _save_docs(progress_var, percentage_label, num_files, index_name):
    progress_counter = 0
    counter = 1
    for file in os.listdir(f"{parent_dir}/../kitDataMerger/Fungi_meta_data"):
        # Index data into Elasticsearch
        df = pd.read_csv(f"{parent_dir}/../kitDataMerger/Fungi_meta_data/{file}")
        records = df.to_dict(orient='records')
        bulk_str = ''
        skip = False
        for rec in records:
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
                skip = True
                break
            bulk_str += '{"index": {"_index": "' + index_name + '", "_id": ' + str(counter) + ' }}\n' + str(rec).replace("'", '"').replace("nan", '""').replace("ח\"צ", "ח\\\"צ") + "\n"
            counter += 1

        if not skip:
            client.bulk(bulk_str)

        progress_counter += 1
        progress = (progress_counter / num_files) * 100
        progress_var.set(progress)
        percentage_label.config(text=(('%.2f ' % progress) + '%'))




def fetch_and_index_data(progress_var, percentage_label, status_label, num_files):
    request_body = {
        'mappings': {
            'properties': {
                'Coordination': {
                    'type': 'geo_point'
                },
                'F': {
                    'type': 'double'
                },
                'R': {
                    'type': 'double'
                },
                'S': {
                    'type': 'double'
                },
                'Fr': {
                    'type': 'double'
                }
            }
        }
    }
    status_label.config(text="Uploading...")
    _create_index(client, request_body, "fungi-samples-v1")
    _save_docs(progress_var=progress_var, percentage_label=percentage_label, num_files=num_files, index_name="fungi-samples-v1")


if __name__ == '__main__':
    fetch_and_index_data()