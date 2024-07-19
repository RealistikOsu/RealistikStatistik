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
elif [[ $APP_COMPONENT == "online_cron" ]]; then
  echo "Starting online history cron"
  exec python3.10 -m app.workers.daemons.online_history_crawler
elif [[ $APP_COMPONENT == "profile_graphs_cron" ]]; then
  echo "Starting profile graph cron"
  exec python3.10 -m app.workers.daemons.profile_graphs_crawler
elif [[ $APP_COMPONENT == "top_scores_cron" ]]; then
  echo "Starting top scores cache cron"
  exec python3.10 -m app.workers.daemons.top_scores_crawler
else
  echo "Unknown APP_COMPONENT: $APP_COMPONENT"
  exit 1
fi
