import logging, sys
from pathlib import Path
from datetime import datetime

def setup_logging():
    Path("logs").mkdir(exist_ok=True)

    script_name = Path(sys.argv[0]).stem
    log_filename = f"logs/{script_name}_{datetime.now():%Y%m%d_%H%M%S}.log"

    logging.basicConfig(
        level = logging.INFO,
        format = "%(asctime)s -%(name)s - %(levelname)s -%(funcName)s- %(message)s",
        handlers = [
            logging.FileHandler(log_filename),
            logging.StreamHandler()
        ]

    )

    return log_filename
