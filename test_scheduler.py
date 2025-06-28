#!/usr/bin/env python3
"""
Script de teste para o novo sistema de agendamento baseado em datetime
"""

import requests
import json
from datetime import datetime, timedelta
import time

# Configuração
WEBHOOK_URL = "http://localhost:5002/schedule"
STATUS_URL = "http://localhost:5002/schedule-status"

def test_schedule():
    """Testa o agendamento de uma imagem"""
    
    # Dados de teste
    cpf = "12345678901"
    entry_time = "20:00:00"  # Horário de entrada
    wait_time = "00:00:30"   # 30 segundos de espera
    
    print(f"=== Teste de Agendamento ===")
    print(f"CPF: {cpf}")
    print(f"Horário de entrada: {entry_time}")
    print(f"Tempo de espera: {wait_time}")
    print()
    
    # Calcula horários esperados
    entry_dt = datetime.strptime(entry_time, '%H:%M:%S')
    wait_dt = datetime.strptime(wait_time, '%H:%M:%S')
    
    first_display = entry_dt + timedelta(
        hours=wait_dt.hour,
        minutes=wait_dt.minute,
        seconds=wait_dt.second
    )
    
    print("Horários esperados de exibição:")
    for i in range(6):
        display_time = first_display + timedelta(seconds=i*10)
        print(f"  Visualization{i+1}: {display_time.strftime('%H:%M:%S')}")
    print()
    
    # Faz a requisição de agendamento
    payload = {
        'cpf': cpf,
        'entry_time': entry_time,
        'wait_time': wait_time
    }
    
    try:
        print("Enviando requisição de agendamento...")
        response = requests.post(WEBHOOK_URL, json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Agendamento realizado com sucesso!")
            print(f"Mensagem: {result.get('message')}")
            
            # Mostra status das visualizações
            print("\nStatus das visualizações:")
            for view in result.get('view_urls', []):
                status = "✅" if view['status'] == 'success' else "❌"
                print(f"  {status} {view['server']}: {view['url']}")
                if view.get('error'):
                    print(f"    Erro: {view['error']}")
        else:
            print(f"❌ Erro no agendamento: {response.status_code}")
            print(f"Resposta: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro ao fazer requisição: {e}")

def check_schedule_status():
    """Verifica o status dos agendamentos"""
    print(f"\n=== Status dos Agendamentos ===")
    
    try:
        response = requests.get(STATUS_URL, timeout=5)
        
        if response.status_code == 200:
            status = response.json()
            print(f"Total de jobs agendados: {status.get('total_jobs', 0)}")
            
            current_images = status.get('current_images', {})
            print("\nImagens atualmente exibidas:")
            for viz, cpf in current_images.items():
                if cpf:
                    print(f"  {viz}: {cpf}")
                else:
                    print(f"  {viz}: Nenhuma")
            
            scheduled_jobs = status.get('scheduled_jobs', {})
            if scheduled_jobs:
                print("\nJobs agendados:")
                for cpf, viz_schedule in scheduled_jobs.items():
                    print(f"  CPF {cpf}:")
                    for viz, job_info in viz_schedule.items():
                        scheduled_time = job_info.get('scheduled_time', 'N/A')
                        print(f"    {viz}: {scheduled_time}")
        else:
            print(f"❌ Erro ao obter status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro ao verificar status: {e}")

def test_multiple_schedules():
    """Testa múltiplos agendamentos"""
    print(f"\n=== Teste de Múltiplos Agendamentos ===")
    
    # Lista de agendamentos de teste
    schedules = [
        {"cpf": "11111111111", "entry_time": "20:00:00", "wait_time": "00:00:30"},
        {"cpf": "22222222222", "entry_time": "20:01:00", "wait_time": "00:00:30"},
        {"cpf": "33333333333", "entry_time": "20:02:00", "wait_time": "00:00:30"},
    ]
    
    for i, schedule in enumerate(schedules, 1):
        print(f"\n--- Agendamento {i} ---")
        print(f"CPF: {schedule['cpf']}")
        print(f"Entrada: {schedule['entry_time']}")
        print(f"Espera: {schedule['wait_time']}")
        
        try:
            response = requests.post(WEBHOOK_URL, json=schedule, timeout=10)
            if response.status_code == 200:
                print("✅ Agendado com sucesso")
            else:
                print(f"❌ Erro: {response.status_code}")
        except Exception as e:
            print(f"❌ Erro: {e}")

def main():
    """Função principal"""
    print("🚀 Teste do Sistema de Agendamento Baseado em DateTime")
    print("=" * 60)
    
    # Teste 1: Agendamento simples
    test_schedule()
    
    # Teste 2: Verificar status
    check_schedule_status()
    
    # Teste 3: Múltiplos agendamentos
    test_multiple_schedules()
    
    # Verificar status final
    check_schedule_status()
    
    print(f"\n✅ Testes concluídos!")
    print("\nPara monitorar em tempo real, acesse:")
    print("  - http://localhost:8083/view/ (Visualization1)")
    print("  - http://localhost:8084/view/ (Visualization2)")
    print("  - http://localhost:8085/view/ (Visualization3)")
    print("  - http://localhost:8086/view/ (Visualization4)")
    print("  - http://localhost:8087/view/ (Visualization5)")
    print("  - http://localhost:8088/view/ (Visualization6)")

if __name__ == "__main__":
    main() 