import logging
import os
import sys
from datetime import datetime

# 1. Log file ka naam set karein
LOG_FILE = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"

# 2. Logs folder ka path (Project root mein banane ke liye)
log_path = os.path.join(os.getcwd(), "logs")
os.makedirs(log_path, exist_ok=True)

LOG_FILEPATH = os.path.join(log_path, LOG_FILE)

# 3. Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(lineno)d %(name)s - %(levelname)s - %(message)s",
    
    handlers=[
        logging.FileHandler(LOG_FILEPATH), # File mein save karega
        logging.StreamHandler(sys.stdout)  # Terminal par bhi dikhayega
    ]
)

# Taake isay doosri files mein import kiya ja sake
# from src.logger import logging