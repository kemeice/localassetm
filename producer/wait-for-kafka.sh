#!/bin/sh

HOST="$1"
PORT="$2"

echo "⏳ Waiting for Kafka DNS to resolve: $HOST..."

# Wait for Docker's internal DNS to resolve the hostname
until getent hosts "$HOST"; do
  echo "❌ DNS not ready for $HOST — retrying in 2s..."
  sleep 2
done

echo "✅ DNS resolved for $HOST. Waiting for port $PORT to open..."

# Wait for Kafka to be available on the resolved host and port
while ! nc -z "$HOST" "$PORT"; do
  echo "❌ Kafka not ready yet at $HOST:$PORT — retrying in 2s..."
  sleep 2
done

echo "✅ Kafka is up at $HOST:$PORT — starting app..."
exec "$@"