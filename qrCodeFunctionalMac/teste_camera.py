import cv2
import sys
import os
import time
import threading

try:
    from flask import Flask, render_template, jsonify, Response, request
except ModuleNotFoundError as e:
    print("[ERRO] Módulo Flask não instalado:", e)
    print("Instale com: /usr/local/bin/python3 -m pip install Flask")
    raise SystemExit(1)

app = Flask(__name__)

# =========================
# MYSQL
# =========================
try:
    import mysql.connector
except ModuleNotFoundError:
    mysql = None
    print("[WARN] mysql-connector-python não instalado.")
    print("Instale com: python3 -m pip install mysql-connector-python")

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "127.0.0.1"),
    "port": int(os.environ.get("DB_PORT", 3306)),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", ""),
    "database": os.environ.get("DB_NAME", "centro_logistica"),
}

# =========================
# REGIÕES
# =========================
REGIOES_BR = {
    "SP": "São Paulo",
    "RJ": "Rio de Janeiro",
    "MG": "Minas Gerais",
    "ES": "Espírito Santo",

    "RS": "Rio Grande do Sul",
    "SC": "Santa Catarina",
    "PR": "Paraná",

    "BA": "Bahia",
    "PE": "Pernambuco",
    "CE": "Ceará",

    "NORTE": "Região Norte",
    "NORDESTE": "Região Nordeste",
    "CENTRO-OESTE": "Região Centro-Oeste",
    "SUDESTE": "Região Sudeste",
    "SUL": "Região Sul"
}

FALLBACK_REGIAO = {
    "123.456.789-00": "Norte",
    "234.567.890-11": "Nordeste",
    "345.678.901-22": "Centro-Oeste",
    "456.789.012-33": "Sudeste",
    "567.890.123-44": "Sul",
    "12.345.678/0001-99": "Centro-Oeste",
    "Porto Velho": "Norte",
    "Salvador": "Nordeste",
    "Cuiabá": "Centro-Oeste",
    "São Paulo": "Sudeste",
    "Sao Paulo": "Sudeste",
    "Curitiba": "Sul",
    "Batel": "Sul",
}

# =========================
# DADOS GLOBAIS
# =========================
dados_compartilhados = {
    "conteudo": "Aguardando leitura...",
    "tipo": "-",
    "regiao": "-",
    "timestamp": "-",
    "status": "aguardando",
    "informacoes": {}
}

dados_lock = threading.Lock()

latest_frame = None
frame_lock = threading.Lock()

camera_index = int(os.environ.get("CAMERA_INDEX", 0))
camera_lock = threading.Lock()
camera_thread_running = True

current_cap = None

# =========================
# OPEN CV QR DETECTOR
# =========================
_cv_detector = cv2.QRCodeDetector()

# =========================
# CONFIGURAÇÕES DE CÂMERA
# =========================
camera_settings_data = {
    "brightness": 60,
    "contrast": 40,
    "saturation": 80,
    "exposure": -5,
    "gain": 50,
    "auto_exposure": True
}

settings_lock = threading.Lock()

# =========================
# FUNÇÕES AUXILIARES
# =========================
def detectar_regiao(texto):

    texto_upper = texto.upper()

    for sigla, nome in REGIOES_BR.items():
        if sigla.upper() in texto_upper:
            return nome

    return "Região não identificada"


def conectar_db():

    if mysql is None:
        return None

    try:
        return mysql.connector.connect(**DB_CONFIG)

    except Exception as e:
        print(f"[WARN] Não foi possível conectar ao banco: {e}")
        return None


def _normalize_text(text):
    return text.strip().lower() if isinstance(text, str) else ""


# =========================
# BUSCA INFORMAÇÕES
# =========================
def buscar_informacoes_por_qrcode(conteudo):

    if not conteudo:
        return {
            "tipo": "desconhecido",
            "regiao": None,
            "informacoes": {}
        }

    texto = conteudo.strip()

    regiao_detectada = detectar_regiao(texto)

    conn = conectar_db()

    if conn:

        cursor = None

        try:

            cursor = conn.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT c.nome_cli, c.cpf_cli, c.email_cli,
                       c.telefone_cli, l.regiao_loc,
                       l.cidade_loc, l.estado_loc
                FROM cliente c
                JOIN localidade l ON c.id_loc_fk = l.id_loc
                WHERE c.cpf_cli = %s
                   OR c.email_cli = %s
                   OR c.nome_cli = %s
                LIMIT 1
                """,
                (texto, texto, texto)
            )

            row = cursor.fetchone()

            if row:

                return {
                    "tipo": "Cliente",
                    "regiao": row.get("regiao_loc") or regiao_detectada,
                    "informacoes": {
                        "nome": row.get("nome_cli"),
                        "cpf": row.get("cpf_cli"),
                        "email": row.get("email_cli"),
                        "telefone": row.get("telefone_cli"),
                        "cidade": row.get("cidade_loc"),
                        "estado": row.get("estado_loc")
                    }
                }

        except Exception as e:
            print(f"[WARN] Erro banco: {e}")

        finally:

            if cursor:
                cursor.close()

            conn.close()

    chave = _normalize_text(texto)

    for chave_esperada, regiao in FALLBACK_REGIAO.items():

        if chave == _normalize_text(chave_esperada):

            return {
                "tipo": "Fallback",
                "regiao": regiao,
                "informacoes": {
                    "valor_lido": texto
                }
            }

    return {
        "tipo": "QRCode",
        "regiao": regiao_detectada,
        "informacoes": {
            "valor_lido": texto
        }
    }

# =========================
# MELHORIA DE FRAME
# =========================
def processar_frame(frame):

    if frame is None:
        return frame

    try:

        frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        h, s, v = cv2.split(frame_hsv)

        if v.mean() < 80:

            v = cv2.add(v, 40)

            frame_hsv = cv2.merge([h, s, v])

            frame = cv2.cvtColor(frame_hsv, cv2.COLOR_HSV2BGR)

        return frame

    except:
        return frame

# =========================
# OPENCV QR READER
# =========================
def decode_qrcodes(frame):

    decoded = []

    try:

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

    except Exception as e:
        print("[WARN] Erro ao detectar QRCode:", e)

    return decoded

# =========================
# OTIMIZA CÂMERA
# =========================
def otimizar_camera(cap):

    try:

        with settings_lock:
            settings = camera_settings_data.copy()

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)

        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        try:
            cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)
        except:
            pass

        try:
            cap.set(cv2.CAP_PROP_AUTO_WB, 1)
        except:
            pass

        print("[OK] Câmera otimizada")

    except Exception as e:
        print("[WARN] Erro ao otimizar câmera:", e)

# =========================
# LISTAR CÂMERAS
# =========================
def listar_cameras_disponiveis():

    cameras = []

    for i in range(5):

        cap = cv2.VideoCapture(i)

        if cap.isOpened():

            cameras.append({
                "indice": i,
                "nome": f"Câmera {i}"
            })

            cap.release()

    return cameras

# =========================
# THREAD CÂMERA
# =========================
def rodar_camera():

    global latest_frame
    global dados_compartilhados
    global current_cap
    global camera_index

    print("[INFO] Iniciando câmera...")

    ultimo_indice = -1

    while camera_thread_running:

        if ultimo_indice != camera_index:

            if current_cap:
                current_cap.release()

            print(f"[INFO] Abrindo câmera {camera_index}")

            current_cap = cv2.VideoCapture(camera_index)

            otimizar_camera(current_cap)

            ultimo_indice = camera_index

            time.sleep(1)

        if current_cap is None or not current_cap.isOpened():

            print("[WARN] Câmera não disponível")
            time.sleep(1)
            continue

        ret, frame = current_cap.read()

        if not ret or frame is None:

            print("[WARN] Falha ao capturar frame")
            time.sleep(0.1)
            continue

        frame = processar_frame(frame)

        textos = decode_qrcodes(frame)

        for conteudo in textos:

            info = buscar_informacoes_por_qrcode(conteudo)

            cv2.putText(
    frame,
    f"{info.get('regiao')}",
    (20, 40),
    cv2.FONT_HERSHEY_SIMPLEX,
    1,
    (0, 255, 0),
    2
)              

            with dados_lock:

                dados_compartilhados = {
                    "conteudo": conteudo,
                    "tipo": info.get("tipo"),
                    "regiao": info.get("regiao"),
                    "timestamp": time.strftime("%H:%M:%S"),
                    "status": "encontrado",
                    "informacoes": info.get("informacoes")
                }

            print(f"[QR] {conteudo}")
            print(f"[REGIÃO] {info.get('regiao')}")
            print("-" * 30)

        with frame_lock:
            latest_frame = frame.copy()

        time.sleep(0.01)

    if current_cap:
        current_cap.release()

# =========================
# FLASK
# =========================
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/dados')
def enviar_dados():

    with dados_lock:
        return jsonify(dados_compartilhados)


@app.route('/cameras')
def cameras():

    global camera_index

    cameras_list = listar_cameras_disponiveis()

    return jsonify({
        "cameras": cameras_list,
        "camera_atual": camera_index
    })


@app.route('/set_camera/<int:index>', methods=['POST'])
def set_camera(index):

    global camera_index

    with camera_lock:
        camera_index = index

    print(f"[INFO] Câmera alterada para {index}")

    return jsonify({
        "sucesso": True,
        "camera_atual": index
    })


@app.route('/video_feed')
def video_feed():

    def gen():

        global latest_frame

        while True:

            try:

                with frame_lock:

                    if latest_frame is None:
                        frame = None
                    else:
                        frame = latest_frame.copy()

                if frame is None:

                    time.sleep(0.05)
                    continue

                ret, jpeg = cv2.imencode(
                    '.jpg',
                    frame,
                    [int(cv2.IMWRITE_JPEG_QUALITY), 80]
                )

                if not ret:
                    continue

                frame_bytes = jpeg.tobytes()

                yield (
                    b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' +
                    frame_bytes +
                    b'\r\n'
                )

                time.sleep(0.03)

            except GeneratorExit:
                break

            except Exception as e:

                print("[ERRO STREAM]", e)
                time.sleep(0.1)

    return Response(
        gen(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

# =========================
# CAMERA SETTINGS
# =========================
@app.route('/camera_settings', methods=['GET', 'POST'])
def camera_settings():

    global current_cap

    if request.method == 'GET':

        with settings_lock:
            return jsonify(camera_settings_data)

    data = request.get_json()

    with settings_lock:

        camera_settings_data.update(data)

    try:

        if current_cap and current_cap.isOpened():

            current_cap.set(
                cv2.CAP_PROP_BRIGHTNESS,
                float(data.get("brightness", 60)) / 100
            )

            current_cap.set(
                cv2.CAP_PROP_CONTRAST,
                float(data.get("contrast", 40)) / 100
            )

            current_cap.set(
                cv2.CAP_PROP_SATURATION,
                float(data.get("saturation", 80)) / 100
            )

            current_cap.set(
                cv2.CAP_PROP_GAIN,
                float(data.get("gain", 50)) / 100
            )

            auto_exposure = data.get("auto_exposure", True)

            if auto_exposure:
                current_cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.75)
            else:
                current_cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)
                current_cap.set(
                    cv2.CAP_PROP_EXPOSURE,
                    float(data.get("exposure", -5))
                )

    except Exception as e:
        print("[WARN] Erro ao aplicar configurações:", e)

    return jsonify({
        "sucesso": True
    })

# =========================
# MAIN
# =========================
if __name__ == "__main__":

    print("[INFO] Sistema iniciado usando OpenCV QRCodeDetector")

    camera_thread = threading.Thread(
        target=rodar_camera,
        daemon=True
    )

    camera_thread.start()

    print("[INFO] Servidor iniciado em:")
    print("http://127.0.0.1:5000")
    print("http://SEU_IP_LOCAL:5000")

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        threaded=True,
        use_reloader=False
    )

# =========================
# INSTALAÇÃO
# =========================
# python3 -m pip install Flask
# python3 -m pip install opencv-python
# python3 -m pip install mysql-connector-python