import os
import logging.config
import configparser
from pathlib import Path
from pyspark.sql import SparkSession
from wiki_transform import WikiTransform

config = configparser.ConfigParser()
config.read_file(open(f"{Path(__file__).parents[0]}/config.cfg"))

logging.config.fileConfig(f"{Path(__file__).parents[0]}/logging.ini")
logger = logging.getLogger(__name__)


def main():
    logging.debug("Setting up Spark session.")
    spark = SparkSession.builder.appName("wiki").getOrCreate()

    logging.debug("Checking working zone for files.")
    working_zone = config.get("BUCKET", "WORKING_ZONE")
    for file in os.listdir(working_zone):
        if "pageview" in file:
            logging.debug(f"Starting pageview dataset transformations for {file}.")
            wt = WikiTransform(spark, file)
            wt.transform_pageview_dataset()


if __name__ == '__main__':
    main()