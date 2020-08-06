"""Simple script for testing out pyspark with dataproc.

In order to submit this job to an existing cluster, first you have to create that cluster and
then you need to ensure that the bigquery adapter is available.

gcloud dataproc jobs submit pyspark etls/lor/simple_bigquery.py \
   --cluster wkerr-etl-test \
   --jars=gs://spark-lib/bigquery/spark-bigquery-latest.jar \
   --py-files=test.zip

"""
# Third Party
import pyspark
from utils import count

def main():
    sc = pyspark.SparkContext.getOrCreate()
    sqlContext = pyspark.SQLContext.getOrCreate(sc)

    df = (
        sqlContext.read.format("bigquery")
        .option("viewsEnabled", "true")
        .option("table", "lor-data-platform-dev-f369:lor_dw.game_event")
        .load()
    )

    # print(df.count())
    print(count(df))


if __name__ == "__main__":
    main()
