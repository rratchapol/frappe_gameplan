#!/bin/bash

set -e

BENCH_DIR="/home/frappe/frappe-bench"

if [ -f "$BENCH_DIR/apps/frappe/pyproject.toml" ] || [ -f "$BENCH_DIR/apps/frappe/setup.py" ]; then
    echo "Bench already fully initialized, starting bench..."
    cd "$BENCH_DIR"
    bench start
    exit 0
fi

echo "Creating new bench..."
cd /home/frappe
bench init --skip-redis-config-generation frappe-bench

cd "$BENCH_DIR"

bench set-mariadb-host mariadb
bench set-redis-cache-host redis://redis:6379
bench set-redis-queue-host redis://redis:6379
bench set-redis-socketio-host redis://redis:6379

sed -i '/redis/d' ./Procfile
sed -i '/watch/d' ./Procfile

echo "Getting app gameplan from local workspace..."
# Copy the entire workspace to the bench so all custom files (like NewTaskDialog and gp_task.json) are included.
# We don't use soft-link to avoid Windows/Linux shared volume issues with node_modules.
mkdir -p "$BENCH_DIR/apps/gameplan"
cp -a /workspace/. "$BENCH_DIR/apps/gameplan/"

# Fix CRLF line endings on shell scripts coming from Windows host
find "$BENCH_DIR/apps/gameplan" -type f -name "*.sh" -exec sed -i 's/\r$//' {} \;

# Remove any pre-existing node_modules copied from Windows host to ensure a clean Linux build
rm -rf "$BENCH_DIR/apps/gameplan/node_modules" 2>/dev/null || true
rm -rf "$BENCH_DIR/apps/gameplan/frontend/node_modules" 2>/dev/null || true

# Register the app manually within bench, ensuring we don't concatenate with an existing line
echo "" >> "$BENCH_DIR/sites/apps.txt"
sed -i '/^$/d' "$BENCH_DIR/sites/apps.txt" # clean up any empty lines safely
echo "gameplan" >> "$BENCH_DIR/sites/apps.txt"
./env/bin/pip install -e apps/gameplan

echo "Installing frontend dependencies..."
cd "$BENCH_DIR/apps/gameplan/frontend"
yarn install
cd "$BENCH_DIR"

echo "Creating site gameplan.localhost..."
bench new-site gameplan.localhost \
    --force \
    --mariadb-root-password 123 \
    --admin-password admin \
    --no-mariadb-socket

bench --site gameplan.localhost install-app gameplan
bench --site gameplan.localhost set-config developer_mode 1
bench --site gameplan.localhost clear-cache
bench --site gameplan.localhost set-config mute_emails 1
bench --site gameplan.localhost add-user alex@example.com \
    --first-name Alex \
    --last-name Scott \
    --password 123 \
    --user-type 'System User' \
    --add-role 'Gameplan Admin'
bench use gameplan.localhost

bench build --app gameplan

echo "Starting bench..."
bench start
