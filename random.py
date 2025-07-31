from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit, current_timestamp, expr

# Initialize Spark session
spark = SparkSession.builder \
    .appName("SCD2_Product_Dimension") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .getOrCreate()

# Load source data (replace with your actual source)
source_df = spark.read.jdbc(
    url="jdbc:sqlserver://<SERVER>:<PORT>;databaseName=<DATABASE>",
    table="<SCHEMA>.<PRODUCT_TABLE>",
    properties={
        "user": "<USERNAME>",
        "password": "<PASSWORD>",
        "driver": "com.microsoft.sqlserver.jdbc.SQLServerDriver"
    }
)

# Load target Delta table (if exists)
delta_path = "/path/to/delta/product_dim"
try:
    target_df = spark.read.format("delta").load(delta_path)
except Exception:
    # If not exists, create empty DataFrame with required schema
    target_df = spark.createDataFrame([], source_df.schema
        .add("is_current", "boolean")
        .add("start_date", "timestamp")
        .add("end_date", "timestamp")
    )

# Join on business key (e.g., product_id)
join_cond = [source_df.product_id == target_df.product_id, target_df.is_current == True]

# Find records to update (changed records)
changed_df = source_df.join(target_df, join_cond, "inner") \
    .where(
        (source_df.product_name != target_df.product_name) |  # Add other columns as needed
        (source_df.product_category != target_df.product_category)
    ) \
    .select(source_df["*"])

# Expire old records in target
expired_df = target_df.join(changed_df, "product_id", "inner") \
    .withColumn("is_current", lit(False)) \
    .withColumn("end_date", current_timestamp())

# New records (inserts)
new_df = source_df.join(target_df, source_df.product_id == target_df.product_id, "left_anti") \
    .withColumn("is_current", lit(True)) \
    .withColumn("start_date", current_timestamp()) \
    .withColumn("end_date", lit(None).cast("timestamp"))

# Updated records (inserts)
updated_df = changed_df \
    .withColumn("is_current", lit(True)) \
    .withColumn("start_date", current_timestamp()) \
    .withColumn("end_date", lit(None).cast("timestamp"))

# Unchanged current records
unchanged_df = target_df.join(changed_df, "product_id", "left_anti") \
    .where(col("is_current") == True)

# Combine all
final_df = unchanged_df.unionByName(expired_df).unionByName(new_df).unionByName(updated_df) 

# Write back to Delta table
final_df.write.format("delta").mode("overwrite").save(delta_path)
