import logging


def get_logger(name):
    log_format = '%(asctime)s  %(name)8s  %(levelname)5s  %(message)s'

    logging.basicConfig(
        level=logging.DEBUG,
        format=log_format,
        filename="ipp.log",
        filemode="w"
    )

    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    console.setFormatter(logging.Formatter(log_format))

    logging.getLogger(name)

    return logging.getLogger(name)