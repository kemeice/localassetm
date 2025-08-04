import time
import json
import random
from faker import Faker
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
# Initialize Faker and Kafka
fake = Faker()
for attempt in range(20):
    try:
        producer = KafkaProducer(
            bootstrap_servers='kafka:9092',  # Docker Compose Kafka service name
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        print("KafkaProducer connected")
        break
    except NoBrokersAvailable as e:
        print(f"Kafka not ready, retrying ({attempt + 1}/20)...")
        time.sleep(10)
else:
    raise RuntimeError(" Kafka broker not available after 10 attempts")


# Global config
fx_pairs = ['EUR/USD', 'USD/JPY', 'GBP/USD', 'USD/CHF', 'AUD/USD']
currencies = ['USD', 'EUR', 'JPY', 'GBP', 'CHF', 'AUD']
stocks = ['AAPL', 'GOOG', 'TSLA', 'MSFT', 'AMZN']
fx_rates = {pair: round(random.uniform(0.8, 1.2), 5) for pair in fx_pairs}  # initial FX rates


# Update FX rates with small random drift
def update_fx_rates():
    for pair in fx_pairs:
        drift = random.uniform(-0.002, 0.002)
        fx_rates[pair] = max(0.4, round(fx_rates[pair] + drift, 5))


# Generate fake FX trade
def generate_fx_trade():
    pair = random.choice(fx_pairs)
    base_ccy, quote_ccy = pair.split('/')
    price = fx_rates[pair]
    volume = round(random.uniform(1_000, 1_000_000), 2)
    return {
        "type": "fx_trade",
        "trade_id": fake.uuid4(),
        "fx_pair": pair,
        "base_currency": base_ccy,
        "quote_currency": quote_ccy,
        "trade_price": price,
        "trade_volume": volume,
        "trade_value_quote": round(price * volume, 2),
        "timestamp": time.time(),
        "trader": fake.name(),
    }


# Generate fake stock trade
def generate_stock_trade():
    ticker = random.choice(stocks)
    price = round(random.uniform(50, 1500), 2)
    volume = random.randint(10, 10_000)
    return {
        "type": "stock_trade",
        "trade_id": fake.uuid4(),
        "ticker": ticker,
        "trade_price": price,
        "trade_volume": volume,
        "trade_value": round(price * volume, 2),
        "currency": "USD",
        "timestamp": time.time(),
        "trader": fake.name(),
    }


# Generate fake portfolio valuation
def generate_portfolio_valuation():
    return {
        "type": "portfolio_valuation",
        "portfolio_id": fake.uuid4(),
        "base_currency": random.choice(currencies),
        "total_value": round(random.uniform(1_000_000, 50_000_000), 2),
        "timestamp": time.time(),
        "manager": fake.name(),
    }


# Stream loop
topic = "asset-management-stream"
print(f"Starting producer for topic: {topic}")

try:
    while True:
        update_fx_rates()
        event = random.choices(
            [generate_fx_trade, generate_stock_trade, generate_portfolio_valuation],
            weights=[0.4, 0.4, 0.2]
        )[0]()

        producer.send(topic, event)
        print(f"✅ Sent: {event}")
        time.sleep(0.5)  # 2 events per second
except KeyboardInterrupt:
    print("Stopping producer...")
finally:
    producer.flush()
    producer.close()