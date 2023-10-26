
# Sample Kit Data Merger 

This project is designed to merge sample data from different plant areas (root, flower, fruit, and soil).

The samples are part of a microbiome research program, and the files are merged by sample kits.

## Setup the project

### Clone the project

```bash
  git clone https://github.com/matan15/kit-data-merger.git
```

### Go to the project directory

```bash
  cd kit-data-merger
```

### Create an environment and activate it

```bash
  python -m venv env && cd env/Scripts && activate && cd ../..
```

### Install requirements

```bash
  pip install -r requirements.txt
```

### Set the configuration file
```bash
  python set_config.py
```
Answer the questions that you will be asked.

### Run the project
```bash
  python main.py
```

## IMPORTANT: Meta-Data File Structure
To prevent critical errors, please make sure your meta-data file is formatted correctly:
1. Each word in a column's name/title is capitalised ("This Is An Example For A Column Name")
2. Coordinates are seperated by a comma only, without any spaces: lat,lon (e.g. 38.897957,-77.036560).
3. The following columns MUST be included: Kit ID, Date, Location, Coordination, Location Picture, Treatment, Plant Picture, Temperature, School, Scientific Plant Name, Hebrew Plant Name.
4. Avoid whitespaces anywhere in the file.

## User Instructions

![screenshot](/static/images/screenshot.png)

The window of the program built from 3 inputs:
1. In the first input field, you can choose the data folder by typing the path of the folder in the first input, or by clicking the button "Browse" that will open the file explorer.
2. In the second input field, you can choose the meta data file that will be merged into the data files. Type the path to the file in the second input or click the "Browse" button to choose the file with file explorer.
3. Optional: you can check the check box that is on the bottom of the window in order to upload the files to Open-Search.

When you filled all the fields, you can click the "Submit" button. After the program finishes the process the files will be saved in the folder that you choose in the file explorer (and will upload the data to Open-Search, if you choose the check box).

## Documantation

The program consists of 4 Python scripts:
1. data_filter - Receives a path for the raw directory. Filters the raw data by deleting redundant files (mismatching the "S[number][any other text]" filename format).
2. file_merger - Iterates through the filtered raw data files and merges them into sorted files (files called "s_{Kit ID}_fungi", containing all fungi in the specific kit). The merged and sorted files are saved in a temporary directory within the scripts' directory.
3. meta_data_merger - Receives a path for a meta data file, reads the file and adds relevant info to the merged files.
4. main - TODO

## Issues & Questions
If you have any issue with the program, contact us:

Matan: matan.naydis@gmail.com
Tomer: tomer.bolt@gmail.com