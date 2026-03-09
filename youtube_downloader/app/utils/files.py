import os
import logging

logger = logging.getLogger(__name__)

def remove_file(path: str):
    try:
        if os.path.exists(path):
            os.remove(path)
            logger.error(f"Successfully deleted temporary file: {path}")
    except Exception as e:
        logger.error(f"Error deleting file {path}: {e}")