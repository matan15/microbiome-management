import os
from .get_fungi_id import files_to_id
from tkinter.messagebox import showerror


def update_fungi_ids(fungi_data_folder, progress_var, percentage_label):
    # Create "./kitDataMerger/fungi/data/microbiome-private" if it is not exists
    if not os.path.exists(f"./kitDataMerger/fungi/data/microbiome-private"):
        os.makedirs(f"./kitDataMerger/fungi/data/microbiome-private")

    # Create "./kitDataMerger/fungi/data/microbiome-public" if it is not exists
    if not os.path.exists(f"./kitDataMerger/fungi/data/microbiome-public"):
        os.makedirs(f"./kitDataMerger/fungi/data/microbiome-public")

    progress_counter = 0

    # Count total amount of files
    total_files = 0
    for seq_folder in os.listdir(fungi_data_folder):
        total_files += len(
            [_ for _ in range(len(os.listdir(f"{fungi_data_folder}/{seq_folder}/ASV")))]
        )

    for seq_folder in os.listdir(fungi_data_folder):
        # Create seq folders in the public directory and the private directory
        os.makedirs(f"./kitDataMerger/fungi/data/microbiome-private/{seq_folder}")
        os.makedirs(f"./kitDataMerger/fungi/data/microbiome-public/{seq_folder}")
        for file in os.listdir(f"{fungi_data_folder}/{seq_folder}/ASV"):
            try:
                # Call the files_to_id function to find the id of the fungis
                files_to_id(
                    asv_path=f"{fungi_data_folder}/{seq_folder}/ASV/{file}",
                    taxonomy_path=f"{fungi_data_folder}/{seq_folder}/REP_TAXONOMY/{file.split('.')[0]}_rep_taxonomy.fasta.{file.split('.')[1]}",
                    rep_path=f"{fungi_data_folder}/{seq_folder}/REP/{file.split('.')[0]}_rep.fasta.{file.split('.')[1]}",
                    seq=seq_folder,
                    output_dir=f"./kitDataMerger/fungi/data",
                )

                progress_counter += 1
                progress = (progress_counter / total_files) * 100
                progress_var.set(progress)
                percentage_label.config(text=(("%.2f " % progress) + "%"))

            # Raise an error if file is not exist
            except FileNotFoundError as e:
                percentage_label.config(text="0 %")
                showerror("Error", "An error has occurred. File Not Found.")
                raise FileNotFoundError(e)
