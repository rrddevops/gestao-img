#!/usr/bin/env python3
"""
Script para inicializar e testar o sistema rapidamente
"""

import subprocess
import time
import requests
import sys
from datetime import datetime

def run_command(command, description):
    """Executa um comando e mostra o resultado"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} concluído")
            return True
        else:
            print(f"❌ {description} falhou")
            print(f"Erro: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Erro ao executar comando: {e}")
        return False

def wait_for_service(url, service_name, max_attempts=30):
    """Aguarda um serviço ficar disponível"""
    print(f"⏳ Aguardando {service_name} ficar disponível...")
    
    for attempt in range(max_attempts):
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {service_name} está disponível")
                return True
        except:
            pass
        
        print(f"   Tentativa {attempt + 1}/{max_attempts}...")
        time.sleep(2)
    
    print(f"❌ {service_name} não ficou disponível após {max_attempts} tentativas")
    return False

def test_basic_functionality():
    """Testa funcionalidade básica do sistema"""
    print("\n🧪 Testando funcionalidade básica...")
    
    # Testa agendamento
    test_payload = {
        'cpf': '99999999999',
        'entry_time': '20:00:00',
        'wait_time': '00:00:30'
    }
    
    try:
        response = requests.post('http://localhost:5002/schedule', json=test_payload, timeout=10)
        if response.status_code == 200:
            print("✅ Agendamento funcionando")
        else:
            print(f"❌ Erro no agendamento: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao testar agendamento: {e}")
        return False
    
    # Testa status
    try:
        response = requests.get('http://localhost:5002/schedule-status', timeout=5)
        if response.status_code == 200:
            print("✅ Status funcionando")
        else:
            print(f"❌ Erro no status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao testar status: {e}")
        return False
    
    return True

def main():
    """Função principal"""
    print("🚀 Inicializando Sistema de Gerenciamento de Imagens")
    print("=" * 60)
    
    # 1. Parar containers existentes
    print("\n1️⃣ Parando containers existentes...")
    run_command("docker-compose down", "Parando containers")
    
    # 2. Construir e iniciar containers
    print("\n2️⃣ Construindo e iniciando containers...")
    if not run_command("docker-compose up -d --build", "Construindo containers"):
        print("❌ Falha ao construir containers. Verifique se o Docker está rodando.")
        sys.exit(1)
    
    # 3. Aguardar serviços ficarem disponíveis
    print("\n3️⃣ Aguardando serviços ficarem disponíveis...")
    
    services = [
        ("http://localhost:5001", "App1 - Cadastro"),
        ("http://localhost:5002", "App2 - Webhook"),
        ("http://localhost:8083", "App3 - Visualization1"),
    ]
    
    for url, name in services:
        if not wait_for_service(url, name):
            print(f"❌ Falha ao aguardar {name}")
            sys.exit(1)
    
    # 4. Testar funcionalidade básica
    print("\n4️⃣ Testando funcionalidade básica...")
    if not test_basic_functionality():
        print("❌ Teste de funcionalidade falhou")
        sys.exit(1)
    
    # 5. Mostrar informações finais
    print("\n✅ Sistema inicializado com sucesso!")
    print("\n📋 Informações do Sistema:")
    print("   - App1 (Cadastro): http://localhost:5001")
    print("   - App2 (Webhook): http://localhost:5002")
    print("   - App3 (Visualizações):")
    for i in range(6):
        port = 8083 + i
        print(f"     * Visualization{i+1}: http://localhost:{port}/view/")
    
    print("\n🧪 Scripts de teste disponíveis:")
    print("   - python test_scheduler.py (teste rápido)")
    print("   - python example_usage.py (exemplos detalhados)")
    print("   - python test_complete_system.py (teste completo)")
    
    print("\n📖 Documentação:")
    print("   - README.md (visão geral)")
    print("   - README_SCHEDULER.md (detalhes do agendamento)")
    
    print(f"\n⏰ Sistema iniciado em: {datetime.now().strftime('%H:%M:%S')}")
    print("\n🎯 Para parar o sistema, execute: docker-compose down")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Inicialização interrompida pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro durante inicialização: {e}")
        sys.exit(1) 