# Sistemas-Inteligentes

Repositório destinado ao desenvolvimento de sistemas inteligentes com integração de hardware e software.

## 📋 Descrição

Este projeto reúne scripts e componentes para automação e leitura de dados, incluindo:
- **Controle de Garra com Arduino**: Script Arduino para controle de dispositivos robóticos
- **Leitura de QR Code**: Scripts Python para captura e processamento de códigos QR

## 🗂️ Estrutura do Projeto

Sistemas-Inteligentes/ ├── arduino/ │ └── garra/ │ └── controle_garra.ino ├── python/ │ └── qrcode/ │ └── leitor_qrcode.py ├── README.md └── requirements.txt

Code

## 🚀 Funcionalidades

### Arduino - Controle de Garra
Script para controlar uma garra robótica através de Arduino, com comunicação serial e automação de movimentos.

### Python - Leitor de QR Code
Scripts Python para:
- Captura de câmera em tempo real
- Decodificação de QR codes
- Processamento e armazenamento de dados

## 💻 Requisitos

### Hardware
- Arduino (Uno, Mega, etc.)
- Câmera/Webcam (para leitura de QR code)
- Garra robótica
- Cabos e componentes eletrônicos

### Software
- Python 3.7+
- Arduino IDE
- Bibliotecas Python (veja `requirements.txt`)

## 📦 Instalação

### Configuração Python

```bash
pip install -r requirements.txt
Configuração Arduino

Abra o Arduino IDE
Carregue o arquivo .ino da pasta arduino/garra/
Selecione a porta COM e o modelo de placa
Faça o upload do código
🔧 Uso

Executar leitor de QR Code

bash
python python/qrcode/leitor_qrcode.py
Controlar Garra

Carregue o sketch Arduino e use a comunicação serial para enviar comandos.

📝 Dependências Python

As principais dependências estão listadas em requirements.txt:

opencv-python (para processamento de imagem)
pyzbar (para decodificação de QR code)
pyserial (para comunicação Arduino)
🤝 Contribuindo

Para contribuir com o projeto:

Crie uma branch a partir de prd
Faça suas alterações
Commit com mensagens descritivas
Envie um Pull Request

📧 Contato

Para dúvidas ou sugestões, abra uma issue no repositório.
