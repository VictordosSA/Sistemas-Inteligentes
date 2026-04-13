# Sistemas-Inteligentes

Repositório com exemplos e artefatos para integração hardware ↔ software em projetos de sistemas inteligentes.

## Visão geral
Conteúdo atual do repositório:
- templates/dashboard.html — página de visualização (Socket.IO) para mostrar contadores/estatísticas.
- Script_Garra/Script_Garra_Arduino.ino — sketch Arduino para controle de garra (servos, botões, sensor, buzzer).
- Script_Lego/Area51.lmsp — arquivo de projeto LEGO (Area51).

## Estrutura (resumida)
Sistemas-Inteligentes/
- templates/
  - dashboard.html
- Script_Garra/
  - Script_Garra_Arduino.ino
- Script_Lego/
  - Area51.lmsp
- README.md

## Requisitos (macOS)
- Homebrew (opcional, para dependências nativas)
- Python 3.8+
- Arduino IDE (ou CLI) para upload do sketch
- (Opcional) Webcam para testes
- Librarias nativas: zbar (para pyzbar) — instalar via Homebrew

## Instalação (rápida, macOS)
1. Instalar Homebrew (se necessário):
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

2. Instalar zbar (necessário para pyzbar):
```bash
brew update
brew install zbar
```

3. Criar e ativar virtualenv no diretório do projeto:
```bash
cd /Users/pasta_do_usuario/Sistemas-Inteligentes
python3 -m venv venv
source venv/bin/activate
```

4. Instalar dependências Python (se houver requirements.txt):
```bash
pip install --upgrade pip
pip install -r requirements.txt
```
Se não existir requirements.txt, exemplos de libs úteis:
```bash
pip install flask flask_socketio eventlet opencv-python-headless numpy pyzbar pyserial
```

## Arduino — upload do sketch
1. Abra Script_Garra/Script_Garra_Arduino.ino na Arduino IDE.
2. Selecione placa e porta corretas (Tools → Board / Port).
3. Faça upload.
4. Ajuste limites de saída dos servos (variáveis B, G, P, A no código) conforme a montagem.

## Testes / execução
- Dashboard: templates/dashboard.html espera receber eventos via Socket.IO; para funcionar, abra a aplicação server-side que emita eventos (ex.: app Flask + Socket.IO). Se não houver servidor, use um servidor de desenvolvimento que suporte Socket.IO ou adapte o arquivo para testes locais.
- Leitor QR (se houver scripts Python): ative venv e execute o script correspondente. Garanta zbar instalado.

Exemplo geral para execução local (quando existir app.py):
```bash
source venv/bin/activate
python app.py
# abrir http://localhost:5000/dashboard
```

## Boas práticas
- Faça branch para novas features: git checkout -b feat/nome-da-feature
- Commits atômicos com mensagens no estilo Conventional Commits (feat:, fix:, chore:, etc.)
- Teste hardware em bancada antes de operar em condições reais.

## Contribuição
- Abra issues descrevendo o problema/feature.
- Envie pull requests a partir de branches com alterações específicas.
- Documente alterações relevantes no README ou em arquivos separados.

## Contato
Abra uma issue no repositório para dúvidas, erros de execução ou solicitações de melhoria.
