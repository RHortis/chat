from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, emit
from datetime import datetime
import pandas as pd
import os
import sys

# Inicializa o Flask e SocketIO
app = Flask(__name__)
socketio = SocketIO(app)

# Define o arquivo CSV para armazenar as mensagens
CHAT_FILE = "C:/Users/Public/Documents/chat_leviosaaa.csv"

# Inicializa o arquivo de chat se não existir
try:
    chat_data = pd.read_csv(CHAT_FILE)
except FileNotFoundError:
    chat_data = pd.DataFrame(columns=["timestamp", "user", "message"])
    chat_data.to_csv(CHAT_FILE, index=False)

# Função para carregar o histórico de mensagens
def load_chat():
    try:
        return pd.read_csv(CHAT_FILE)
    except FileNotFoundError:
        socketio.stop()

# Rota principal
@app.route("/")
def index():
    chat_data = load_chat()
    return render_template("index_leviosaaa.html", chat_data=chat_data.to_dict(orient="records"))

# Rota para adicionar mensagens
@socketio.on("send_message")
def handle_message(data):
    username = data["user"]
    message = data["message"]
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    aux_timestamp = datetime.now().strftime("%Y_%m_%d__%H_%M_%S")
    #aux_timestamp = str(timestamp)
    #aux_timestamp = timestamp[6:]
    #aux_timestamp = aux_timestamp.replace("-","_")
    if  message.lower() == "clear":
        # Apaga o arquivo CSV
        chat_file = "C:/Users/Public/Documents/chat_leviosaaa.csv"
        if os.path.exists(chat_file):
            #os.remove(chat_file)
            novoNome = "C:/Users/Public/Documents/chat_leviosaaa_temp_" + aux_timestamp + ".csv"
            os.rename(chat_file,novoNome)
            chat_data = pd.DataFrame(columns=["timestamp", "user", "message"])
            chat_data.to_csv(CHAT_FILE, index=False)
            emit("reload_page", {"message": "Página será atualizada."}, broadcast=True) # Envia uma mensagem para o cliente pedir a atualização da página
        
    # Adiciona a nova mensagem ao arquivo
    new_message = pd.DataFrame([{
        "timestamp": timestamp,
        "user": username,
        "message": message,        
    }])
    
    if message.lower() == "clear":
        pass
    else:        
        chat_data = pd.concat([load_chat(), new_message], ignore_index=True)
        chat_data.to_csv(CHAT_FILE, index=False)

    # Emite a mensagem para todos os clientes conectados
    emit("receive_message", {"user": username, "message": message, "timestamp": timestamp}, broadcast=True)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5934, debug=True)