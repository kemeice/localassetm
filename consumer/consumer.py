from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json , expr
from pyspark.sql.functions import sum as _sum
from pyspark.sql.types import *

import json

# 1. Create Spark session
spark = SparkSession.builder \
    .appName("AssetManagementConsumer") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# 2. Kafka configuration
topic = "asset-management-stream"
kafka_bootstrap_servers = "kafka:9092"

# 3. Read from Kafka topic as streaming DataFrame
raw_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", kafka_bootstrap_servers) \
    .option("subscribe", topic) \
    .option("startingOffsets", "earliest") \
    .load()

# 4. Define schema for all messages (union of all event types)
base_schema = StructType([
    StructField("type", StringType()),
    StructField("timestamp", DoubleType()),
])

fx_schema = base_schema \
    .add("trade_id", StringType()) \
    .add("fx_pair", StringType()) \
    .add("base_currency", StringType()) \
    .add("quote_currency", StringType()) \
    .add("trade_price", DoubleType()) \
    .add("trade_volume", DoubleType()) \
    .add("trade_value_quote", DoubleType()) \
    .add("trader", StringType())

stock_schema = base_schema \
    .add("trade_id", StringType()) \
    .add("ticker", StringType()) \
    .add("trade_price", DoubleType()) \
    .add("trade_volume", IntegerType()) \
    .add("trade_value", DoubleType()) \
    .add("currency", StringType()) \
    .add("trader", StringType())

portfolio_schema = base_schema \
    .add("portfolio_id", StringType()) \
    .add("base_currency", StringType()) \
    .add("total_value", DoubleType()) \
    .add("manager", StringType())

# 5. Parse JSON values
json_df = raw_df.selectExpr("CAST(value AS STRING) as json_string")

# 6. Filter and parse each type
fx_df = json_df \
    .filter("json_string LIKE '%fx_trade%'") \
    .select(from_json(col("json_string"), fx_schema).alias("data")) \
    .select("data.*")

stock_df = json_df \
    .filter("json_string LIKE '%stock_trade%'") \
    .select(from_json(col("json_string"), stock_schema).alias("data")) \
    .select("data.*")

portfolio_df = json_df \
    .filter("json_string LIKE '%portfolio_valuation%'") \
    .select(from_json(col("json_string"), portfolio_schema).alias("data")) \
    .select("data.*")

# 7. Basic analytics examples

# Total FX volume per pair
fx_agg = fx_df.groupBy("fx_pair").agg(_sum("trade_volume").alias("total_volume"))

# Top 5 traded stocks by volume
stock_agg = stock_df.groupBy("ticker").agg(_sum("trade_volume").alias("total_volume"))

# Average portfolio value
portfolio_avg = portfolio_df.agg(expr("avg(total_value) as avg_portfolio_value"))

# 8. Output to console (for demo only)
fx_query = fx_agg.writeStream \
    .outputMode("complete") \
    .format("console") \
    .option("truncate", False) \
    .start()

stock_query = stock_agg.writeStream \
    .outputMode("complete") \
    .format("console") \
    .option("truncate", False) \
    .start()

portfolio_query = portfolio_avg.writeStream \
    .outputMode("complete") \
    .format("console") \
    .option("truncate", False) \
    .start()

# 9. Await all streams
spark.streams.awaitAnyTermination()