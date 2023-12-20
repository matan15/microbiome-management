
# Microbiome Kibana Management

This project is designed to manage the microbiome-kibana integration. It has 7 tools to integrate with Kibana.

## Installation
Download the latest project release, extract the files, and run the main.exe file.

IMPORTANT: Don't move/delete any files from the folders. moving/deleting files can crash the program.

If you running the program for the first time, you will be prompted for credentials.

## Updating the program
First, you'll need to remove the program from your PC, then, download the latest version from the GitHub releases.

## Setup the project for development

### Navigate to the directory you want to download the project
```bash
cd MY_DIRECTORY
```
replace ```MY_DIRECTORY``` with a real path to the directory.

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

### Run the project
```bash
python main.py
```

## Running the project for the second time...
### Navigate to the directory where the project is located
```bash
cd MY_DIRECTORY
```
replace ```MY_DIRECTORY``` with a real path to the directory.

### Go to the project directory

```bash
cd kit-data-merger
```

### Activate the environment
```bash
cd env/Scripts && activate && cd ../..
```

### Run the project
```bash
python main.py
```

## IMPORTANT: Meta-Data File Structure
To prevent critical errors, please make sure your meta-data file is formatted correctly:
1. Each word in a column's name/title is capitalized ("This Is An Example For A Column Name")
2. Coordinates are separated by a comma only, without any spaces: lat,lon (e.g. 38.897957,-77.036560).
3. The following columns MUST be included: Kit ID, Date, Location, Coordination, Location Picture, Treatment, Plant Picture, Temperature, School, Scientific Plant Name, Hebrew Plant Name.
4. Avoid whitespaces anywhere in the file.
5. All the dates should be in American format.

## User Instructions

If you are running the program for the first time, once you run the program, it will show an error because it couldn't find the credentials. Once you click ok, it will ask you to do the setup process, please answer all the questions.

The user window is divided to 7 tools, which allows to the user do 7 actions with the program.

![screenshot](/static/images/screenshot.png "screenshot")

You can switch between actions in the toolbar at the top of the window.

1. "Documentation": The documentation about the project, you can read it to know how to use the program.
2. "Upload Samples": A tool to upload samples to Kibana. In the first field, you select the data folder using the "Browse" button (inside the folder the data should be divided into sequences, in each sequence there must be an "ASV" folder). In the second field, you select the metadata file (A CSV file, check the section "IMPORTANT: Meta-Data File Structure"). If you want to upload the data to Kibana, check the checkbox "Upload to Kibana". The program will merge files and upload the data to Kibana. At the end, the program will save the data that has been uploaded to Kibana in any location you choose at the end of the running of the program
3. "Delete kit": At the field, you need to enter a kit ID (it must be a number). The program will delete the kit from Kibana.
4. "Delete All Data": the program will delete all the data from Kibana.
5. "Get all the data": In the field, you should choose a location where to save the data using the "Browse" button. Once you click submit, the program will download all the data to kibana_data.csv in the location you chose.
6. "Get Kit": In the first field, you should write the kit ID you want to get (the kit ID must be a number). In the second field, you should select the location where to save the data using the "Browse" button. Once you click Submit, the program will save the data in the location you provided in the file kibana_data.csv.
6. "Update Credentials": if there are credentials that you need to change, you can change them in the "Update Credentials" tool.

## Issues & Questions
If you have any issues with the program or questions, contact us:

Matan: matan.naydis@gmail.com
Tomer: tomer.bolt@gmail.com
