# Sistema Integrado: Leitor QR Code + Controle de Servos Arduino

Este sistema combina leitura de QR Codes via webcam com controle automático de servos no Arduino Uno R3 baseado na região detectada.

## 🚀 Funcionalidades

- **Leitura de QR Codes**: Detecta códigos QR em tempo real via webcam
- **Busca em Banco de Dados**: Consulta informações baseadas no conteúdo do QR Code
- **Mapeamento por Região**: Cada região brasileira tem um comando específico para os servos
- **Controle Automático**: Quando um QR Code é lido, os servos se movem automaticamente
- **Interface Web**: Controle completo via navegador web
- **Teste Manual**: Permite testar comandos dos servos manualmente

## 📋 Mapeamento de Regiões

| Região | Comando Servo | Descrição |
|--------|---------------|-----------|
| Norte | SERVO1:90,SERVO2:45 | Servo 1: 90°, Servo 2: 45° |
| Nordeste | SERVO1:135,SERVO2:90 | Servo 1: 135°, Servo 2: 90° |
| Centro-Oeste | SERVO1:45,SERVO2:135 | Servo 1: 45°, Servo 2: 135° |
| Sudeste | SERVO1:0,SERVO2:180 | Servo 1: 0°, Servo 2: 180° |
| Sul | SERVO1:180,SERVO2:0 | Servo 1: 180°, Servo 2: 0° |
| Não encontrada | SERVO1:90,SERVO2:90 | Posição neutra |

## 🔧 Hardware Necessário

- **Arduino Uno R3**
- **2 Servos Micro (SG90 ou similar)**
- **Cabos jumper**
- **Fonte de alimentação para Arduino**
- **Webcam (interna ou externa)**

## ⚙️ Conexões Arduino

```
Arduino Uno R3
├── Pino 9  → Sinal Servo 1
├── Pino 10 → Sinal Servo 2
├── GND     → GND dos Servos
└── 5V      → VCC dos Servos
```

## 📦 Instalação

### 1. Instalar Dependências Python

```bash
pip install Flask opencv-python pyzbar numpy flask-socketio eventlet pyserial
```

### 2. Carregar Código no Arduino

1. Abra o Arduino IDE
2. Carregue o arquivo `Script_Servo/Script_Servo_Arduino.ino`
3. Conecte o Arduino ao computador
4. Selecione a porta correta em **Ferramentas → Porta**
5. Clique em **Carregar**

### 3. Configurar Porta Serial (Opcional)

Por padrão, o sistema tenta usar `COM3` no Windows. Para alterar:

**Via variável de ambiente:**
```bash
# Windows PowerShell
$env:ARDUINO_PORT="COM4"

# Linux/Mac
export ARDUINO_PORT="/dev/ttyACM0"
```

**Ou modificar no código:**
```python
arduino_port = "COM4"  # Altere para sua porta
```

## 🎯 Como Usar

### 1. Executar o Sistema

```bash
python qrCodeFunctionalMac/teste_camera.py
```

### 2. Abrir Interface Web

Acesse: `http://127.0.0.1:5000`

### 3. Configurar Câmera

- Selecione a câmera desejada no dropdown
- Ajuste brilho, contraste, saturação se necessário
- Clique em "Aplicar"

### 4. Testar Sistema

1. **Teste Manual**: Use o painel "Controle dos Servos" para testar cada região
2. **Teste Automático**: Aponte a câmera para um QR Code com dados que correspondam às regiões

## 📊 Exemplos de QR Codes

O sistema reconhece automaticamente dados como:

- **CPF**: `123.456.789-00` → Norte
- **CNPJ**: `12.345.678/0001-99` → Centro-Oeste
- **Cidades**: `São Paulo` → Sudeste
- **Estados**: `Salvador` → Nordeste

## 🔍 Monitoramento

### Console Python
Mostra logs detalhados:
- Conexão com Arduino
- Detecção de câmeras
- Leitura de QR Codes
- Comandos enviados aos servos

### Interface Web
- Status da conexão Arduino
- Último comando enviado
- Preview da câmera em tempo real
- Informações do QR Code detectado

## 🛠️ Solução de Problemas

### Arduino não conecta
1. Verifique se a porta serial está correta
2. Feche o Arduino IDE se estiver aberto
3. Reinicie o Arduino (desconecte e conecte novamente)

### Câmera não funciona
1. Feche outros programas que usam câmera
2. Teste câmeras diferentes via interface web
3. Verifique permissões da câmera no sistema

### Servos não se movem
1. Verifique conexões físicas
2. Confirme que os servos têm alimentação adequada
3. Teste manualmente via interface web

## 📝 Protocolo de Comunicação

### Comandos Arduino

**Formato**: `SERVO1:ângulo` ou `SERVO2:ângulo` ou `SERVO1:ângulo,SERVO2:ângulo`

**Exemplos**:
- `SERVO1:90` - Move servo 1 para 90°
- `SERVO2:45` - Move servo 2 para 45°
- `SERVO1:135,SERVO2:90` - Move ambos os servos

### Respostas Arduino
- `Servo X movido para: Y` - Confirmação de movimento
- `Erro: Posicao invalida` - Ângulo fora do range 0-180°

## 🔄 Personalização

### Adicionar Novas Regiões

Edite o dicionário `REGIAO_COMANDOS` no arquivo `teste_camera.py`:

```python
REGIAO_COMANDOS = {
    "NovaRegiao": "SERVO1:60,SERVO2:120",
    # ... outras regiões
}
```

### Modificar Ângulos

Ajuste os valores no dicionário para diferentes posições dos servos.

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique os logs no console
2. Teste componentes individualmente
3. Confirme conexões físicas
4. Reinicie todos os componentes