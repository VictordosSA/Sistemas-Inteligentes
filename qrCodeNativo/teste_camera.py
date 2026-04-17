import cv2
from pyzbar import pyzbar
from flask import Flask, render_template, jsonify
import threading
import time
import sys

app = Flask(__name__)

# Dados globais
dados_compartilhados = {
    "conteudo": "Aguardando leitura...",
    "timestamp": "-"
}

def rodar_camera():
    global dados_compartilhados
    print("[INFO] Tentando abrir a câmera...")
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("[ERRO] Câmera não detectada! Verifique se outra thread ou app está usando a câmera.")
        return

    print("[OK] Câmera iniciada com sucesso!")

    while True:
        ret, frame = cap.read()
        if not ret: break

        qrcodes = pyzbar.decode(frame)
        for qrcode in qrcodes:
            conteudo = qrcode.data.decode('utf-8')
            dados_compartilhados = {
                "conteudo": conteudo,
                "timestamp": time.strftime("%H:%M:%S")
            }
            print(f"[LEITURA] QR Code: {conteudo}")

        cv2.imshow("Preview Camera", frame)
        if cv2.waitKey(1) & 0xFF == 27: break

    cap.release()
    cv2.destroyAllWindows()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dados')
def enviar_dados():
    return jsonify(dados_compartilhados)

if __name__ == "__main__":
    print("[INFO] Iniciando sistema...")
    
    # Inicia a thread da câmera
    camera_thread = threading.Thread(target=rodar_camera, daemon=True)
    camera_thread.start()
    
    print("[INFO] Servidor Web iniciando em http://127.0.0.1:5000")
    # debug=False é melhor para evitar que o Windows bloqueie a porta
    app.run(host='127.0.0.1', port=5000, debug=False, threaded=True)