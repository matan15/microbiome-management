from cx_Freeze import setup, Executable
import sys

base = "Win32GUI" if sys.platform == "win32" else None

executables = [Executable("main.py", base=base, icon="static//icons/plant.ico", target_name="kit Data Merger")]

includefiles = [
    "set_config.py", 
    "README.md",
    "static",
    "logs",
    "kitDataMerger",
    "GCS"
]

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
    "elasticsearch"
]

options = {
    "build_exe": {
        "packages": packages,
        "include_files": includefiles
    }
}

setup(
    name="kit Data Merger",
    version="2.0",
    options=options,
    executables=executables,
    author="Matan Naydis and Tomer Kimchi",
    description="""This project is designed to merge sample data from different plant areas (root, flower, fruit, and soil).
The samples are part of a microbiome research program, and the files are merged by sample kits."""
)