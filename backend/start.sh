#!/usr/bin/env bash
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: $0 [controller] [worker]"
  echo "  controller   start the main UVicorn app (main:app)"
  echo "  worker       start the worker UVicorn app (worker:app on port 8001)"
  exit 1
fi

for role in "$@"; do
  case "$role" in
    controller)
      echo "[`date +'%H:%M:%S'`] Starting controller..."
      uv run uvicorn main:app --reload
      ;;
    worker)
      echo "[`date +'%H:%M:%S'`] Starting worker..."
      uv run uvicorn worker:app --reload --port 8001 
      ;;
    *)
      echo "Unknown role: $role"
      exit 1
      ;;
  esac
done