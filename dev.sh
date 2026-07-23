#!/usr/bin/env bash
# One command to bring up Postgres + backend (uvicorn) + frontend (ng serve).
# Ctrl+C stops backend and frontend; Postgres keeps running (data persists in its volume).
set -uo pipefail
set -m  # job control: each background job below gets its own process group,
        # so we can kill uvicorn/ng-serve *and* their child processes on exit.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

VENV_DIR="$ROOT_DIR/.venv"
BACKEND_PID=""
FRONTEND_PID=""

cleanup() {
  echo
  echo "==> Stopping backend/frontend..."
  [ -n "$BACKEND_PID" ] && kill -- "-$BACKEND_PID" 2>/dev/null || true
  [ -n "$FRONTEND_PID" ] && kill -- "-$FRONTEND_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

echo "==> Starting Postgres (docker compose)"
docker compose up -d db

echo "==> Waiting for Postgres to be ready"
until docker compose exec -T db pg_isready -U user -d booking_db >/dev/null 2>&1; do
  sleep 1
done

if [ ! -d "$VENV_DIR" ]; then
  echo "==> Creating backend virtualenv (.venv) and installing dependencies"
  python3 -m venv "$VENV_DIR"
  "$VENV_DIR/bin/pip" install -q -r requirements.txt
fi

echo "==> Running migrations"
"$VENV_DIR/bin/alembic" upgrade head

echo "==> Starting backend on http://localhost:8000 (docs: /docs)"
"$VENV_DIR/bin/uvicorn" app.main:app --reload --port 8000 &
BACKEND_PID=$!

if [ ! -d "$ROOT_DIR/frontend/node_modules" ]; then
  echo "==> Installing frontend dependencies"
  (cd "$ROOT_DIR/frontend" && npm install)
fi

echo "==> Starting frontend on http://localhost:4200"
(cd "$ROOT_DIR/frontend" && npx ng serve --port 4200) &
FRONTEND_PID=$!

echo
echo "Backend:  http://localhost:8000/docs"
echo "Frontend: http://localhost:4200"
echo "(Ctrl+C to stop both; Postgres keeps running)"
echo

wait "$BACKEND_PID" "$FRONTEND_PID"
