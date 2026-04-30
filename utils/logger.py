import logging
import sys


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(f"interview_coach.{name}")
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(logging.Formatter("%(asctime)s [%(name)s] %(levelname)s: %(message)s", datefmt="%H:%M:%S"))
        logger.addHandler(handler)
        logger.propagate = False
    return logger


def set_verbose(verbose: bool = True) -> None:
    root = logging.getLogger("interview_coach")
    root.setLevel(logging.DEBUG if verbose else logging.WARNING)
