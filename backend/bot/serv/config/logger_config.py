import logging
from colorlog import ColoredFormatter

IMPORTANT = 25
logging.addLevelName(IMPORTANT, "IMPORTANT")


def get_logger(name="app_logger", log_file="app.log"):

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    def important(self, message, *args, **kwargs):
        self.log(IMPORTANT, message, *args, **kwargs)

    logging.Logger.important = important

    formatter = ColoredFormatter(
        fmt="%(log_color)s[%(asctime)s] [%(levelname)s] [%(module)s]: %(reset)s%(white)s%(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "IMPORTANT": "purple",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_white,bg_red",
        },
        style="%",
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)

    file_formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(module)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)

    if not logger.handlers:
        logger.addHandler(console_handler)

    return logger

