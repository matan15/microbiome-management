import sys
import os

parent_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(parent_dir)

import pandas as pd
from tkinter import filedialog as fd
from tkinter.messagebox import askokcancel, INFO
import re
import shutil

def merge_meta_data(meta_file):
    # Open and read the provided metadata file
    # df_meta = pd.read_csv(meta_file, usecols=['Kit ID', 'Date', 'Location', 'Coordination', 'Location Picture', 'Treatment', 'Plant Picture', 'Temperature', 'School', 'Scientific Plant Name', 'Hebrew Plant Name'])
    df_meta = pd.read_csv(meta_file, usecols=['Kit ID', 'Date', 'Location', 'Coordination', 'Location Picture', 'Treatment', 'Plant Picture', 'Temperature', 'School', 'Scientific Plant Name', 'Hebrew Plant Name'])

    # Create or clear a destination directory
    if os.path.exists(f"{parent_dir}/Fungi_meta_data"):
        shutil.rmtree(f"{parent_dir}/Fungi_meta_data")
    os.makedirs(f"{parent_dir}/Fungi_meta_data")
    
    # Iterate through the merged asv data
    for file in os.listdir(f"{parent_dir}/merged_asv_data"):

        # Load the kit file into a dict
        df_kit = pd.read_csv(f"{parent_dir}/merged_asv_data/{file}")
        df_kit_dict = df_kit.to_dict()

        # Extract the kit id from the filename
        clean_filename = file.split('.')[0]
        id = re.search(r'S_(\d+)*', clean_filename).group(1)

        # Find the kit's matching metadata and load it into a dict
        kit_row = (df_meta.loc[df_meta['Kit ID'] == id]).to_dict(orient="split")
        for keyIndex in range(len(kit_row['columns'])):
            for index in range(len(df_kit_dict["kit_id"])):
                try:
                    df_kit_dict[kit_row['columns'][keyIndex]][index] = kit_row['data'][0][keyIndex]
                except KeyError:
                    df_kit_dict[kit_row['columns'][keyIndex]] = {}
                    df_kit_dict[kit_row['columns'][keyIndex]][index] = kit_row['data'][0][keyIndex]
                except IndexError:
                    continue

        df = pd.DataFrame.from_dict(df_kit_dict)

        df.to_csv(f"{parent_dir}/Fungi_meta_data/{file}", index=False)


