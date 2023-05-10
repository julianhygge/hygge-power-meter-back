import logging
import os

from hyggepowermeter.config.configuration import CONFIGURATION

# Set up the logger
logger = logging.getLogger("Hygge Energy System")
logger.setLevel(getattr(logging, CONFIGURATION.logging.level))

# Create a file handler for logging to a file
log_file = os.path.join(CONFIGURATION.logging.log_directory, "logfile.log")
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(getattr(logging, CONFIGURATION.logging.level))

# Create a stream handler for logging to the console
console_handler = logging.StreamHandler()
console_handler.setLevel(getattr(logging, CONFIGURATION.logging.level))

# Define the formatter and add it to both handlers
formatter = logging.Formatter('%(asctime)s %(levelname)-2s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)
