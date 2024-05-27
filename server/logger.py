import logging


class Logger:
    def __init__(self) -> None:
        self.log = logging.getLogger('__logger__')
        self.log.setLevel(logging.DEBUG)

        # Create a file for logger handling
        handler = logging.FileHandler('logs.log', mode='a', encoding='utf-8')
        # set a format to log message
        formatter = logging.Formatter(
            '%(asctime)s\t%(levelname)s\t%(message)s', '%d-%m-%Y %H:%M:%S')

        handler.setFormatter(formatter)  # Add formatter to handler
        self.log.addHandler(handler)  # Add handler to logger


logger = Logger()
