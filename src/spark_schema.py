from pyspark.sql.types import *

pageview_schema = StructType([
    StructField("wikicode", StringType()),
    StructField("title", StringType()),
    StructField("page_id", StringType()),
    StructField("source", StringType()),
    StructField("daily_total", IntegerType()),
    StructField("hourly_total", StringType())
])