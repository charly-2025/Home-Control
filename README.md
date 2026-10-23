# Home Control

A self-hosted smart home platform: control Zigbee devices from a web dashboard
or **by voice**, fully locally, with no cloud service involved.

`FastAPI` · `React` · `MySQL` · `MQTT` · `Zigbee2MQTT` · `Home Assistant` · `Ollama` · `Whisper` · `Piper` · `Docker`

## Overview

Home Control brings together a custom web application and open source home
automation building blocks. Zigbee devices (smart plugs, roller shutters...)
are exposed through Zigbee2MQTT, driven by a FastAPI backend and displayed in
real time in a React dashboard. A local voice assistant turns spoken commands
into device actions with speech-to-text, a local LLM and text-to-speech.

## Features

- **Web dashboard** (React + Vite): devices, rooms, groups, account and settings pages
- **Real-time updates** through a WebSocket fed by MQTT
- **Device control API**: list devices, turn on / off, toggle, set state
- **Accounts and roles**: registration, login, JWT access and refresh tokens, admin user management
- **Voice assistant**: wake word detection, speech-to-text (Whisper), intent understanding with a local LLM (Ollama, Qwen 2.5), spoken answers (Piper)
- **Device agent**: a small client that listens to the microphone and streams commands to the assistant
- **Home Assistant** integration and automation blueprints
- Everything runs in Docker behind an nginx reverse proxy

## Architecture

```
                ┌──────────────┐
  Browser ────▶ │    nginx     │ ──▶ frontend (React)
                └──────┬───────┘
                       ▼
                 backend (FastAPI) ◀──▶ MySQL
                       │
                       ▼ MQTT (Mosquitto)
                 Zigbee2MQTT ◀──▶ Zigbee USB dongle ◀──▶ devices
                       ▲
  Microphone ─▶ device-agent ─▶ vocal-assistant ─▶ Whisper / Ollama / Piper
```

| Folder | Content |
| --- | --- |
| `backend/` | FastAPI API: auth, users, devices, WebSocket, MQTT client |
| `frontend/` | React dashboard |
| `vocal-assistant/` | Voice command API (LLM intent parsing, MQTT actions) |
| `device-agent/` | Microphone client with wake word detection |
| `zigbee/` | Zigbee2MQTT configuration template |
| `mqtt/` | Mosquitto configuration |
| `homeassistant/` | Home Assistant configuration and blueprints |
| `nginx/` | Reverse proxy |

## Getting started

Requirements: Docker, Docker Compose and a Zigbee coordinator (tested with a
Z-Stack USB dongle on `/dev/ttyUSB0`).

```bash
cp .env.example .env      # then fill in your own values
docker compose up -d --build
```

- Dashboard: `http://localhost`
- Home Assistant: `http://localhost:8123`
- Zigbee2MQTT frontend: `http://localhost:8080`

Zigbee network keys are generated on first start (`GENERATE` in
`zigbee/data/configuration.yaml`) and stay on your machine.

## Security notes

- No secret is committed: credentials live in `.env` (ignored by git).
- Runtime data (Zigbee keys, coordinator backups, Home Assistant database and
  logs) is ignored by git.

## License

MIT, see [LICENSE](LICENSE).
