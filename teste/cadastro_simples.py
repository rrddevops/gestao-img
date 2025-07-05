#!/usr/bin/env python3
"""
Script simples para cadastro em massa de imagens
Uso: python cadastro_simples.py "C:\caminho\para\imagens"
"""

import os
import sys
import glob
import base64
import requests
from pathlib import Path

def main():
    # Verificar argumentos
    if len(sys.argv) != 2:
        print("❌ Uso: python cadastro_simples.py \"C:\\caminho\\para\\imagens\"")
        print("Exemplo: python cadastro_simples.py \"C:\\imagens\"")
        sys.exit(1)
    
    diretorio = sys.argv[1]
    api_url = "http://localhost:8000"
    
    print("🎯 Cadastro em Massa - Versão Simples")
    print("=" * 50)
    print(f"📁 Diretório: {diretorio}")
    print(f"🌐 API: {api_url}")
    print()
    
    # Verificar se o diretório existe
    if not os.path.exists(diretorio):
        print(f"❌ Diretório não encontrado: {diretorio}")
        sys.exit(1)
    
    # Buscar arquivos de imagem
    extensoes = ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp']
    arquivos = []
    
    for ext in extensoes:
        arquivos.extend(glob.glob(os.path.join(diretorio, ext)))
        arquivos.extend(glob.glob(os.path.join(diretorio, ext.upper())))
    
    if not arquivos:
        print(f"❌ Nenhuma imagem encontrada em: {diretorio}")
        print("   Certifique-se de que os arquivos têm extensões: .jpg, .jpeg, .png, .gif, .bmp")
        sys.exit(1)
    
    print(f"📄 Encontrados {len(arquivos)} arquivos de imagem")
    print()
    
    # Testar conexão com a API
    try:
        response = requests.get(f"{api_url}/docs", timeout=5)
        if response.status_code != 200:
            print("⚠️  Aviso: API pode não estar disponível")
    except:
        print("⚠️  Aviso: Não foi possível conectar à API")
        print("   Certifique-se de que o sistema está rodando: docker-compose up")
        print()
    
    # Processar cada arquivo
    sucessos = 0
    erros = 0
    
    for arquivo in arquivos:
        nome_arquivo = os.path.basename(arquivo)
        nome_sem_ext = os.path.splitext(nome_arquivo)[0]
        
        print(f"📄 Processando: {nome_arquivo}")
        
        # Validar CPF (11 dígitos)
        if not nome_sem_ext.isdigit() or len(nome_sem_ext) != 11:
            print(f"   ❌ CPF inválido: {nome_sem_ext}")
            erros += 1
            continue
        
        cpf = nome_sem_ext
        
        try:
            # Ler arquivo
            with open(arquivo, 'rb') as f:
                conteudo = f.read()
            
            # Preparar dados para envio
            files = {
                'cpf': (None, cpf),
                'imagem': (nome_arquivo, conteudo, 'image/jpeg')
            }
            
            # Enviar para API
            response = requests.post(f"{api_url}/cadastro/", files=files, timeout=30)
            
            if response.status_code == 200:
                print(f"   ✅ CPF {cpf} cadastrado com sucesso")
                sucessos += 1
            elif response.status_code == 400:
                erro_msg = response.json().get('detail', 'Erro desconhecido')
                print(f"   ❌ CPF {cpf}: {erro_msg}")
                erros += 1
            else:
                print(f"   ❌ Erro HTTP {response.status_code}")
                erros += 1
                
        except Exception as e:
            print(f"   ❌ Erro ao processar {nome_arquivo}: {str(e)}")
            erros += 1
    
    # Resumo final
    print()
    print("=" * 50)
    print("📊 RESUMO FINAL")
    print("=" * 50)
    print(f"✅ Sucessos: {sucessos}")
    print(f"❌ Erros: {erros}")
    print(f"📁 Total: {len(arquivos)}")
    print()
    
    if sucessos > 0:
        print("🎉 Cadastro concluído!")
        print(f"   Acesse: http://localhost/cadastro")
    else:
        print("😞 Nenhum cadastro foi realizado.")
    
    print()
    input("Pressione ENTER para sair...")

if __name__ == "__main__":
    main() 