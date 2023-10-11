import sys
import os

parent_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(parent_dir)

import pandas as pd
from tkinter import filedialog as fd
from tkinter.messagebox import askokcancel, INFO
import re
import shutil

def merge_meta_data():
    answer = askokcancel('Choose file', 'Click ok to choose the Meta data file.', icon=INFO)
    if not answer: return
    filepath = fd.askopenfilename(filetypes=(("CSV UTF-8 (Comma delimited)", "*.csv"),))
    df_meta = pd.read_csv(filepath)
    for file in os.listdir(f"{parent_dir}/merged_asv_data"):
        df_kit = pd.read_csv(f"{parent_dir}/merged_asv_data/{file}")
        clean_filename = file.split('.')[0]
        id = re.search(r'S_(\d+)*', clean_filename).group(1)
        print(id)
        kit_row = df_meta.loc[df_meta['Kit ID'] == id]
        print(kit_row)
        #df_merged = pd.merge()
    shutil.rmtree(f"{parent_dir}/merged_asv_data")