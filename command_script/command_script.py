from tkinter.filedialog import askopenfilename
from tkinter.messagebox import showinfo
import pandas as pd
import os

def generate_command():
    command = "POST /weizmann_texonomy_test/_bulk\n"
    id_counter = 0
    limit_counter = 0
    for dirname in os.listdir('../kit_data_merger/merged_asv_data'):
        for filename in os.listdir(f"../kit_data_merger/merged_asv_data/{dirname}"):
            df = pd.read_csv(filepath_or_buffer=f"../kit_data_merger/merged_asv_data/{dirname}/{filename}", encoding='utf-8-sig', header=0)
            df_dict = df.to_dict("index")
            for k, doc in df_dict.items():
                doc_str = "{"
                for dk, dv in doc.items():
                    if str(dv) == 'nan':
                        continue
                    if dk == 'Coordination':
                        dv = eval(dv)
                    doc_str += f'"{dk}": ' + _jsonify_value(dv) + ', '
                doc_str_ar = [l for l in doc_str]
                doc_str_ar[len(doc_str_ar) - 2] = '}'
                doc_str = ''.join(doc_str_ar)
                command += '{"index": {"_index": "weizmann_texonomy_test", "_id": ' + str(id_counter) + '}}\n' + doc_str + '\n'
                if limit_counter == 1250:
                    with open("bulk.txt", 'w', encoding="utf-8") as f:
                        f.write(command)
                    os.startfile("bulk.txt")
                    showinfo("bulk generated", "Copy the command and paste it in Kibana, then click ok")
                    limit_counter = 0
                    command = "POST /weizmann_texonomy_test/_bulk\n"
                limit_counter += 1
                id_counter += 1
    if limit_counter > 0:
        with open("bulk.txt", 'w', encoding="utf-8") as f:
            f.write(command)
        os.startfile("bulk.txt")


def _jsonify_value(val):
    if type(val) is str:
        return '"' + val.strip().replace('"', '\\"') + '"'
    return str(val).replace("'", '"')
