FROM bitnami/spark:3.3.1

USER root

WORKDIR /app

# Copy your Spark consumer script
COPY consumer.py .

# Install Python dependencies for Redis + PySpark
RUN pip install --no-cache-dir redis pyspark

# Clean out Kafka-related packages (remove the Kafka package env & submit option)
# ENV SPARK_JARS_PACKAGES=org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.1

USER 1001

CMD ["spark-submit", "consumer.py"]