import cv2
import sys
import os
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

# Configuração opcional de banco de dados MySQL/MariaDB
try:
    import mysql.connector
except ModuleNotFoundError:
    mysql = None
    print("[WARN] mysql-connector-python não instalado. Instale com: python3 -m pip install mysql-connector-python")

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "127.0.0.1"),
    "port": int(os.environ.get("DB_PORT", 3306)),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", ""),
    "database": os.environ.get("DB_NAME", "centro_logistica"),
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

# Dados globais
dados_compartilhados = {
    "conteudo": "Aguardando leitura...",
    "tipo": "-",
    "regiao": "-",
    "timestamp": "-",
    "status": "aguardando",
    "informacoes": {}
}
dados_lock = threading.Lock()

# Armazenar último frame para o stream
latest_frame = None
frame_lock = threading.Lock()

# Instância do detector OpenCV (usada no fallback)
_cv_detector = cv2.QRCodeDetector()

def conectar_db():
    if mysql is None:
        return None
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Exception as e:
        print(f"[WARN] Não foi possível conectar ao banco MySQL: {e}")
        return None


def _normalize_text(text):
    return text.strip().lower() if isinstance(text, str) else ""


def buscar_informacoes_por_qrcode(conteudo):
    """Busca todas as informações disponíveis para um QR Code."""
    if not conteudo:
        return {
            "tipo": "desconhecido",
            "regiao": None,
            "informacoes": {}
        }

    texto = conteudo.strip()
    conn = conectar_db()
    
    # Tenta buscar em Cliente
    if conn:
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT c.nome_cli, c.cpf_cli, c.email_cli, c.telefone_cli, l.regiao_loc, l.cidade_loc, l.estado_loc, l.bairro_loc, l.cep_loc
                FROM cliente c
                JOIN localidade l ON c.id_loc_fk = l.id_loc
                WHERE c.cpf_cli = %s OR c.email_cli = %s OR c.nome_cli = %s
                LIMIT 1
                """,
                (texto, texto, texto)
            )
            row = cursor.fetchone()
            if row:
                return {
                    "tipo": "Cliente",
                    "regiao": row.get("regiao_loc"),
                    "informacoes": {
                        "nome": row.get("nome_cli"),
                        "cpf": row.get("cpf_cli"),
                        "email": row.get("email_cli"),
                        "telefone": row.get("telefone_cli"),
                        "cidade": row.get("cidade_loc"),
                        "estado": row.get("estado_loc"),
                        "bairro": row.get("bairro_loc"),
                        "cep": row.get("cep_loc")
                    }
                }

            # Tenta buscar em Distribuidora
            cursor.execute(
                """
                SELECT d.nome_dist, d.cnpj_dist, d.email_dist, d.telefone_dist, d.capacidade_dist, l.regiao_loc, l.cidade_loc, l.estado_loc, l.bairro_loc, l.cep_loc
                FROM distribuidora d
                JOIN localidade l ON d.id_loc_fk = l.id_loc
                WHERE d.cnpj_dist = %s OR d.email_dist = %s OR d.nome_dist = %s
                LIMIT 1
                """,
                (texto, texto, texto)
            )
            row = cursor.fetchone()
            if row:
                return {
                    "tipo": "Distribuidora",
                    "regiao": row.get("regiao_loc"),
                    "informacoes": {
                        "nome": row.get("nome_dist"),
                        "cnpj": row.get("cnpj_dist"),
                        "email": row.get("email_dist"),
                        "telefone": row.get("telefone_dist"),
                        "capacidade": f"{row.get('capacidade_dist', 0):.0f} kg",
                        "cidade": row.get("cidade_loc"),
                        "estado": row.get("estado_loc"),
                        "bairro": row.get("bairro_loc"),
                        "cep": row.get("cep_loc")
                    }
                }

            # Tenta buscar em Localidade
            cursor.execute(
                """
                SELECT regiao_loc, cidade_loc, estado_loc, pais_loc, bairro_loc, cep_loc, numero_loc, complemento_loc, ponto_refer_loc
                FROM localidade
                WHERE cep_loc = %s OR cidade_loc = %s OR bairro_loc = %s OR ponto_refer_loc = %s OR complemento_loc = %s
                LIMIT 1
                """,
                (texto, texto, texto, texto, texto)
            )
            row = cursor.fetchone()
            if row:
                return {
                    "tipo": "Localidade",
                    "regiao": row.get("regiao_loc"),
                    "informacoes": {
                        "cidade": row.get("cidade_loc"),
                        "estado": row.get("estado_loc"),
                        "bairro": row.get("bairro_loc"),
                        "cep": row.get("cep_loc"),
                        "pais": row.get("pais_loc"),
                        "numero": row.get("numero_loc"),
                        "complemento": row.get("complemento_loc"),
                        "ponto_referencia": row.get("ponto_refer_loc")
                    }
                }

        except Exception as e:
            print(f"[WARN] Erro ao buscar informações no banco de dados: {e}")
        finally:
            if cursor is not None:
                try:
                    cursor.close()
                except Exception:
                    pass
            try:
                conn.close()
            except Exception:
                pass

    # Fallback com as informações mapeadas localmente
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
        "tipo": "desconhecido",
        "regiao": None,
        "informacoes": {}
    }

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
            info = buscar_informacoes_por_qrcode(conteudo)
            with dados_lock:
                dados_compartilhados = {
                    "conteudo": conteudo,
                    "tipo": info.get("tipo"),
                    "regiao": info.get("regiao") or "Não encontrada",
                    "timestamp": time.strftime("%H:%M:%S"),
                    "status": "encontrado" if info.get("regiao") else "não encontrado",
                    "informacoes": info.get("informacoes", {})
                }

            if info.get("regiao"):
                print(f"[DB] {info.get('tipo')} encontrado: {conteudo} → {info.get('regiao')}")
            else:
                print(f"[DB] QR Code lido, mas valor não está na base: {conteudo}")

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