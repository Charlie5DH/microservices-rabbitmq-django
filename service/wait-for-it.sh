#!/bin/sh
# wait-for-postgres.sh

echo "Waiting for rabbit..."

if curl http://rabbitmq:15672/api/aliveness-test/
then
  echo "Rabbit is up"
else
  echo "Rabbit is down"
  exit 1
fi