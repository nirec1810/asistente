# AGENTS.md

## Project

Voice assistant "Adam" (v2.0.0). Spanish-language app with Flask web server and static HTML frontend. Deployed on Render via Docker.

## Structure

- `asistente/` — Python package. Entry: `asistente/__main__.py` → `asistente/main.py:initiar()`
- `asistente/server.py` — Flask web API (port from `$PORT` or 5000). Serves frontend from `../frontend/`
- `asistente/comandos.py` — Command logic. Has dual functions: `_funcion()` for CLI (calls `hablar()`), `_funcion_api()` for web (returns strings)
- `asistente/audio.py` — TTS engines. Primary: edge-tts (Elvira). Fallbacks: gTTS → pyttsx3. Voice input via SpeechRecognition
- `frontend/` — Static HTML/CSS/JS. Uses Web Speech API for voice I/O (browser-side, not server)
- `render.yaml` + `Dockerfile` — Render deployment config

## Running

```bash
# Local CLI (needs mic, Windows venv)
.venv\Scripts\activate
python -m asistente

# Local web server
pip install flask flask-cors edge-tts
python -m asistente.server
# Open http://localhost:5000

# Docker
docker build -t adam .
docker run -p 5000:5000 adam
```

## Architecture

Two runtimes share `comandos.py`:
- **CLI** (`python -m asistente`): mic input → `hablar()` audio output
- **Web** (`python -m asistente.server`): HTTP JSON → `hablar()` on server + frontend Web Speech API

The web server does NOT call `hablar()` for API responses — audio plays via browser SpeechSynthesis. Server-side `hablar()` only runs if explicitly called.

## Gotchas

- **System audio deps**: `pyaudio`, `pyttsx3`, `portaudio19-dev` need system-level libs. Dockerfile installs them.
- **TTS priority**: edge-tts → gTTS → pyttsx3. Requires `pygame.mixer.init()` at module load (not conditional on gTTS).
- **Edge-TTS voice**: `es-ES-ElviraNeural` (config in `audio.py:VOZ_EDGE`). Change there to swap voices.
- **`comandos.py` duplication**: Every command function exists in two forms — `_funcion()` and `_funcion_api()`. When adding commands, update BOTH plus the respective COMANDOS/COMANDOS_API lists.
- **`utilidades.py` bug**: `obtener_hora_actual()` uses `ahora.minute` not `ahora.minuto`. Don't regress.
- **Language**: All user-facing strings are Spanish. Commands match Spanish phrases in `comandos.py`.
- **No tests, no linter, no typecheck**: repo has none configured.
