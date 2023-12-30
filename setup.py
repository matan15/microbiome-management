from cx_Freeze import Executable, setup
import sys

# Set the base platform for the executable
base = "Win32GUI" if sys.platform == "win32" else None

# Define the list of executables to be created
executables = [Executable("main.py", base=base, icon="./static/icons/plant.ico", target_name="kit Data Merger")]

includefiles = [
    "set_config.py", 
    "README.md",
    "static",
    "logs",
    "kitDataMerger",
    "GCS",
    "pages"
]

# Define the list of packages required for the executable
packages = [
    "os",
    "sys",
    "shutil",
    "threading",
    "tkinter",
    "requests",
    "dotenv",
    "pandas",
    "re",
    "logging",
    "datetime",
    "pytz",
    "numpy",
    "geopy",
    "time",
    "typing",
    "elasticsearch",
    "csv",
    "tkhtmlview",
    "markdown",
    "certifi"
]

# Set the options for the build
options = {
    "build_exe": {
        "packages": packages,
        "include_files": includefiles
    }
}

# Define the setup configuration
setup(
    name="kit Data Merger",
    version="2.2",
    options=options,
    executables=executables,
    author="Matan Naydis and Tomer Kimchi",
    description="""This project is designed to merge sample data from different plant areas (root, flower, fruit, and soil).
The samples are part of a microbiome research program, and the files are merged by sample kits."""
)