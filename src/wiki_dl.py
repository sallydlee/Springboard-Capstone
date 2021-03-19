import logging
import configparser
import logging.config
from pathlib import Path
from wiki_extract import WikiPageViews
from datetime import datetime, timedelta


config = configparser.ConfigParser()
config.read_file(open(f"{Path(__file__).parents[0]}/config.cfg"))

logging.config.fileConfig(f"{Path(__file__).parents[0]}/logging.ini")
logger = logging.getLogger(__name__)

yesterday = datetime.now() - timedelta(1)
datetime.strftime(yesterday, "%Y%m%d")


def main():
    logging.debug("Downloading data.")
    print(str(yesterday.month))
    we = WikiPageViews(str(yesterday.year), f"{yesterday.month:02d}", str(yesterday.day))
    logging.debug(we.get_url())
    we.use_threading()


if __name__ == '__main__':
    main()

