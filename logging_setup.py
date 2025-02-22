import logging
import sys

def setup_logging():
    if sys.version_info >= (3, 9):
        logging.basicConfig(
            filename="spdl.log",
            filemode="a",
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            encoding="utf-8"
        )
    else:
        file_handler = logging.FileHandler("spdl.log", mode="a", encoding="utf-8")
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        logger.addHandler(file_handler) 