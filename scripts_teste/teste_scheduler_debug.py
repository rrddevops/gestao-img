#!/usr/bin/env python3
"""
Script para testar e debugar o scheduler
"""

import requests
import json
from datetime import datetime
import pytz

# Configuração de timezone
TIMEZONE = pytz.timezone('America/Sao_Paulo')

def test_scheduler_debug():
    """Testa o debug do scheduler"""
    
    print("=== DEBUG DO SCHEDULER ===")
    print(f"Horário atual: {datetime.now(TIMEZONE).strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Testa cada servidor de visualização
    servers = [
        {"name": "visualization1", "url": "http://localhost:8083"},
        {"name": "visualization2", "url": "http://localhost:8084"},
        {"name": "visualization3", "url": "http://localhost:8085"},
        {"name": "visualization4", "url": "http://localhost:8086"},
        {"name": "visualization5", "url": "http://localhost:8087"},
        {"name": "visualization6", "url": "http://localhost:8088"}
    ]
    
    for server in servers:
        print(f"--- {server['name'].upper()} ---")
        
        try:
            # Testa status do scheduler
            print("1. Status do scheduler...")
            response = requests.get(f"{server['url']}/schedule-status", timeout=5)
            if response.status_code == 200:
                status = response.json()
                print(f"   ✓ Jobs agendados: {len(status.get('scheduled_jobs', {}))}")
                print(f"   ✓ Imagens atuais: {status.get('current_images', {})}")
            else:
                print(f"   ✗ Erro: {response.status_code}")
            
            # Força recarregamento dos agendamentos
            print("2. Forçando recarregamento...")
            response = requests.post(f"{server['url']}/reload-schedules", timeout=10)
            if response.status_code == 200:
                result = response.json()
                print(f"   ✓ Recarregamento: {result}")
            else:
                print(f"   ✗ Erro no recarregamento: {response.status_code}")
            
            # Testa status novamente
            print("3. Status após recarregamento...")
            response = requests.get(f"{server['url']}/schedule-status", timeout=5)
            if response.status_code == 200:
                status = response.json()
                print(f"   ✓ Jobs agendados: {len(status.get('scheduled_jobs', {}))}")
                print(f"   ✓ Imagens atuais: {status.get('current_images', {})}")
            else:
                print(f"   ✗ Erro: {response.status_code}")
                
        except Exception as e:
            print(f"   ✗ Erro de conexão: {e}")
        
        print()

def test_webhook_with_debug():
    """Testa o webhook com debug"""
    
    print("=== TESTE DO WEBHOOK COM DEBUG ===")
    
    # CPF de teste que existe no banco
    test_cpf = "12345678901"
    
    try:
        # Testa o webhook
        webhook_url = "http://localhost:5002/webhook"
        data = {"cpf": test_cpf}
        
        print(f"Enviando webhook para CPF: {test_cpf}")
        response = requests.post(webhook_url, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Webhook sucesso: {result}")
            
            # Aguarda um pouco e testa novamente
            print("Aguardando 5 segundos...")
            import time
            time.sleep(5)
            
            # Testa status dos servidores após webhook
            print("Testando status dos servidores após webhook...")
            for i in range(1, 7):
                url = f"http://localhost:808{i+2}/schedule-status"
                try:
                    response = requests.get(url, timeout=5)
                    if response.status_code == 200:
                        status = response.json()
                        print(f"  visualization{i}: {len(status.get('scheduled_jobs', {}))} jobs")
                    else:
                        print(f"  visualization{i}: erro {response.status_code}")
                except:
                    print(f"  visualization{i}: erro de conexão")
                    
        else:
            print(f"✗ Erro no webhook: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"✗ Erro ao testar webhook: {e}")

def test_manual_schedule():
    """Testa agendamento manual direto no servidor"""
    
    print("=== TESTE DE AGENDAMENTO MANUAL ===")
    
    # Testa agendamento direto no primeiro servidor
    test_cpf = "12345678901"
    entry_time = "13:00:00"
    wait_time = "00:00:30"
    
    try:
        url = "http://localhost:8083/schedule"
        data = {
            "cpf": test_cpf,
            "entry_time": entry_time,
            "wait_time": wait_time
        }
        
        print(f"Enviando agendamento manual para {test_cpf}")
        response = requests.post(url, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Agendamento manual sucesso: {result}")
        else:
            print(f"✗ Erro no agendamento manual: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"✗ Erro ao testar agendamento manual: {e}")

if __name__ == "__main__":
    test_scheduler_debug()
    print()
    test_webhook_with_debug()
    print()
    test_manual_schedule() 