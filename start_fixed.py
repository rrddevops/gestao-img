#!/usr/bin/env python3
"""
Script de inicialização corrigido para o Sistema de Gerenciamento de Imagens
"""

import subprocess
import time
import requests
import sys
import os

def run_command(command, description):
    """Executa um comando e mostra o resultado"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - Sucesso")
            return True
        else:
            print(f"❌ {description} - Falhou")
            print(f"Erro: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} - Erro: {e}")
        return False

def wait_for_service(url, description, max_attempts=30):
    """Aguarda um serviço ficar disponível"""
    print(f"⏳ Aguardando {description}...")
    for i in range(max_attempts):
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {description} está respondendo!")
                return True
        except:
            pass
        print(f"   Tentativa {i+1}/{max_attempts}")
        time.sleep(2)
    
    print(f"❌ {description} não respondeu após {max_attempts} tentativas")
    return False

def main():
    """Função principal"""
    print("🚀 Iniciando Sistema de Gerenciamento de Imagens (Versão Corrigida)")
    print("=" * 70)
    
    # Verificar se estamos no diretório correto
    if not os.path.exists("docker-compose.yml"):
        print("❌ docker-compose.yml não encontrado. Execute este script no diretório do projeto.")
        sys.exit(1)
    
    # Parar containers existentes
    if not run_command("docker-compose down", "Parando containers existentes"):
        print("⚠️  Continuando mesmo com erro ao parar containers...")
    
    # Limpar volumes se necessário
    print("🗑️  Limpando volumes para evitar conflitos...")
    run_command("docker-compose down -v", "Limpando volumes")
    
    # Construir e iniciar containers
    if not run_command("docker-compose up -d --build", "Construindo e iniciando containers"):
        print("❌ Falha ao iniciar containers")
        sys.exit(1)
    
    # Aguardar inicialização
    print("⏳ Aguardando inicialização dos serviços...")
    time.sleep(15)
    
    # Verificar status dos containers
    print("📊 Verificando status dos containers...")
    run_command("docker-compose ps", "Status dos containers")
    
    # Aguardar backend ficar disponível
    if not wait_for_service("http://localhost:8000/health", "Backend"):
        print("❌ Backend não está respondendo. Verificando logs...")
        run_command("docker-compose logs backend", "Logs do backend")
        sys.exit(1)
    
    # Verificar banco de dados
    print("🔍 Verificando banco de dados...")
    if not run_command("docker-compose exec -T db pg_isready -U postgres -d gestao_img", "Conexão com banco"):
        print("❌ Banco de dados não está funcionando. Verificando logs...")
        run_command("docker-compose logs db", "Logs do banco")
        sys.exit(1)
    
    # Testar endpoints básicos
    print("🧪 Testando endpoints básicos...")
    endpoints = [
        ("http://localhost:8000/", "Página inicial"),
        ("http://localhost:8000/docs", "Documentação API"),
        ("http://localhost:8000/cadastro", "Interface de cadastro"),
        ("http://localhost:8000/scheduler/status", "Status do agendador"),
        ("http://localhost:8000/websocket/status", "Status do WebSocket"),
    ]
    
    for url, description in endpoints:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {description}: OK")
            else:
                print(f"⚠️  {description}: Status {response.status_code}")
        except Exception as e:
            print(f"❌ {description}: Erro - {e}")
    
    print("\n" + "=" * 70)
    print("🎉 Sistema iniciado com sucesso!")
    print("=" * 70)
    
    print("\n📋 URLs do sistema:")
    print("   🌐 Página inicial: http://localhost:8000")
    print("   📝 Cadastro: http://localhost:8000/cadastro")
    print("   📚 API Docs: http://localhost:8000/docs")
    
    print("\n📺 Visualizações:")
    for i in range(1, 7):
        print(f"   🖥️  Visualization {i}: http://localhost:8000/visualization{i}")
    
    print("\n🧪 Para testar o sistema:")
    print("   python test_system.py")
    
    print("\n📊 Para ver logs:")
    print("   docker-compose logs -f backend")
    
    print("\n🛑 Para parar o sistema:")
    print("   docker-compose down")
    
    print("\n🔧 Se houver problemas:")
    print("   python diagnose.py")

if __name__ == "__main__":
    main() 