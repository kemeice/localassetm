import time
import json
import random
import redis
from faker import Faker

# Initialize Faker and Redis
fake = Faker()
r = redis.Redis(host='redis', port=6379)
stream_key = "asset-management-stream"

# Global config
fx_pairs = ['EUR/USD', 'USD/JPY', 'GBP/USD', 'USD/CHF', 'AUD/USD']
currencies = ['USD', 'EUR', 'JPY', 'GBP', 'CHF', 'AUD']
stocks = ['AAPL', 'GOOG', 'TSLA', 'MSFT', 'AMZN']
fx_rates = {pair: round(random.uniform(0.8, 1.2), 5) for pair in fx_pairs}  # initial FX rates


def update_fx_rates():
    """Apply small drift to FX rates"""
    for pair in fx_pairs:
        drift = random.uniform(-0.002, 0.002)
        fx_rates[pair] = max(0.4, round(fx_rates[pair] + drift, 5))


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
print(f"🚀 Starting Redis producer -> stream: {stream_key}")

try:
    while True:
        update_fx_rates()
        event = random.choices(
            [generate_fx_trade, generate_stock_trade, generate_portfolio_valuation],
            weights=[0.4, 0.4, 0.2]
        )[0]()

        # Redis requires key-values as strings
        redis_event = {k: str(v) for k, v in event.items()}

        r.xadd(stream_key, redis_event)
        print(f"✅ Sent: {event}")

        time.sleep(0.5)  # ~2 events per second

except KeyboardInterrupt:
    print("⛔️ Stopping producer...")