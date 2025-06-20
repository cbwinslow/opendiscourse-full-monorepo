#!/bin/bash
set -e

if ! command -v docker &>/dev/null; then
  echo "Docker not installed" >&2
  exit 1
fi

if ! command -v docker-compose &>/dev/null; then
  echo "docker-compose not installed" >&2
  exit 1
fi

docker-compose build
if docker-compose up -d; then
  echo "Services started"
else
  echo "Failed to start services" >&2
fi

docker-compose ps
