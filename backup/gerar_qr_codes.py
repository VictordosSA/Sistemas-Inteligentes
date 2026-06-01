#!/usr/bin/env python3
"""
Script para gerar QR codes com base nos dados do banco de dados centro_logistica.
Os QR codes gerados podem ser lidos pelo teste_camera.py e retornarão a região correspondente.
"""

import os
import sys

# Tenta importar qrcode; se falhar, oferece instruções de instalação
try:
    import qrcode
except ModuleNotFoundError:
    print("[ERRO] Módulo qrcode não instalado.")
    print("Instale com: python -m pip install qrcode[pil]")
    sys.exit(1)

# Dados do banco de dados (baseado no schema centro_logistica.sql)
CLIENTES = [
    {"nome": "João Silva", "cpf": "123.456.789-00", "email": "joao.silva@email.com", "regiao": "Norte"},
    {"nome": "Maria Oliveira", "cpf": "234.567.890-11", "email": "maria.oliveira@email.com", "regiao": "Nordeste"},
    {"nome": "Carlos Souza", "cpf": "345.678.901-22", "email": "carlos.souza@email.com", "regiao": "Centro-Oeste"},
    {"nome": "Ana Santos", "cpf": "456.789.012-33", "email": "ana.santos@email.com", "regiao": "Sudeste"},
    {"nome": "Pedro Costa", "cpf": "567.890.123-44", "email": "pedro.costa@email.com", "regiao": "Sul"},
]

DISTRIBUIDORAS = [
    {"nome": "Distribuidora Central", "cnpj": "12.345.678/0001-99", "email": "contato@distcentral.com", "regiao": "Centro-Oeste"},
]

LOCALIDADES = [
    {"cidade": "Porto Velho", "estado": "Rondônia", "regiao": "Norte", "cep": "76801-000"},
    {"cidade": "Salvador", "estado": "Bahia", "regiao": "Nordeste", "cep": "40140-110"},
    {"cidade": "Cuiabá", "estado": "Mato Grosso", "regiao": "Centro-Oeste", "cep": "78043-000"},
    {"cidade": "São Paulo", "estado": "São Paulo", "regiao": "Sudeste", "cep": "04101-000"},
    {"cidade": "Curitiba", "estado": "Paraná", "regiao": "Sul", "cep": "80420-090"},
]

def criar_pasta_qr():
    """Cria pasta qr_codes se não existir."""
    pasta = "qr_codes"
    if not os.path.exists(pasta):
        os.makedirs(pasta)
        print(f"[OK] Pasta '{pasta}' criada.")
    return pasta


def gerar_qr(conteudo, nome_arquivo, pasta):
    """Gera um QR code e salva em arquivo PNG."""
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=2,
        )
        qr.add_data(conteudo)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        caminho = os.path.join(pasta, f"{nome_arquivo}.png")
        img.save(caminho)
        print(f"[GERADO] {caminho} -> {conteudo}")
        return caminho
    except Exception as e:
        print(f"[ERRO] Falha ao gerar QR code para '{conteudo}': {e}")
        return None


def main():
    print("[INFO] Iniciando geração de QR codes...\n")
    
    pasta = criar_pasta_qr()
    gerados = []
    
    # Gerar QR codes para clientes
    print("=== CLIENTES ===")
    for cliente in CLIENTES:
        # QR code com CPF
        gerar_qr(cliente["cpf"], f"cliente_cpf_{cliente['cpf'].replace('.', '').replace('-', '')}", pasta)
        # QR code com Email
        gerar_qr(cliente["email"], f"cliente_email_{cliente['email'].replace('@', '_').replace('.', '_')}", pasta)
        # QR code com Nome
        gerar_qr(cliente["nome"], f"cliente_nome_{cliente['nome'].replace(' ', '_')}", pasta)
    
    # Gerar QR codes para distribuidoras
    print("\n=== DISTRIBUIDORAS ===")
    for dist in DISTRIBUIDORAS:
        # QR code com CNPJ
        gerar_qr(dist["cnpj"], f"dist_cnpj_{dist['cnpj'].replace('.', '').replace('/', '').replace('-', '')}", pasta)
        # QR code com Email
        gerar_qr(dist["email"], f"dist_email_{dist['email'].replace('@', '_').replace('.', '_')}", pasta)
        # QR code com Nome
        gerar_qr(dist["nome"], f"dist_nome_{dist['nome'].replace(' ', '_')}", pasta)
    
    # Gerar QR codes para localidades
    print("\n=== LOCALIDADES ===")
    for local in LOCALIDADES:
        # QR code com Cidade
        gerar_qr(local["cidade"], f"local_cidade_{local['cidade'].replace(' ', '_')}", pasta)
        # QR code com CEP
        gerar_qr(local["cep"], f"local_cep_{local['cep'].replace('-', '')}", pasta)
    
    print(f"\n[OK] QR codes gerados em: {os.path.abspath(pasta)}")
    print("\n[DICA] Para testar:")
    print(f"  1. Abra os arquivos PNG em {pasta}")
    print("  2. Aponte sua câmera para um QR code")
    print("  3. O script teste_camera.py vai ler e buscar a região correspondente")


if __name__ == "__main__":
    main()
