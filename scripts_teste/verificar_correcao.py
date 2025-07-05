#!/usr/bin/env python3
"""
Script para verificar se a correção do timing funcionou corretamente.
Testa um CPF e verifica se todas as visualizações estão funcionando.
"""

import requests
import time
import json

# Configuração
WEBHOOK_URL = "http://localhost:5002/webhook"
TEST_CPF = "00000000000"  # CPF de teste

def testar_visualizacao(porta, nome):
    """Testa se uma visualização está respondendo"""
    try:
        url = f"http://localhost:{porta}/current-image"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {nome} (porta {porta}): OK - {data}")
            return True
        else:
            print(f"❌ {nome} (porta {porta}): Erro {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {nome} (porta {porta}): Erro de conexão - {e}")
        return False

def agendar_cpf_teste():
    """Agenda um CPF para teste"""
    try:
        print(f"🔄 Agendando CPF {TEST_CPF} para teste...")
        data = {'cpf': TEST_CPF}
        response = requests.post(WEBHOOK_URL, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ CPF {TEST_CPF} agendado com sucesso!")
            print(f"📋 Resposta: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"❌ Erro ao agendar CPF {TEST_CPF}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def verificar_status_agendamentos():
    """Verifica o status dos agendamentos"""
    try:
        print("\n📊 Verificando status dos agendamentos...")
        response = requests.get(f"{WEBHOOK_URL.replace('/webhook', '')}/schedule-status", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status obtido com sucesso!")
            print(f"📋 Jobs agendados: {data.get('total_jobs', 0)}")
            
            # Mostra jobs por visualização
            jobs = data.get('scheduled_jobs', {})
            if TEST_CPF in jobs:
                print(f"📋 Jobs para CPF {TEST_CPF}:")
                for viz, info in jobs[TEST_CPF].items():
                    print(f"  - {viz}: {info.get('scheduled_time', 'N/A')}")
            else:
                print(f"⚠️  Nenhum job encontrado para CPF {TEST_CPF}")
            
            return True
        else:
            print(f"❌ Erro ao obter status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar status: {e}")
        return False

def main():
    print("🔧 VERIFICAÇÃO DA CORREÇÃO DE TIMING")
    print("=" * 60)
    
    # 1. Testa se todas as visualizações estão respondendo
    print("\n1️⃣ TESTANDO CONECTIVIDADE DAS VISUALIZAÇÕES")
    print("-" * 40)
    
    visualizacoes = [
        (8083, "visualization1"),
        (8084, "visualization2"), 
        (8085, "visualization3"),
        (8086, "visualization4"),
        (8087, "visualization5"),
        (8088, "visualization6")
    ]
    
    conectividade_ok = 0
    for porta, nome in visualizacoes:
        if testar_visualizacao(porta, nome):
            conectividade_ok += 1
    
    print(f"\n📊 Conectividade: {conectividade_ok}/6 visualizações respondendo")
    
    # 2. Agenda um CPF para teste
    print("\n2️⃣ AGENDANDO CPF PARA TESTE")
    print("-" * 40)
    
    if not agendar_cpf_teste():
        print("❌ Falha no agendamento. Abortando teste.")
        return
    
    # 3. Verifica status dos agendamentos
    print("\n3️⃣ VERIFICANDO STATUS DOS AGENDAMENTOS")
    print("-" * 40)
    
    verificar_status_agendamentos()
    
    # 4. Instruções para monitoramento
    print("\n4️⃣ INSTRUÇÕES PARA MONITORAMENTO")
    print("-" * 40)
    print("⏰ Aguarde 30 segundos para a primeira exibição...")
    print("📺 Monitore as visualizações:")
    for porta, nome in visualizacoes:
        print(f"  - {nome}: http://localhost:{porta}/view/")
    
    print("\n⏱️  SEQUÊNCIA ESPERADA:")
    print("• visualization1: aparece em 30s")
    print("• visualization2: aparece em 40s") 
    print("• visualization3: aparece em 50s")
    print("• visualization4: aparece em 60s")
    print("• visualization5: aparece em 70s")
    print("• visualization6: aparece em 80s")
    
    print("\n🎯 RESULTADO ESPERADO:")
    if conectividade_ok == 6:
        print("✅ Todas as visualizações devem mostrar a imagem na sequência correta")
    else:
        print(f"⚠️  Apenas {conectividade_ok}/6 visualizações estão respondendo")
        print("❌ Verifique se todos os containers estão rodando")

if __name__ == "__main__":
    main() 