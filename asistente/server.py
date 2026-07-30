import logging
import os

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

from asistente.comandos import procesar_comando_api
from asistente.config import NOMBRE_ASISTENTE

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)

logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder="../frontend", static_url_path="")
CORS(app)

conversations = {}


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/status", methods=["GET"])
def status():
    return jsonify({
        "status": "ready",
        "name": NOMBRE_ASISTENTE,
        "version": "2.0.0"
    })


@app.route("/api/command", methods=["POST"])
def command():
    data = request.get_json()
    if not data or "command" not in data:
        return jsonify({"error": "Se requiere campo 'command'"}), 400

    user_command = data["command"].strip()
    if not user_command:
        return jsonify({"error": "Comando vacío"}), 400

    logger.info("Comando recibido: %s", user_command)

    response_text, state, context = procesar_comando_api(user_command)

    if context:
        conversations[context] = {"active": True}

    logger.info("Respuesta: %s (state=%s)", response_text, state)

    return jsonify({
        "response": response_text,
        "state": state,
        "context": context
    })


@app.route("/api/respond", methods=["POST"])
def respond():
    data = request.get_json()
    if not data or "response" not in data or "context" not in data:
        return jsonify({"error": "Se requieren campos 'response' y 'context'"}), 400

    user_response = data["response"].strip()
    context = data["context"]

    if not user_response:
        return jsonify({"error": "Respuesta vacía"}), 400

    if context not in conversations or not conversations[context].get("active"):
        return jsonify({"error": "Contexto de conversación no válido o expirado"}), 400

    logger.info("Respuesta de seguimiento: %s (context=%s)", user_response, context)

    response_text, state, _ = procesar_comando_api(user_response, context)

    if state == "complete":
        conversations.pop(context, None)
    else:
        conversations[context]["active"] = True

    logger.info("Respuesta: %s (state=%s)", response_text, state)

    return jsonify({
        "response": response_text,
        "state": state,
        "context": context if state != "complete" else None
    })


def run_server(host="0.0.0.0", port=None):
    if port is None:
        port = int(os.environ.get("PORT", 5000))
    logger.info("Iniciando servidor en %s:%s", host, port)
    app.run(host=host, port=port, debug=False)


if __name__ == "__main__":
    run_server()
