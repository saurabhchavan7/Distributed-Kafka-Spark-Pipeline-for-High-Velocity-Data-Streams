from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import StructField, DoubleType, LongType

KAFKA_BROKERS = "kafka-broker-1:19092,kafka-broker-2:19092,kafka-broker-3:19092"
SOURCE_TOPIC = 'financial_transactions' # whre the data is coming from
AGGREGATES_TOPIC = 'transaction_aggregates' # so we want to do some processing and send it to another topic
ANOMALIES_TOPIC = 'transaction_anomalies' # simple as high volume of transactions
CHECKPOINT_DIR = '/mnt/spark-checkpoints' # we did this in main.py file in volumes: checkpoints
STATES_DIR = '/mnt/spark-state'  # this is the mount

spark = SparkSession.builder \
    .appName("FinancialTransactionProcessor") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
    .config("spark.sql.streaming.checkpointLocation", CHECKPOINT_DIR) \
    .config("spark.sql.shuffle.partitions", 5) \
    .config("spark.sql.streaming.stateStore.stateStoreDir", STATES_DIR) \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN") # just for decoration

transaction_schema = StructType([
    StructField("transactionId", StringType(), True),
    StructField("userId", StringType(), True),
    StructField("merchantId", StringType(), True),
    StructField("amount", DoubleType(), True),
    StructField("transactionTime", LongType(), True),
    StructField("transactionType", StringType(), True),
    StructField("location", StringType(), True),
    StructField("paymentMethod", StringType(), True),
    StructField("isInternational", StringType(), True),
    StructField("currency", StringType(), True),
])

# so the transaction schema is defined here
# next we will read the data from kafka
# then we will do some processing

kafka_stream = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BROKERS) \
    .option("subscribe", SOURCE_TOPIC) \
    .option("startingOffsets", "earliest") \
    .load()
# we want to start from the earlies but it gets tricky here
# the first time we run the job, it will start from the earliest
# but if we stop the job and start it again, it will start from the latest
# so we need to handle this in the code
# otherwise we will have to start from the earliest every time

# now we have the data in kafka_stream
# next thing is to extract the data from the kafka_stream
# that will be our transactions_df which will be kafka_stream.selectExpr("CAST(value AS STRING)") ....



# Deserialize JSON Data
transactions_df = kafka_stream.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), transaction_schema).alias("data")) \
    .select("data.*")

# Add Derived Columns
transactions_df = transactions_df.withColumn(
    "transactionTimestamp", (col("transactionTime") / 1000).cast("timestamp")
)



# simple aggregation logic we want to do is just to aggregate the merchant and the total per each merchant
# later we can make the logice more complex as possible
# for now lets keep it simple

aggregated_df = transactions_df.groupby("merchantId") \
    .agg(
    sum("amount").alias('totalAmount'),
    count("*").alias("transactionCount"))

aggregation_query = aggregated_df \
    .withColumn("key", col('merchantId').cast("string")) \
    .withColumn("value", to_json(struct(
    col("merchantId"),
    col('totalAmount'),
    col("transactionCount")
))).selectExpr("key", "value") \
    .writeStream \
    .format('kafka') \
    .outputMode('update') \
    .option('kafka.bootstrap.servers', KAFKA_BROKERS) \
    .option('topic', AGGREGATES_TOPIC) \
    .option('checkpointLocation', f'{CHECKPOINT_DIR}/aggregates') \
    .start().awaitTermination()