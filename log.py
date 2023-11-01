import logging
from logging.handlers import RotatingFileHandler

formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = RotatingFileHandler("/var/log/halo-session/hs.log", maxBytes=1000000, backupCount=10)
handler.setFormatter(formatter)
logger.addHandler(handler)

if __name__ == "__main__":
	logger.info("TEST")
