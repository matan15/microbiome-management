from cx_Freeze import Executable, setup
import sys

# Set the base platform for the executable
base = "Win32GUI" if sys.platform == "win32" else None

# Define the list of executables to be created
executables = [
    Executable(
        "main.py",
        base=base,
        icon="./static/icons/plant.ico",
        target_name="Microbiome Management",
    )
]

includefiles = [
    "GCP",
    "KitDataMerger",
    "logs",
    "pages",
    "static",
    ".gitignore",
    "README.md",
    "set_config.py",
    "sh_taxonomy_qiime_ver9_99_29.11.2022.txt",
    "utils.py",
]

# Define the list of packages required for the executable
packages = [
    "os",
    "dotenv",
    "typing",
    "sys",
    "cx_Freeze",
    "tkinter",
    "threading",
    "PIL",
    "shutil",
    "logging",
    "datetime",
    "csv",
    "certifi",
    "geopy",
    "google",
    "tkhtmlview",
    "markdown",
    "tempfile",
    "pandas",
    "re",
    "requests",
    "pytz",
    "numpy",
]

# Set the options for the build
options = {"build_exe": {"packages": packages, "include_files": includefiles}}

# Define the setup configuration
setup(
    name="Microbiome Management",
    version="2.4",
    options=options,
    executables=executables,
    author="Matan Naydis and Tomer Kimchi",
)
