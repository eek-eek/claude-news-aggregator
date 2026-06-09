#!/usr/bin/env bash
# Bootstrap / re-deploy the Claude News Aggregator on a fresh Ubuntu 24 VPS.
# Run as root from the directory containing this script and the .py files:
#     sudo bash deploy.sh
#
# Idempotent: safe to re-run. The API key is generated once and preserved.

set -euo pipefail

if [[ $EUID -ne 0 ]]; then
    echo "deploy.sh must be run as root" >&2
    exit 1
fi

DOMAIN="154-12-117-57.sslip.io"
ADMIN_EMAIL="${ADMIN_EMAIL:-admin@example.com}"
APP_DIR="/opt/claude-news"
DATA_DIR="/var/lib/claude-news"
CONF_DIR="/etc/claude-news"
LOG_DIR="/var/log/claude-news"
ENV_FILE="${CONF_DIR}/env"
SRC_DIR="$(cd "$(dirname "$0")" && pwd)"

APP_PORT="${APP_PORT:-18327}"

echo "==> checking port ${APP_PORT} availability"
if ss -ltn 2>/dev/null | awk '{print $4}' | grep -E "[:.]${APP_PORT}\$" >/dev/null; then
    echo "ERROR: port ${APP_PORT} already in use (possibly hermes or other service)." >&2
    echo "Set APP_PORT=<free port> and re-run, e.g.: APP_PORT=18999 sudo -E bash deploy.sh" >&2
    exit 1
fi

echo "==> installing system packages"
export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get install -y \
    python3 python3-venv python3-pip \
    nginx certbot python3-certbot-nginx \
    git curl openssl iproute2

echo "==> creating service user"
if ! id -u claude-news >/dev/null 2>&1; then
    useradd -r -s /bin/false claude-news
fi

echo "==> creating directories"
mkdir -p "${APP_DIR}" "${DATA_DIR}" "${CONF_DIR}" "${LOG_DIR}"

echo "==> copying source files"
cp "${SRC_DIR}/main.py" "${APP_DIR}/"
cp "${SRC_DIR}/db.py" "${APP_DIR}/"
cp "${SRC_DIR}/feed_fetcher.py" "${APP_DIR}/"
cp "${SRC_DIR}/feeds.py" "${APP_DIR}/"
cp "${SRC_DIR}/scheduler.py" "${APP_DIR}/"
cp "${SRC_DIR}/requirements.txt" "${APP_DIR}/"

echo "==> building virtualenv"
if [[ ! -d "${APP_DIR}/venv" ]]; then
    python3 -m venv "${APP_DIR}/venv"
fi
"${APP_DIR}/venv/bin/pip" install --upgrade pip
"${APP_DIR}/venv/bin/pip" install -r "${APP_DIR}/requirements.txt"

echo "==> generating env file (preserving existing API key on re-run)"
if [[ ! -f "${ENV_FILE}" ]]; then
    API_KEY="$(openssl rand -hex 32)"
    cat > "${ENV_FILE}" <<EOF
NEWS_API_KEY=${API_KEY}
NEWS_DB_PATH=${DATA_DIR}/db.sqlite
EOF
else
    echo "    (existing ${ENV_FILE} kept)"
    source "${ENV_FILE}"
    API_KEY="${NEWS_API_KEY}"
fi

echo "==> fixing ownership and permissions"
chown -R claude-news:claude-news "${APP_DIR}" "${DATA_DIR}" "${CONF_DIR}" "${LOG_DIR}"
chmod 600 "${ENV_FILE}"
chown root:claude-news "${ENV_FILE}"

echo "==> installing systemd unit (port ${APP_PORT})"
sed "s/--port [0-9]\\+/--port ${APP_PORT}/" "${SRC_DIR}/claude-news.service" \
    > /etc/systemd/system/claude-news.service
systemctl daemon-reload
systemctl enable claude-news.service
systemctl restart claude-news.service

echo "==> installing nginx HTTP config (port 80 only — for certbot)"
cat > /etc/nginx/sites-available/claude-news <<NGINX_HTTP
server {
    listen 80;
    server_name ${DOMAIN};
    location /.well-known/acme-challenge/ { root /var/www/html; }
    location / { return 200 'pending certbot\n'; add_header Content-Type text/plain; }
}
NGINX_HTTP

ln -sf /etc/nginx/sites-available/claude-news /etc/nginx/sites-enabled/claude-news
if grep -rl "server_name.*${DOMAIN}" /etc/nginx/sites-enabled/ 2>/dev/null | grep -v "/claude-news$" >/dev/null; then
    echo "WARN: another site already declares server_name ${DOMAIN}; you may have a conflict" >&2
fi
mkdir -p /var/www/html
nginx -t
systemctl reload nginx

echo "==> obtaining TLS certificate via certbot"
certbot --nginx \
    -d "${DOMAIN}" \
    --non-interactive \
    --agree-tos \
    -m "${ADMIN_EMAIL}" \
    --keep-until-expiring \
    --redirect || {
        echo "WARN: certbot failed — leaving HTTP-only config in place" >&2
    }

echo "==> installing final nginx config (HTTPS reverse proxy, port ${APP_PORT})"
if [[ -f "/etc/letsencrypt/live/${DOMAIN}/fullchain.pem" ]]; then
    sed "s|127.0.0.1:[0-9]\\+|127.0.0.1:${APP_PORT}|" "${SRC_DIR}/nginx.conf" \
        > /etc/nginx/sites-available/claude-news
    nginx -t
    systemctl reload nginx
fi

echo
echo "================================================================"
echo "Deploy complete. API_KEY: ${API_KEY}"
echo "Test: curl -H 'Authorization: Bearer ${API_KEY}' https://${DOMAIN}/health"
echo "================================================================"
