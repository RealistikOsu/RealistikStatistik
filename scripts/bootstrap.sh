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

case "$APP_COMPONENT" in
  api)
    echo "Starting server..."
    exec python3.10 main.py
    ;;
  online_cron)
    echo "Starting online history crawler loop (every 5m)..."
    while true; do
      python3.10 -m app.workers.daemons.online_history_crawler || true
      sleep 300
    done
    ;;
  profile_graphs_cron)
    echo "Starting profile graphs crawler loop (every 24h)..."
    while true; do
      python3.10 -m app.workers.daemons.profile_graphs_crawler || true
      sleep 86400
    done
    ;;
  top_scores_cron)
    echo "Starting top scores crawler loop (every 24h)..."
    while true; do
      python3.10 -m app.workers.daemons.top_scores_crawler || true
      sleep 86400
    done
    ;;
  *)
    echo "Unknown APP_COMPONENT: $APP_COMPONENT"
    exit 1
    ;;
esac
