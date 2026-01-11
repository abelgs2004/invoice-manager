import logging
import uuid

def get_logger():
    logger = logging.getLogger("invoice")
    if not logger.handlers:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(message)s"
        )
    return logger

def new_request_id():
    return str(uuid.uuid4())[:8]
