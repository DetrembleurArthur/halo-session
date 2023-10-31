import logging
from logging.handlers import RotatingFileHandler

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = RotatingFileHandler("/var/log/halo-session/hs.log", maxBytes=1000000, backupCount=10)
logger.addHandler(handler)
