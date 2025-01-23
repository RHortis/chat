from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, emit
from datetime import datetime
import pandas as pd
import os
import sys

# Inicializa o Flask e SocketIO
app = Flask(__name__)
socketio = SocketIO(app)

# Lista para armazenar as mensagens temporariamente (em memória)
chat_data = []

# Função para carregar o histórico de mensagens
def load_chat():
    return chat_data

# Rota principal
@app.route("/")
def index():
    return render_template("index_hortis.html", chat_data=load_chat())

# Rota para adicionar mensagens
@socketio.on("send_message")
def handle_message(data):
    username = data["user"]
    message = data["message"]
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Adiciona a nova mensagem à lista (em memória)
    new_message = {
        "timestamp": timestamp,
        "user": username,
        "message": message
    }
    chat_data.append(new_message)

    # Se a mensagem for "clear", esvazia a lista
    if message.lower() == "clear":
        chat_data.clear()

    # Emite a mensagem para todos os clientes conectados
    emit("receive_message", {"user": username, "message": message, "timestamp": timestamp}, broadcast=True)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
