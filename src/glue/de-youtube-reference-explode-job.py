import sys
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import explode, col

args = getResolvedOptions(sys.argv, ['JOB_NAME'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

job = Job(glueContext)
job.init(args['JOB_NAME'], args)

df = spark.read.option("multiLine", "true").json(
    "s3://de-youtube-raw-useast1-krishna-2026/youtube/raw_statistics_reference_data/*.json"
)

final_df = (
    df.select(explode("items").alias("item"))
      .select(
          col("item.kind").alias("kind"),
          col("item.etag").alias("etag"),
          col("item.id").cast("bigint").alias("id"),
          col("item.snippet.channelId").alias("snippet_channelid"),
          col("item.snippet.title").alias("snippet_title"),
          col("item.snippet.assignable").alias("snippet_assignable")
      )
)

final_df.write.mode("overwrite").option("compression", "snappy").parquet(
    "s3://de-on-youtube-cleansed-useast1-s3/statistics_reference_data/"
)

job.commit()
