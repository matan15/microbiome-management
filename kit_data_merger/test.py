import os

data = []

for dirname in os.listdir('merged_asv_data'):
    for filename in os.listdir(f"merged_asv_data/{dirname}"):
        s = f"{dirname}: {filename}"
        if s in data:
            print(s)
        data.append(s)
