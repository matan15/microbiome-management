import os

import re
import shutil

def filter(
    data_dir,
    progress_var,
    percentage_label,
    status_label,
    sample_type,
):
    # If the destination direcorty already exists, delete it
    if os.path.exists(f"./kitDataMerger/filtered_data"):
        shutil.rmtree(f"./kitDataMerger/filtered_data")

    # Initialise a filtered-file counter to track progress
    progress_counter = 0

    # Set the progress bar text label
    status_label.configure(text="Filtering data...")

    os.makedirs(f"./kitDataMerger/filtered_data")
    if sample_type == "Bacteria":
        # Count how many files to be filtered are there
        num_files = sum([1 for _ in os.listdir(data_dir)])
        # Copy files that match the creteria (Starts with "S")
        for filename in os.listdir(data_dir):
            if re.match(r"^S(\d+)_(Fr|R|S|F|L)(.*)", filename):
                with open(f"./kitDataMerger/filtered_data/{filename}", "w") as f:
                    shutil.copy2(
                        f"{data_dir}/{filename}",
                        f'./kitDataMerger/filtered_data/{filename.upper() if not "Fr" in filename else filename}',
                    )

            progress_counter += 1
            progress = progress_counter / num_files
            progress_var.set(progress)
            percentage_label.configure(text=(("%.2f " % (progress * 100)) + "%"))

    elif sample_type == "Fungi":
        num_files = 0
        # Count how many files to be filtered are there
        for seq_folder in os.listdir(data_dir):
            for filename in os.listdir(
                f"./kitDataMerger/fungi/data/microbiome-public/{seq_folder}"
            ):
                num_files += 1
        # Copy files that match the creteria (files that starts with "S")
        for seq_folder in os.listdir(data_dir):
            for filename in os.listdir(
                f"./kitDataMerger/fungi/data/microbiome-public/{seq_folder}"
            ):
                if re.match(r"^S(\d+)_(Fr|R|S|F|L)(.*)", filename):
                    filename = f"{'.'.join((filename.upper() if not 'Fr' in filename else filename).split('.')[:-1])}.csv"
                    with open(f"./kitDataMerger/filtered_data/{filename}", "w") as f:
                        shutil.copy2(
                            f"./kitDataMerger/fungi/data/microbiome-public/{seq_folder}/{filename}",
                            f"./kitDataMerger/filtered_data/{filename}",
                        )

                progress_counter += 1
                progress = progress_counter / num_files
                progress_var.set(progress)
                percentage_label.configure(text=(("%.2f " % (progress * 100)) + "%"))

    return True  # As a success
