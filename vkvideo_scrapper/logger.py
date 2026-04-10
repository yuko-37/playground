import logging
import logging.handlers


def configure_logging(level: int = logging.INFO) -> None:
    fmt = "%(asctime)s  %(levelname)-8s  %(name)s  %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(fmt, datefmt=datefmt)

    root = logging.getLogger()
    if root.handlers:
        return

    root.setLevel(level)

    file_handler = logging.handlers.RotatingFileHandler(
        "vkvideo.log",
        maxBytes=100 * 1024,  # 100 KB
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root.addHandler(console_handler)
