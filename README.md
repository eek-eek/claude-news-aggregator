# Claude News Aggregator

RSS aggregator that polls ~85 feeds across 5 categories (AI, finance, fintech/banking, cybersec, IT leadership) and exposes a bearer-protected JSON API.

## Deploy

```bash
git clone https://github.com/eek-eek/claude-news-aggregator.git
cd claude-news-aggregator
sudo bash deploy.sh
```

The script installs packages, creates `claude-news` user, builds venv, generates API key, installs systemd unit, configures nginx + Let's Encrypt. Final output prints the API key and a test curl.

Override port if 18327 is taken: `APP_PORT=18999 sudo -E bash deploy.sh`.

## API

All endpoints require `Authorization: Bearer <KEY>` except `/health`.

- `GET /health` — liveness
- `GET /news?category=&hours_back=&source=&query=&limit=` — filtered items
- `GET /sources` — per-feed status
- `POST /refresh` — sync force-refresh

## Ops

- Logs: `journalctl -u claude-news -f`
- Service: `systemctl {status,restart} claude-news`
- DB: `/var/lib/claude-news/db.sqlite`
- API key: `/etc/claude-news/env`
- Refresh: every 20 min
