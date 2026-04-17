import cv2
import sys
import time
import threading
try:
    from flask import Flask, render_template, jsonify, Response
except ModuleNotFoundError as e:
    print("[ERRO] Módulo Flask não instalado:", e)
    print("Instale com: /usr/local/bin/python3 -m pip install Flask")
    raise SystemExit(1)

# Tenta usar pyzbar; se falhar, fallback para OpenCV QRCodeDetector
use_pyzbar = False
try:
    from pyzbar import pyzbar  # optional native dependency (requires zbar)
    use_pyzbar = True
except Exception as e:
    print("[WARN] pyzbar não inicializou:", e)
    print("Dica: instale zbar (Homebrew): brew install zbar")
    print("Usando detector nativo do OpenCV como fallback (não precisa de zbar).")

app = Flask(__name__)

# Dados globais
dados_compartilhados = {
    "conteudo": "Aguardando leitura...",
    "timestamp": "-"
}
dados_lock = threading.Lock()

# Armazenar último frame para o stream
latest_frame = None
frame_lock = threading.Lock()

# Instância do detector OpenCV (usada no fallback)
_cv_detector = cv2.QRCodeDetector()

def decode_qrcodes(frame):
    decoded = []
    if use_pyzbar:
        qrcodes = pyzbar.decode(frame)
        for q in qrcodes:
            try:
                decoded.append(q.data.decode('utf-8'))
            except Exception:
                pass
    else:
        if hasattr(_cv_detector, "detectAndDecodeMulti"):
            ok, decoded_info, points, _ = _cv_detector.detectAndDecodeMulti(frame)
            if ok and decoded_info:
                for txt in decoded_info:
                    if txt:
                        decoded.append(txt)
        else:
            txt, points = _cv_detector.detectAndDecode(frame)[0:2]
            if txt:
                decoded.append(txt)
    return decoded

def rodar_camera():
    global dados_compartilhados, latest_frame
    print("[INFO] Tentando abrir a câmera...")

    # No macOS é mais confiável usar o backend AVFoundation
    if sys.platform == "darwin":
        cap = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)
    else:
        cap = cv2.VideoCapture(0)

    # Ajustar resolução (opcional)
    try:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    except Exception:
        pass

    if not cap.isOpened():
        print("[ERRO] Câmera não detectada! Verifique se outra app está usando a câmera.")
        print("[DICA] No macOS: conceda permissão em System Settings → Privacy & Security → Camera")
        return

    print("[OK] Câmera iniciada com sucesso!")

    while True:
        ret, frame = cap.read()
        if not ret:
            time.sleep(0.1)
            continue

        # atualiza frame para o stream
        with frame_lock:
            latest_frame = frame.copy()

        textos = decode_qrcodes(frame)
        for conteudo in textos:
            with dados_lock:
                dados_compartilhados = {
                    "conteudo": conteudo,
                    "timestamp": time.strftime("%H:%M:%S")
                }
            print(f"[LEITURA] QR Code: {conteudo}")

        time.sleep(0.01)

    cap.release()
    cv2.destroyAllWindows()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    def gen():
        while True:
            with frame_lock:
                frame = None if latest_frame is None else latest_frame.copy()
            if frame is None:
                time.sleep(0.05)
                continue
            ret, jpeg = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
            if not ret:
                continue
            frame_bytes = jpeg.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            time.sleep(0.03)
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/dados')
def enviar_dados():
    with dados_lock:
        return jsonify(dados_compartilhados)

if __name__ == "__main__":
    print("[INFO] Iniciando sistema...")

    if sys.platform == "darwin":
        print("[NOTICE] macOS detectado. Se usar pyzbar, instale zbar: brew install zbar")

    # Inicia a thread da câmera
    camera_thread = threading.Thread(target=rodar_camera, daemon=True)
    camera_thread.start()

    print("[INFO] Servidor Web iniciando em http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=False, threaded=True, use_reloader=False)

# Para instalação de dependências (executar no terminal, fora do Python):
# /usr/local/bin/python3 -m pip install --upgrade pip setuptools wheel
# /usr/local/bin/python3 -m pip install Flask
# se precisar de OpenCV/pyzbar também:
#/usr/local/bin/python3 -m pip install opencv-python pyzbar
# instale zbar nativo (se usar pyzbar)
# brew install zbar
# /usr/local/bin/python3 -c "import flask; print('Flask ok', flask.__version__)"