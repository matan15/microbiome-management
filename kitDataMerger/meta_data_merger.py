import os

import pandas as pd
import re
import shutil
import logging

logging.getLogger("kitDataMerger")

def merge_meta_data():
    # Open and read the provided metadata file
    df_meta = pd.read_csv(f"./kitDataMerger/meteorology/meta_data_final.csv", encoding="utf-16", usecols=['Kit ID', 'Date', 'Location', 'Coordination', 'Location Picture', 'Treatment', 'Plant Picture', 'Temperature', 'School', 'Scientific Plant Name', 'Hebrew Plant Name', 'TD', 'TDmin', 'TDmax', 'TG', 'WSmax', 'WDmax', 'WS', 'WD', 'STDwd', 'Grad', 'NIP', 'DiffR', 'RH', 'Rain'])
    # Create or clear a destination directory
    if os.path.exists(f"./kitDataMerger/Fungi_meta_data"):
        shutil.rmtree(f"./kitDataMerger/Fungi_meta_data")
    os.makedirs(f"./kitDataMerger/Fungi_meta_data")
    
    # Iterate through the merged asv data
    for file in os.listdir(f"./kitDataMerger/merged_asv_data"):

        # Load the kit file into a dict
        df_kit = pd.read_csv(f"./kitDataMerger/merged_asv_data/{file}")
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
        if len(df.columns) != 37:
            logging.error(f"Not enough columns in kit ID {id}: {len(df.columns)}\nThe columns are: {df.columns}")

        try:
            df.to_csv(
                f"./kitDataMerger/Fungi_meta_data/{file}",
                index=False, 
                encoding="utf-16",
                sep="\t"
            )
        except Exception as e:
            print(e)


