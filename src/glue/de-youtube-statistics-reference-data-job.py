import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
import gs_flatten

args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Script generated for node AWS Glue Data Catalog
AWSGlueDataCatalog_node1788836117283 = glueContext.create_dynamic_frame.from_catalog(database="de-youtube-raw", table_name="raw_statistics_reference_data", transformation_ctx="AWSGlueDataCatalog_node1788836117283")

# Script generated for node Amazon S3
AmazonS3_node1788836368299 = glueContext.create_dynamic_frame.from_options(format_options={}, connection_type="s3", format="parquet", connection_options={"paths": ["s3://de-on-youtube-cleansed-useast1-s3/statistics_reference_data/"], "recurse": True}, transformation_ctx="AmazonS3_node1788836368299")

# Script generated for node Flatten
Flatten_node1788837716719 = AWSGlueDataCatalog_node1788836117283.gs_flatten(maxLevels=0)

job.commit()
