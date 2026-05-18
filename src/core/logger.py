import logging
import os

log_level = int(os.getenv("LOGLEVEL", logging.INFO))
logger = logging.getLogger(__name__)
logger.setLevel(log_level)
logger.propagate = False

# Formatiting
formatter = logging.Formatter(
    r"%(asctime)s - %(levelname)-7s %(threadName)-12s [%(filename)s:%(lineno)s - %(funcName)s()] - %(message)s"
)


if __name__ == "__main__":
    logger.info("Info logging test")
    logger.warning("Warning logging test")
    logger.error("Error logging test")
    logger.exception(Exception("Exception logging test"))
    logger.info(f"This is the log level {log_level}")
