# Physics Wallah (PW) — Without Purchase TXT Extractor

A Telegram bot that extracts **Physics Wallah** batch content (videos, notes,
DPP videos, DPP notes) from your purchased or legacy PW batches on
[pw.live](https://www.pw.live) / `api.penpencil.co` and ships them back as a
`.txt`, `.zip`, and `.json`.

> This build is **PW-only**. All ClassPlus (CP) and Appx code paths have been
> removed.

## Features

- Login with Phone + OTP **or** a pre-existing PW access token
- Search your purchased batches by name
- Three download modes:
  1. **Full Batch** — every subject, chapter, videos, notes, DPP videos, DPP notes
  2. **Today's Class** — today's live schedule
  3. **Khazana** — purchased PW Khazana library (best-effort)
- Robust extraction — videos (with correct `parentId`/`childId`/`videoId`
  attached for PW CDN playback), lecture PDFs, top-level attachments, DPP PDFs
  and DPP videos, exercise sheets
- Falls back from `v2` → `v3` of the batches `topics` and `contents` endpoints
  for newer batches
- Flask keep-alive on `$PORT` (default `8000`) for Render / Koyeb healthchecks

## Config

Fill your Telegram `api_id`, `api_hash`, `bot_token`, and the authorized user
id in `config.py`:

```python
api_id = 12345678
api_hash = "..."
bot_token = "..."
auth_users = [YOUR_TELEGRAM_USER_ID]
```

These can also be overridden at runtime via environment variables
`API_ID`, `API_HASH`, and `BOT_TOKEN`.

## Run on a Linux VPS / Docker / Render / Koyeb

```bash
pip install -r requirements.txt
python main.py
```

For Koyeb, expose port `8080` in `main.py` (the Flask keep-alive uses the
`PORT` env var; set it to `8080` in Koyeb).

## Run on Termux (Android)

The dependencies have been pared down so the bot runs cleanly on Termux.

```bash
pkg update && pkg upgrade -y
pkg install -y python git libjpeg-turbo libcrypt openssl
git clone https://github.com/msbro-rmw/pw-without.git
cd pw-without
pip install --upgrade pip wheel
pip install -r requirements.txt
python main.py
```

If `tgcrypto` fails to compile, install it separately with:

```bash
pip install tgcrypto --no-binary :all:
```

## Deploy To Heroku

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/)

## Deploy To Koyeb

[![Deploy to Koyeb](https://www.koyeb.com/static/images/deploy/button.svg)](https://app.koyeb.com/deploy?name=pw-without&repository=msbro-rmw%2Fpw-without&branch=main&builder=dockerfile&instance_type=free&instances_min=0&autoscaling_sleep_idle_delay=300&ports=8080%3Bhttp%3B%2F&hc_protocol%5B8080%5D=tcp&hc_grace_period%5B8080%5D=5&hc_interval%5B8080%5D=30&hc_restart_limit%5B8080%5D=3&hc_timeout%5B8080%5D=5&hc_path%5B8080%5D=%2F&hc_method%5B8080%5D=get)

## Deploy To Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/msbro-rmw/pw-without)
