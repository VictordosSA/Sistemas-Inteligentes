from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import cv2
import numpy as np
from pyzbar.pyzbar import decode
import base64
from collections import defaultdict

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Contador para dashboard
contador_regioes = defaultdict(int)

REGIOES = [
    "NORTE",
    "SUL",
    "NORDESTE",
    "SUDESTE",
    "CENTRO-OESTE",
    "CENTRO OESTE"
]

def detectar_regiao(texto):
    texto = texto.upper()
    for r in REGIOES:
        if r in texto:
            return r
    return "OUTROS"

@app.route("/")
def index():
    return render_template("realtime_ws.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@socketio.on("frame")
def processar_frame(data):
    try:
        encoded_data = data.split(",")[1]
        img_bytes = base64.b64decode(encoded_data)

        np_arr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        decoded_objs = decode(img)

        if not decoded_objs:
            return  # 🔥 NÃO envia nada (economia de rede)

        for obj in decoded_objs:
            dados = obj.data.decode("utf-8")
            regiao = detectar_regiao(dados)

            contador_regioes[regiao] += 1

            x, y, w, h = obj.rect
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 3)
            cv2.putText(img, regiao, (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                        (0, 255, 0), 2)

            _, buffer = cv2.imencode('.jpg', img)
            img_base64 = base64.b64encode(buffer).decode('utf-8')

            emit("resultado", {
                "resultado": dados,
                "regiao": regiao,
                "imagem": f"data:image/jpeg;base64,{img_base64}"
            })

            # Atualiza dashboard
            emit("dashboard", contador_regioes, broadcast=True)

    except Exception as e:
        print("Erro:", e)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)