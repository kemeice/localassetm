import redis
import json
import time

from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark.sql.functions import col, from_json, expr, sum as _sum

# 1. Spark session
spark = SparkSession.builder \
    .appName("AssetManagementConsumerRedis") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# 2. Redis connection
r = redis.Redis(host='redis', port=6379)
stream_key = "asset-management-stream"
last_id = "0-0"  # start from beginning; use '$' to read only new events

# 3. Unified schema definitions
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

# 4. Continuous batch loop
print("🔄 Starting Redis consumer loop...")
while True:
    response = r.xread({stream_key: last_id}, block=5000, count=100)
    if not response:
        continue

    data = []
    for stream, messages in response:
        for msg_id, msg in messages:
            last_id = msg_id
            flat_msg = {k.decode(): v.decode() for k, v in msg.items()}
            data.append(flat_msg)

    if not data:
        continue

    # 5. Create Spark DataFrame
    df = spark.read.json(spark.sparkContext.parallelize([json.dumps(d) for d in data]))

    # 6. Separate streams by type
    fx_df = df.filter(col("type") == "fx_trade").selectExpr("*")
    stock_df = df.filter(col("type") == "stock_trade").selectExpr("*")
    portfolio_df = df.filter(col("type") == "portfolio_valuation").selectExpr("*")

    # 7. Type conversions for aggregations
    fx_df = fx_df.withColumn("trade_volume", fx_df["trade_volume"].cast("double"))
    stock_df = stock_df.withColumn("trade_volume", stock_df["trade_volume"].cast("int"))
    portfolio_df = portfolio_df.withColumn("total_value", portfolio_df["total_value"].cast("double"))

    # 8. Aggregations
    fx_agg = fx_df.groupBy("fx_pair").agg(_sum("trade_volume").alias("total_volume"))
    stock_agg = stock_df.groupBy("ticker").agg(_sum("trade_volume").alias("total_volume"))
    portfolio_avg = portfolio_df.agg(expr("avg(total_value) as avg_portfolio_value"))

    # 9. Output to console
    print("\n📊 FX Aggregate:")
    fx_agg.show(truncate=False)

    print("📈 Stock Aggregate:")
    stock_agg.show(truncate=False)

    print("💼 Portfolio Average:")
    portfolio_avg.show(truncate=False)

    time.sleep(5)  # simulate micro-batch interval