# Adam — Asistente de Voz

Asistente virtual en español con interfaz web y reconocimiento de voz. Escucha comandos de voz o texto y responde con voz natural usando voces neurales de Microsoft Edge.

## Características

- Reconocimiento de voz en español (Web Speech API en navegador)
- Respuestas con voz neural (Edge-TTS, voz Elvira)
- Interfaz web moderna con visualización de onda de audio
- Chat interactivo con seguimiento de contexto
- Desplegado en Render via Docker

## Comandos disponibles

| Comando | Descripción |
|---------|-------------|
| `abre youtube` | Abre YouTube en nueva pestaña |
| `abre google` | Abre el navegador |
| `qué hora es` | Dice la hora actual |
| `qué día es` | Dice el día y fecha |
| `busca en Wikipedia` | Busca en Wikipedia (pregunta qué) |
| `busca en internet` | Busca en Google (pregunta qué) |
| `reproduce` | Busca música en YouTube (pregunta qué) |
| `chiste` | Cuenta un chiste |
| `precio de acciones` | Consulta precio (pregunta cuál) |
| `ayuda` | Lista todos los comandos |

## Instalación

### Requisitos

- Python 3.11+
- pip

### Pasos

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/asistente.git
cd asistente

# Crear entorno virtual (Windows)
python -m venv .venv
.venv\Scripts\activate

# Crear entorno virtual (Linux/Mac)
python3 -m venv .venv
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

## Ejecución

### Modo web (recomendado)

```bash
python -m asistente.server
```

Abre http://localhost:5000 en tu navegador. Usa el micrófono o escribe comandos.

### Modo CLI

```bash
python -m asistente
```

Habla directamente al micrófono. Di "Adam" para activar.

## Despliegue en Render

1. Sube el código a GitHub
2. En Render, crea un nuevo **Web Service**
3. Conecta tu repositorio de GitHub
4. Selecciona **Docker** como runtime
5. Render usará `render.yaml` automáticamente

La app estará disponible en `https://tu-app.onrender.com`

## Arquitectura

```
asistente/
├── __main__.py        # Entry point CLI
├── main.py            # Lógica principal CLI
├── server.py          # Flask API + sirve frontend
├── comandos.py        # Procesamiento de comandos (CLI + API)
├── audio.py           # TTS: edge-tts → gTTS → pyttsx3
├── config.py          # Configuración
└── utilidades.py      # Utilidades (hora, fecha)

frontend/
├── index.html         # Interfaz web
├── styles.css         # Estilos (tema Resonance)
└── app.js             # Lógica frontend + Web Speech API
```

## Tecnologías

- **Backend**: Python, Flask, edge-tts, SpeechRecognition
- **Frontend**: HTML, CSS, JavaScript, Web Speech API
- **Despliegue**: Docker, Render
