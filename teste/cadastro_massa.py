#!/usr/bin/env python3
"""
Script para cadastro em massa de imagens no sistema de gestão de imagens.
As imagens devem estar em um diretório com o nome do arquivo seguindo o padrão CPF.extensao
Exemplo: 11111111111.jpg, 22222222222.png, etc.
"""

import os
import sys
import glob
import base64
import requests
import argparse
from pathlib import Path

def validar_cpf(cpf):
    """Valida se o CPF tem 11 dígitos numéricos"""
    return cpf.isdigit() and len(cpf) == 11

def cadastrar_imagem(api_url, cpf, caminho_imagem):
    """Cadastra uma imagem via API"""
    try:
        # Ler e converter imagem para Base64
        with open(caminho_imagem, 'rb') as f:
            conteudo_imagem = f.read()
            imagem_base64 = base64.b64encode(conteudo_imagem).decode('utf-8')
        
        # Preparar dados para envio
        files = {
            'cpf': (None, cpf),
            'imagem': (os.path.basename(caminho_imagem), conteudo_imagem, 'image/jpeg')
        }
        
        # Fazer requisição para a API
        response = requests.post(f"{api_url}/cadastro/", files=files)
        
        if response.status_code == 200:
            return True, "Cadastrado com sucesso"
        elif response.status_code == 400:
            return False, f"CPF já cadastrado ou inválido: {response.json().get('detail', 'Erro desconhecido')}"
        else:
            return False, f"Erro HTTP {response.status_code}: {response.text}"
            
    except Exception as e:
        return False, f"Erro ao processar arquivo: {str(e)}"

def processar_diretorio(diretorio, api_url, dry_run=False):
    """Processa todos os arquivos de imagem em um diretório"""
    
    if not os.path.exists(diretorio):
        print(f"❌ Diretório {diretorio} não encontrado!")
        return
    
    # Buscar arquivos de imagem
    extensoes = ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp']
    arquivos_encontrados = []
    
    for extensao in extensoes:
        arquivos_encontrados.extend(glob.glob(os.path.join(diretorio, extensao)))
        arquivos_encontrados.extend(glob.glob(os.path.join(diretorio, extensao.upper())))
    
    if not arquivos_encontrados:
        print(f"❌ Nenhum arquivo de imagem encontrado em {diretorio}")
        return
    
    print(f"📁 Encontrados {len(arquivos_encontrados)} arquivos de imagem")
    print(f"🌐 API URL: {api_url}")
    print(f"🔍 Modo: {'Simulação' if dry_run else 'Cadastro real'}")
    print("-" * 50)
    
    sucessos = 0
    erros = 0
    
    for arquivo in arquivos_encontrados:
        nome_arquivo = os.path.basename(arquivo)
        nome_sem_extensao = os.path.splitext(nome_arquivo)[0]
        
        print(f"📄 Processando: {nome_arquivo}")
        
        # Validar CPF
        if not validar_cpf(nome_sem_extensao):
            print(f"   ❌ CPF inválido: {nome_sem_extensao}")
            erros += 1
            continue
        
        cpf = nome_sem_extensao
        
        if dry_run:
            print(f"   ✅ Simulação: CPF {cpf} seria cadastrado")
            sucessos += 1
        else:
            # Cadastrar via API
            sucesso, mensagem = cadastrar_imagem(api_url, cpf, arquivo)
            if sucesso:
                print(f"   ✅ {mensagem}")
                sucessos += 1
            else:
                print(f"   ❌ {mensagem}")
                erros += 1
    
    print("-" * 50)
    print(f"📊 Resumo:")
    print(f"   ✅ Sucessos: {sucessos}")
    print(f"   ❌ Erros: {erros}")
    print(f"   📁 Total processado: {len(arquivos_encontrados)}")

def main():
    parser = argparse.ArgumentParser(description='Cadastro em massa de imagens no sistema de gestão')
    parser.add_argument('diretorio', help='Diretório contendo as imagens')
    parser.add_argument('--api-url', default='http://localhost:8000', 
                       help='URL da API (padrão: http://localhost:8000)')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Simular cadastro sem realmente cadastrar')
    
    args = parser.parse_args()
    
    print("🎯 Sistema de Cadastro em Massa de Imagens")
    print("=" * 50)
    
    # Verificar se o diretório existe
    if not os.path.exists(args.diretorio):
        print(f"❌ Diretório {args.diretorio} não encontrado!")
        sys.exit(1)
    
    # Testar conexão com a API
    if not args.dry_run:
        try:
            response = requests.get(f"{args.api_url}/docs", timeout=5)
            if response.status_code != 200:
                print(f"⚠️  Aviso: API pode não estar disponível em {args.api_url}")
        except requests.exceptions.RequestException:
            print(f"⚠️  Aviso: Não foi possível conectar à API em {args.api_url}")
            print("   Certifique-se de que o sistema está rodando com: docker-compose up")
    
    # Processar diretório
    processar_diretorio(args.diretorio, args.api_url, args.dry_run)

if __name__ == "__main__":
    main() 