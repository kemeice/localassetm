FROM bitnami/spark:3.3.1

USER root

WORKDIR /app

COPY consumer.py .

# Install Python packages for Kafka and JSON processing
RUN pip install --no-cache-dir kafka-python pyspark

#Let Spark know to include Kafka connector
ENV SPARK_JARS_PACKAGES=org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.1


USER 1001

CMD ["spark-submit", "--packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.1", "consumer.py"]