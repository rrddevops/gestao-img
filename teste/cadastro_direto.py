#!/usr/bin/env python3
"""
Script para cadastro em massa direto no banco de dados
Uso: python cadastro_direto.py "C:\caminho\para\imagens"
"""

import os
import sys
import glob
import base64
import psycopg2
from pathlib import Path

def conectar_banco():
    """Conecta ao banco de dados PostgreSQL"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="gestao_img",
            user="postgres",
            password="postgres"
        )
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco: {e}")
        return None

def cadastrar_imagem(conn, cpf, caminho_imagem):
    """Cadastra uma imagem no banco de dados"""
    try:
        # Ler e converter imagem para Base64
        with open(caminho_imagem, 'rb') as f:
            conteudo = f.read()
            imagem_base64 = base64.b64encode(conteudo).decode('utf-8')
        
        # Verificar se CPF já existe
        cursor = conn.cursor()
        cursor.execute("SELECT cpf FROM cadastro WHERE cpf = %s", (cpf,))
        if cursor.fetchone():
            cursor.close()
            return False, "CPF já cadastrado"
        
        # Inserir novo cadastro
        cursor.execute(
            "INSERT INTO cadastro (cpf, caminho_imagem) VALUES (%s, %s)",
            (cpf, imagem_base64)
        )
        conn.commit()
        cursor.close()
        return True, "Cadastrado com sucesso"
        
    except Exception as e:
        conn.rollback()
        return False, f"Erro: {str(e)}"

def main():
    # Verificar argumentos
    if len(sys.argv) != 2:
        print("❌ Uso: python cadastro_direto.py \"C:\\caminho\\para\\imagens\"")
        print("Exemplo: python cadastro_direto.py \"C:\\imagens\"")
        sys.exit(1)
    
    diretorio = sys.argv[1]
    
    print("🎯 Cadastro em Massa - Acesso Direto ao Banco")
    print("=" * 50)
    print(f"📁 Diretório: {diretorio}")
    print()
    
    # Verificar se o diretório existe
    if not os.path.exists(diretorio):
        print(f"❌ Diretório não encontrado: {diretorio}")
        sys.exit(1)
    
    # Conectar ao banco
    print("🔌 Conectando ao banco de dados...")
    conn = conectar_banco()
    if not conn:
        print("❌ Não foi possível conectar ao banco de dados")
        print("   Certifique-se de que o PostgreSQL está rodando:")
        print("   docker-compose up -d")
        sys.exit(1)
    
    print("✅ Conectado ao banco de dados")
    print()
    
    # Buscar arquivos de imagem
    extensoes = ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp']
    arquivos = []
    
    for ext in extensoes:
        arquivos.extend(glob.glob(os.path.join(diretorio, ext)))
        arquivos.extend(glob.glob(os.path.join(diretorio, ext.upper())))
    
    if not arquivos:
        print(f"❌ Nenhuma imagem encontrada em: {diretorio}")
        print("   Certifique-se de que os arquivos têm extensões: .jpg, .jpeg, .png, .gif, .bmp")
        conn.close()
        sys.exit(1)
    
    print(f"📄 Encontrados {len(arquivos)} arquivos de imagem")
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
        
        # Cadastrar no banco
        sucesso, mensagem = cadastrar_imagem(conn, cpf, arquivo)
        
        if sucesso:
            print(f"   ✅ CPF {cpf} cadastrado com sucesso")
            sucessos += 1
        else:
            print(f"   ❌ CPF {cpf}: {mensagem}")
            erros += 1
    
    # Fechar conexão
    conn.close()
    
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