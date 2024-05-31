import logging

from os import mkdir


class Logger:
    def __init__(self) -> None:
        self.log_message = '%(asctime)s\t%(levelname)s\t%(message)s'
        self.tFormat = '%d-%m-%Y %H:%M:%S'

        # Create data folder if not exist
        try:
            mkdir('data')
        except FileExistsError:
            pass

    def _create_infoLogger(self):
        """Logger for info messages"""

        self.log = logging.getLogger('info')
        self.log.setLevel(logging.INFO)

        # Create a file for logger handling
        handler = logging.FileHandler(
            'data/logs.log', mode='a', encoding='utf-8')
        # set a format to log message
        formatter = logging.Formatter(self.log_message, self.tFormat)

        handler.setFormatter(formatter)  # Add formatter to handler
        self.log.addHandler(handler)  # Add handler to logger

    def _create_debugLogger(self):
        """Logger for debug messages and error handlers"""

        self.debug = logging.getLogger('debug')
        self.debug.setLevel(logging.DEBUG)

        # Create a file for logger handling
        handler = logging.FileHandler(
            'data/debug.log', mode='a', encoding='utf-8')
        # set a format to log message
        formatter = logging.Formatter(self.log_message, self.tFormat)

        handler.setFormatter(formatter)  # Add formatter to handler
        self.debug.addHandler(handler)  # Add handler to logger


logger = Logger()
logger._create_infoLogger()
logger._create_debugLogger()
