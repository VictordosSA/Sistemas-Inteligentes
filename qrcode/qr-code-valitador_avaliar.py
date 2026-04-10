import cv2
from pyzbar.pyzbar import decode

# Dicionário simples para mapear sigla/nome ao nome completo da região
REGIOES_BR = {
    "SP": "São Paulo", "RJ": "Rio de Janeiro", "MG": "Minas Gerais", "ES": "Espírito Santo",
    "RS": "Rio Grande do Sul", "SC": "Santa Catarina", "PR": "Paraná",
    "BA": "Bahia", "PE": "Pernambuco", "CE": "Ceará", # ... adicione outros
    "Norte": "Região Norte", "Nordeste": "Região Nordeste",
    "Centro-Oeste": "Região Centro-Oeste", "Sudeste": "Região Sudeste",
    "Sul": "Região Sul"
}

def detectar_regiao(texto):
    """Tenta identificar a região brasileira no texto."""
    texto_upper = texto.upper()
    for sigla, nome in REGIOES_BR.items():
        if sigla.upper() in texto_upper:
            return nome
    return "Região não identificada"

def main():
    cap = cv2.VideoCapture(0) # Abre a webcam
    print("Iniciando câmera... Pressione 'q' para sair.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Lê os QR Codes no frame
        for qr in decode(frame):
            data = qr.data.decode('utf-8')
            regiao = detectar_regiao(data)
            
            # Desenha retângulo e texto na tela
            pts = qr.polygon
            if len(pts) > 3:
                cv2.polylines(frame, [cv2.typing.Point(*p) for p in pts], True, (0, 255, 0), 3)
            
            print(f"QR Code Detectado: {data}")
            print(f"Região Provável: {regiao}")
            print("-" * 20)

        cv2.imshow('Leitor QR Code - BR', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
