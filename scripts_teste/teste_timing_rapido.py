#!/usr/bin/env python3
"""
Script de teste rápido para verificar se o timing está correto.
Agenda um CPF e mostra os horários esperados de exibição.
"""

import requests
import json
from datetime import datetime, timedelta

# Configuração
WEBHOOK_URL = "http://localhost:5002/webhook"
TEST_CPF = "00000000000"

def agendar_cpf():
    """Agenda um CPF e mostra os horários esperados"""
    try:
        print(f"🔄 Agendando CPF {TEST_CPF}...")
        data = {'cpf': TEST_CPF}
        response = requests.post(WEBHOOK_URL, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ CPF {TEST_CPF} agendado com sucesso!")
            
            # Mostra informações do agendamento
            entry_time = result.get('entry_time', 'N/A')
            wait_time = result.get('wait_time', 'N/A')
            
            print(f"\n📋 INFORMAÇÕES DO AGENDAMENTO:")
            print(f"• CPF: {TEST_CPF}")
            print(f"• Horário de entrada: {entry_time}")
            print(f"• Tempo de espera: {wait_time}")
            
            # Calcula horários esperados
            now = datetime.now()
            print(f"• Horário atual: {now.strftime('%H:%M:%S')}")
            
            print(f"\n⏱️  SEQUÊNCIA DE EXIBIÇÃO ESPERADA:")
            delays = [30, 40, 50, 60, 70, 80]
            for i, delay in enumerate(delays, 1):
                expected_time = now + timedelta(seconds=delay)
                print(f"• visualization{i}: {expected_time.strftime('%H:%M:%S')} (após {delay}s)")
            
            print(f"\n📺 URLs DAS VISUALIZAÇÕES:")
            for i, delay in enumerate(delays, 1):
                port = 8082 + i
                print(f"• visualization{i}: http://localhost:{port}/view/")
            
            return True
        else:
            print(f"❌ Erro ao agendar CPF {TEST_CPF}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def verificar_status():
    """Verifica o status dos agendamentos"""
    try:
        print(f"\n📊 Verificando status dos agendamentos...")
        response = requests.get(f"{WEBHOOK_URL.replace('/webhook', '')}/schedule-status", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            total_jobs = data.get('total_jobs', 0)
            print(f"✅ Total de jobs agendados: {total_jobs}")
            
            # Mostra jobs cronológicos
            chronological = data.get('scheduled_jobs_chronological', [])
            if chronological:
                print(f"\n📋 JOBS AGENDADOS (ordem cronológica):")
                for job in chronological:
                    cpf = job.get('cpf', 'N/A')
                    viz = job.get('visualization', 'N/A')
                    time = job.get('scheduled_time', 'N/A')
                    print(f"• {time} - {cpf} em {viz}")
            else:
                print(f"⚠️  Nenhum job encontrado")
            
            return True
        else:
            print(f"❌ Erro ao obter status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar status: {e}")
        return False

def main():
    print("⚡ TESTE RÁPIDO DE TIMING")
    print("=" * 50)
    
    # Agenda o CPF
    if not agendar_cpf():
        print("❌ Falha no agendamento. Abortando teste.")
        return
    
    # Verifica status
    verificar_status()
    
    print(f"\n🎯 INSTRUÇÕES:")
    print(f"1. Aguarde 30 segundos para a primeira exibição")
    print(f"2. Monitore as visualizações nas URLs listadas acima")
    print(f"3. Cada imagem deve aparecer por 10 segundos")
    print(f"4. A sequência deve ser: 30s, 40s, 50s, 60s, 70s, 80s")

if __name__ == "__main__":
    main() 