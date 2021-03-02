# Springboard Capstone - Wikipedia Data Engineering Project
## Objective

In order to achieve a deeper understanding of DE concepts and tools, I am utilizing Wikipedia's abundant and large datasets to build a data pipeline.

## Technical Overview
Dump files from Wikipedia are accessible from: https://dumps.wikimedia.org/other/pageview_complete/. 
<br> Raw dump files are available: https://dumps.wikimedia.org/other/pagecounts-raw/
<br><br> These can be downloaded in bulk using the dump_access.py in the src folder. Date ranges can be altered in the config.xml file. When running the script, a parameter indicating the storage location is needed.
>python dump_access.py [storage_directory]

<br> Springboard's cloud service provider of choice is Microsoft Azure. Therefore we will be utilizing Azure Data Lake to store the data. Each day is roughly 2 GB so a month's worth of data ends up being ~60 GB. Due to the size of the data, I am using PySpark for processing the data.
