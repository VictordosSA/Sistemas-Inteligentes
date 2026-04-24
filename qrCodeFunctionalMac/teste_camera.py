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

# Variáveis globais para controle da câmera
camera_index = int(os.environ.get("CAMERA_INDEX", 0))
camera_lock = threading.Lock()
camera_thread_running = True

# Instância do detector OpenCV (usada no fallback)
_cv_detector = cv2.QRCodeDetector()

# Função para listar câmeras disponíveis
def listar_cameras_disponiveis():
    """Lista todas as câmeras disponíveis no sistema com melhor detecção."""
    cameras = []
    max_cameras = 20
    consecutive_failures = 0
    max_consecutive_failures = 5  # Parar após 5 falhas consecutivas
    
    print("[INFO] Escaneando câmeras disponíveis...")
    
    for i in range(max_cameras):
        try:
            # Tentar abrir câmera
            cap = cv2.VideoCapture(i)
            
            if cap is not None and cap.isOpened():
                # Tentar ler um frame para verificar se a câmera funciona
                try:
                    ret, frame = cap.read()
                    
                    if ret and frame is not None:  # Se conseguiu ler frame, câmera é válida
                        consecutive_failures = 0
                        
                        # Tentar obter nome da câmera
                        try:
                            nome_camera = cap.getBackendName()
                            if not nome_camera or nome_camera == "":
                                nome_camera = "Desconhecido"
                        except:
                            nome_camera = "Desconhecido"
                        
                        # Melhor nomeação
                        if i == 0:
                            nome_exibicao = f"📱 Câmera Interna (Notebook) - {nome_camera}"
                        else:
                            nome_exibicao = f"📷 Câmera Externa {i} - {nome_camera}"
                        
                        cameras.append({
                            "indice": i,
                            "nome": nome_exibicao
                        })
                        print(f"[OK] Câmera {i} detectada: {nome_exibicao}")
                    else:
                        consecutive_failures += 1
                        print(f"[SKIP] Índice {i}: não conseguiu capturar frame")
                except Exception as e:
                    consecutive_failures += 1
                    print(f"[SKIP] Índice {i}: {str(e)[:40]}")
                finally:
                    try:
                        cap.release()
                    except:
                        pass
            else:
                consecutive_failures += 1
                print(f"[SKIP] Índice {i}: câmera não abriu")
            
            # Parar se muitas falhas consecutivas
            if consecutive_failures >= max_consecutive_failures:
                print(f"[INFO] Parando varredura após {max_consecutive_failures} falhas consecutivas")
                break
            
        except Exception as e:
            consecutive_failures += 1
            print(f"[DEBUG] Índice {i}: {str(e)[:40]}")
    
    if not cameras:
        print("[WARN] Nenhuma câmera detectada! Tente:")
        print("  - Verificar se a câmera está conectada")
        print("  - Fechar outros aplicativos que usam câmera")
        print("  - Reiniciar o script")
    else:
        print(f"[INFO] Total de câmeras encontradas: {len(cameras)}")
    
    return cameras

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

def processar_frame(frame):
    """Melhora a qualidade do frame para câmeras escuras."""
    if frame is None:
        return frame
    
    try:
        # Aumentar brilho manualmente se a imagem for muito escura
        frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(frame_hsv)
        
        # Se muito escuro (V < 80), aumentar o brilho
        if v.mean() < 80:
            v = cv2.add(v, 40)
            v = cv2.min(v, 255)  # Garantir que não ultrapasse 255
            frame_hsv = cv2.merge([h, s, v])
            frame = cv2.cvtColor(frame_hsv, cv2.COLOR_HSV2BGR)
        
        # Aplicar equilização de histograma em baixa luminosidade
        if v.mean() < 100:
            lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            l = clahe.apply(l)
            frame = cv2.merge([l, a, b])
            frame = cv2.cvtColor(frame, cv2.COLOR_LAB2BGR)
        
        # Reduzir ruído se necessário
        if v.mean() < 120:
            frame = cv2.fastNlMeansDenoisingColored(frame, None, h=10, hForColorComponents=10, templateWindowSize=7, searchWindowSize=21)
        
        return frame
    except:
        return frame

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

# Dicionário global para armazenar configurações de câmera
camera_settings = {
    "brightness": 60,
    "contrast": 40,
    "saturation": 80,
    "exposure": -5,
    "gain": 50,
    "auto_exposure": True
}
settings_lock = threading.Lock()

def otimizar_camera(cap):
    """Otimiza as configurações da câmera para melhor qualidade."""
    try:
        with settings_lock:
            settings = camera_settings.copy()
        
        # Tentar definir propriedades (nem todas as câmeras suportam todas)
        configs = [
            (cv2.CAP_PROP_BRIGHTNESS, settings["brightness"], "Brilho"),
            (cv2.CAP_PROP_CONTRAST, settings["contrast"], "Contraste"),
            (cv2.CAP_PROP_SATURATION, settings["saturation"], "Saturação"),
            (cv2.CAP_PROP_GAIN, settings["gain"], "Ganho"),
        ]
        
        # Exposição (algumas câmeras usam valores negativos para exposição manual)
        if settings["auto_exposure"]:
            try:
                cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)  # 1 = auto
                print("[OK] Exposição automática ativada")
            except:
                pass
        else:
            try:
                cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)  # 0.25 = manual
                cap.set(cv2.CAP_PROP_EXPOSURE, settings["exposure"])
                print(f"[OK] Exposição manual ajustada: {settings['exposure']}")
            except:
                pass
        
        # Tentar definir outras propriedades
        for prop, valor, nome in configs:
            try:
                # Normalizar valor entre 0 e 1 para algumas propriedades
                if prop in [cv2.CAP_PROP_BRIGHTNESS, cv2.CAP_PROP_CONTRAST, cv2.CAP_PROP_SATURATION]:
                    # Converter 0-100 para -1 a 1 (ou 0 a 1 dependendo da câmera)
                    valor_normalizado = (valor / 100.0) * 2 - 1
                else:
                    valor_normalizado = valor / 100.0
                
                cap.set(prop, valor_normalizado)
                print(f"[OK] {nome}: {valor}")
            except Exception as e:
                print(f"[WARN] Não conseguiu ajustar {nome}: {str(e)[:50]}")
        
        # Equilíbrio de branco automático (se suportado)
        try:
            cap.set(cv2.CAP_PROP_AUTO_WB, 1)
            print("[OK] Equilíbrio de branco automático ativado")
        except:
            pass
        
        # Desabilitar buffer para obter frames mais recentes
        try:
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        except:
            pass
            
    except Exception as e:
        print(f"[WARN] Erro ao otimizar câmera: {str(e)[:100]}")

def rodar_camera():
    global dados_compartilhados, latest_frame, camera_index, camera_thread_running
    print("[INFO] Iniciando sistema de câmera...")

    # Listar câmeras disponíveis
    cameras = listar_cameras_disponiveis()
    if cameras:
        print("[INFO] Câmeras detectadas:")
        for cam in cameras:
            print(f"  - {cam['nome']} (índice: {cam['indice']})")
    else:
        print("[WARN] Nenhuma câmera detectada!")

    cap = None
    current_camera_open = None
    failed_attempts = 0
    
    while camera_thread_running:
        try:
            # Verificar se houve mudança na câmera
            with camera_lock:
                requested_camera = camera_index
            
            # Se a câmera mudou ou está nula, reinicializa
            if cap is None or current_camera_open != requested_camera:
                if cap is not None:
                    try:
                        print(f"[INFO] Liberando câmera {current_camera_open}...")
                        cap.release()
                    except:
                        pass
                    cap = None
                
                print(f"[INFO] Tentando abrir câmera com índice: {requested_camera}")
                
                # No Windows, usar DirectShow é mais confiável
                # No macOS usar AVFoundation
                try:
                    if sys.platform == "darwin":
                        cap = cv2.VideoCapture(requested_camera, cv2.CAP_AVFOUNDATION)
                    elif sys.platform == "win32":
                        cap = cv2.VideoCapture(requested_camera, cv2.CAP_DSHOW)
                    else:
                        cap = cv2.VideoCapture(requested_camera)
                    
                    # Configurar propriedades da câmera
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                    cap.set(cv2.CAP_PROP_FPS, 30)
                    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduzir buffer para frames mais recentes
                    
                    # Otimizar câmera para melhor qualidade
                    otimizar_camera(cap)
                    
                    # Verificar se a câmera abriu e consegue capturar
                    if cap.isOpened():
                        ret, test_frame = cap.read()
                        if ret and test_frame is not None:
                            current_camera_open = requested_camera
                            failed_attempts = 0
                            print(f"[OK] Câmera {requested_camera} aberta com sucesso!")
                        else:
                            print(f"[WARN] Câmera {requested_camera} abriu mas não consegue capturar frames")
                            cap.release()
                            cap = None
                            current_camera_open = None
                            failed_attempts += 1
                    else:
                        print(f"[WARN] Câmera {requested_camera} não conseguiu abrir")
                        cap = None
                        current_camera_open = None
                        failed_attempts += 1
                except Exception as e:
                    print(f"[ERRO] Falha ao abrir câmera {requested_camera}: {str(e)[:100]}")
                    cap = None
                    current_camera_open = None
                    failed_attempts += 1
                
                # Se falhou muito, tentar câmera padrão
                if failed_attempts > 2 and requested_camera != 0:
                    print(f"[WARN] Câmera {requested_camera} falhou múltiplas vezes, tentando câmera padrão (0)")
                    with camera_lock:
                        camera_index = 0
                    time.sleep(1)
                    continue
                
                if cap is None:
                    time.sleep(1)
                    continue
            
            if cap is None:
                time.sleep(0.5)
                continue
            
            # Capturar frame
            ret, frame = cap.read()
            if not ret or frame is None:
                print(f"[WARN] Falha ao ler frame da câmera {current_camera_open}")
                cap = None
                current_camera_open = None
                time.sleep(0.5)
                continue
            
            # Processar frame para melhorar qualidade
            frame = processar_frame(frame)
            
            # Atualizar frame para o stream
            with frame_lock:
                latest_frame = frame.copy()

            # Decodificar QR codes
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
        
        except Exception as e:
            print(f"[ERRO] Erro na thread de câmera: {str(e)[:100]}")
            if cap is not None:
                try:
                    cap.release()
                except:
                    pass
            cap = None
            current_camera_open = None
            time.sleep(1)

    if cap is not None:
        cap.release()
    cv2.destroyAllWindows()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/camera_settings', methods=['GET', 'POST'])
def camera_settings():
    """Obtém ou atualiza as configurações da câmera."""
    global camera_settings
    
    if request.method == 'GET':
        with settings_lock:
            return jsonify(camera_settings)
    
    elif request.method == 'POST':
        data = request.get_json()
        
        if data:
            with settings_lock:
                # Atualizar apenas os campos enviados
                for key in ['brightness', 'contrast', 'saturation', 'exposure', 'gain', 'auto_exposure']:
                    if key in data:
                        camera_settings[key] = data[key]
            
            print(f"[INFO] Configurações de câmera atualizadas: {camera_settings}")
            return jsonify({
                "sucesso": True,
                "mensagem": "Configurações salvas",
                "settings": camera_settings
            })
        
        return jsonify({"sucesso": False, "mensagem": "Dados inválidos"}), 400

@app.route('/cameras')
def cameras():
    """Retorna lista de câmeras disponíveis."""
    global camera_index
    cameras_list = listar_cameras_disponiveis()
    return jsonify({
        "cameras": cameras_list,
        "camera_atual": camera_index
    })

@app.route('/set_camera/<int:index>', methods=['POST'])
def set_camera(index):
    """Muda a câmera sendo usada."""
    global camera_index
    cameras_list = listar_cameras_disponiveis()
    camera_indices = [cam['indice'] for cam in cameras_list]
    
    if index not in camera_indices:
        return jsonify({
            "sucesso": False,
            "mensagem": f"Câmera {index} não encontrada",
            "cameras_disponiveis": camera_indices
        }), 400
    
    with camera_lock:
        camera_index = index
    
    print(f"[INFO] Câmera mudada para índice {index}")
    return jsonify({
        "sucesso": True,
        "mensagem": f"Câmera mudada para {index}",
        "camera_atual": index
    })

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