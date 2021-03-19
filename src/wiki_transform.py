import logging
import wiki_udf
import configparser
import spark_schema
from pathlib import Path
from itertools import chain
from datetime import datetime
from pyspark.sql.functions import *
from pyspark.sql.types import IntegerType


logger = logging.getLogger(__name__)

config = configparser.ConfigParser()
config.read_file(open(f"{Path(__file__).parents[0]}/config.cfg"))


class WikiTransform:
    def __init__(self, spark, file):
        self._spark = spark
        self._file = file
        self._load_path = config.get("BUCKET", "WORKING_ZONE")
        self._save_path = config.get("BUCKET", "PROCESSED_ZONE")

    def transform_pageview_dataset(self):
        logger.debug("Loading page views dataset")
        name_list = self._file.split("-")
        view_date = datetime.strptime(name_list[1], "%Y%m%d").date()

        pageview_df = (self._spark
                       .read
                       .option("header", "false")
                       .option("delimiter", " ")
                       .schema(spark_schema.pageview_schema)
                       .csv(self._load_path + self._file)
                       )

        logging.debug("Transforming page view dataset")
        pageview_df = pageview_df.filter((pageview_df.page_id != "null") & (pageview_df.wikicode == "en.wikipedia") &
                                         (pageview_df.title != "Main_Page"))
        pageview_df = pageview_df.drop("wikicode")
        pageview_df = (pageview_df
                       .withColumn("title", regexp_replace("title", "_", " "))
                       .withColumn("views_date", lit(view_date)).select("views_date", *pageview_df.columns)
                       )
        logging.debug("Creating hourly dataframe")
        hourly_df = (pageview_df
                     .drop("daily_total")
                     .withColumn("hourly_total", wiki_udf.split_hourly_udf("hourly_total"))
                     .withColumn("hourly_total", explode("hourly_total"))
                     )
        mapping = create_map([lit(x) for x in chain(*wiki_udf.AZ_time.items())])
        hourly_df = (hourly_df
                     .withColumn("time_indicator", regexp_extract("hourly_total", pattern="[A-Z]", idx=0))
                     .withColumn("hourly_total", regexp_replace("hourly_total", "[A-Z]", ""))
                     )
        hourly_df = hourly_df.withColumn("time_indicator", mapping[hourly_df['time_indicator']])
        hourly_df = (hourly_df
                     .withColumn('views_datetime',
                                 to_timestamp(concat(col('views_date'), lit(' '), col('time_indicator'))))
                     .withColumn("hourly_total", hourly_df.hourly_total.cast(IntegerType()))
                     .drop("views_date")
                     .drop("time_indicator")
                     )
        hourly_df = (hourly_df
                     .groupBy("title", "page_id", "views_datetime")
                     .pivot("source")
                     .max("hourly_total")
                     .sort("page_id", "views_datetime")
                     )
        daily_df = (pageview_df
                    .groupBy("title", "page_id", "views_date")
                    .pivot("source")
                    .max("daily_total")
                    .sort("page_id")
                    )

        logger.debug(f"Attempting to write data to {self._save_path}")
        daily_df.write.csv(self._save_path + "daily_" + self._file)
        hourly_df.write.csv(self._save_path + "hourly_" + self._file)

