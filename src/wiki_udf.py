import re
from pyspark.sql.types import ArrayType, StringType
from pyspark.sql.functions import udf

AZ_time = {
    "A": "00:00:00",
    "B": "01:00:00",
    "C": "02:00:00",
    "D": "03:00:00",
    "E": "04:00:00",
    "F": "05:00:00",
    "G": "06:00:00",
    "H": "07:00:00",
    "I": "08:00:00",
    "J": "09:00:00",
    "K": "10:00:00",
    "L": "11:00:00",
    "M": "12:00:00",
    "N": "13:00:00",
    "O": "14:00:00",
    "P": "15:00:00",
    "Q": "16:00:00",
    "R": "17:00:00",
    "S": "18:00:00",
    "T": "19:00:00",
    "U": "20:00:00",
    "V": "21:00:00",
    "W": "22:00:00",
    "X": "23:00:00"
}


def split_hourly(string):
    add_delim = re.sub(r'([A-Z])', r',\1', re.sub(r'[,:=/]', '', string))
    return list(filter(None, add_delim.split(',')))


split_hourly_udf = udf(split_hourly, ArrayType(StringType()))
