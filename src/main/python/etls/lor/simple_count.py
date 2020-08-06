"""Runs a simple script against and existing dataproc cluster demonstrating what ETLs could be.

gcloud dataproc jobs submit pyspark etls/lor/simple_count.py --cluster wkerr-dev
"""
# Third Party
import pyspark

sc = pyspark.SparkContext()
rdd = sc.parallelize(["hello,", "world!"])
words = sorted(rdd.collect())
print(words)
