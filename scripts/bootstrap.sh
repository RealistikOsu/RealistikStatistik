#!/usr/bin/env bash
set -eo pipefail

cd /srv/root

if [ -z "$APP_ENV" ]; then
  echo "Please set APP_ENV"
  exit 1
fi

if [ -z "$APP_COMPONENT" ]; then
  echo "Please set APP_COMPONENT"
  exit 1
fi

echo "Waiting for services to become available..."

/scripts/await_service.sh $READ_DB_HOST $READ_DB_PORT $SERVICE_READINESS_TIMEOUT
/scripts/await_service.sh $REDIS_HOST $REDIS_PORT $SERVICE_READINESS_TIMEOUT

if [[ $APP_COMPONENT == "api" ]]; then
  echo "Starting server..."
  exec python3.10 main.py
else
  echo "Unknown APP_COMPONENT: $APP_COMPONENT"
  exit 1
fi
