from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, emit
from datetime import datetime
import pandas as pd

# Inicializa o Flask e SocketIO
app = Flask(__name__)
socketio = SocketIO(app)

# Define o arquivo CSV para armazenar as mensagens
CHAT_FILE = "chat_harley.csv"

# Inicializa o arquivo de chat se não existir
try:
    chat_data = pd.read_csv(CHAT_FILE)
except FileNotFoundError:
    chat_data = pd.DataFrame(columns=["timestamp", "user", "message"])
    chat_data.to_csv(CHAT_FILE, index=False)

# Função para carregar o histórico de mensagens
def load_chat():
    return pd.read_csv(CHAT_FILE)

# Rota principal
@app.route("/")
def index():
    chat_data = load_chat()
    return render_template("index_harley.html", chat_data=chat_data.to_dict(orient="records"))

# Rota para adicionar mensagens
@socketio.on("send_message")
def handle_message(data):
    username = data["user"]
    message = data["message"]
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Adiciona a nova mensagem ao arquivo
    new_message = pd.DataFrame([{
        "timestamp": timestamp,
        "user": username,
        "message": message,
    }])
    chat_data = pd.concat([load_chat(), new_message], ignore_index=True)
    chat_data.to_csv(CHAT_FILE, index=False)

    # Emite a mensagem para todos os clientes conectados
    emit("receive_message", {"user": username, "message": message, "timestamp": timestamp}, broadcast=True)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5002, debug=True)