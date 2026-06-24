"""Logging setup."""

import logging
import os


def configure_logging(level: str = "INFO") -> None:
    os.makedirs("reports", exist_ok=True)
    
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s - %(message)s")
    
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    
    fh = logging.FileHandler("reports/trace.log", mode="a")
    fh.setFormatter(formatter)
    logger.addHandler(fh)
