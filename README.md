
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
