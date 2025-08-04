FROM python:3.10-slim

WORKDIR /app

# Copy both producer.py and the wait script
COPY producer.py .
#COPY wait-for-kafka.sh .

# RUN apt-get update && apt-get install -y netcat-openbsd && \
#     chmod +x wait-for-kafka.sh && \
#     pip install --no-cache-dir kafka-python
RUN pip install --no-cache-dir redis faker

#ENTRYPOINT ["sh", "./wait-for-kafka.sh", "kafka", "9092", "python", "producer.py"]
CMD ["python", "producer.py"]