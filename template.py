import os
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='[%(asctime)s]: %(message)s:')

list_of_files = [
    "src/__init__.py",
    "src/logger.py",
    "src/utils.py",
    "src/prompt.py",
    "notebook/data/.gitkeep", 
    "notebook/test_notebook.ipynb",
    "static/style.css",
    "templates/index.html",
    ".env",
    ".gitignore",
    "pyproject.toml",
    "app.py",
    "requirements.txt",
    "README.md"
]

for filepath in list_of_files:
    filepath = Path(filepath)
    filedir, filename = os.path.split(filepath)

    # Pehle check karein ke kahin folder ki jagah file to nahi bani hui
    if filename == "" and os.path.isfile(filedir):
        os.remove(filedir) # Purani ghalat file ko delete kar dega
        logging.info(f"Removed incorrect file: {filedir} to create directory")

    # Folder banayein
    if filedir != "":
        os.makedirs(filedir, exist_ok=True)
        logging.info(f"Creating directory: {filedir}")

    # File banayein (sirf agar filename maujood ho)
    if filename != "":
        if (not os.path.exists(filepath)) or (os.path.getsize(filepath) == 0):
            with open(filepath, "w") as f:
                pass
            logging.info(f"Creating empty file: {filepath}")
        else:
            logging.info(f"{filename} already exists")

print("\n--- Project Structure Created Successfully! ---")