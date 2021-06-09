import logging


def configure_logging(no_logging: bool):
    logger = logging.getLogger('fotoserver')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(filename)s | %(levelname)-8s | [%(asctime)s] | %(message)s')
    ch.setFormatter(formatter)
    if no_logging:
        logger.addHandler(logging.NullHandler())
    else:
        logger.addHandler(ch)
    return logger
