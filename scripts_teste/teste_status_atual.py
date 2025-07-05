#!/usr/bin/env python3
"""
Script para testar o status atual de todos os servidores de visualização
"""

import requests
import json
from datetime import datetime
import pytz

# Configuração de timezone
TIMEZONE = pytz.timezone('America/Sao_Paulo')

def test_visualization_status():
    """Testa o status de todos os servidores de visualização"""
    
    # URLs dos servidores de visualização
    servers = [
        {"name": "visualization1", "url": "http://localhost:8083"},
        {"name": "visualization2", "url": "http://localhost:8084"},
        {"name": "visualization3", "url": "http://localhost:8085"},
        {"name": "visualization4", "url": "http://localhost:8086"},
        {"name": "visualization5", "url": "http://localhost:8087"},
        {"name": "visualization6", "url": "http://localhost:8088"}
    ]
    
    print("=== TESTE DE STATUS DOS SERVIDORES DE VISUALIZAÇÃO ===")
    print(f"Horário atual: {datetime.now(TIMEZONE).strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    for server in servers:
        print(f"--- {server['name'].upper()} ---")
        
        try:
            # Testa endpoint de configuração
            print("1. Testando configuração...")
            response = requests.get(f"{server['url']}/config", timeout=5)
            if response.status_code == 200:
                config = response.json()
                print(f"   ✓ Configuração: {config}")
            else:
                print(f"   ✗ Erro na configuração: {response.status_code}")
            
            # Testa endpoint de status do scheduler
            print("2. Testando status do scheduler...")
            response = requests.get(f"{server['url']}/schedule-status", timeout=5)
            if response.status_code == 200:
                status = response.json()
                print(f"   ✓ Status do scheduler: {status}")
            else:
                print(f"   ✗ Erro no status: {response.status_code}")
            
            # Testa endpoint de imagem atual
            print("3. Testando imagem atual...")
            response = requests.get(f"{server['url']}/current-image", timeout=5)
            if response.status_code == 200:
                current = response.json()
                print(f"   ✓ Imagem atual: {current}")
            else:
                print(f"   ✗ Erro na imagem atual: {response.status_code}")
            
            # Testa endpoint de detalhes do schedule
            print("4. Testando detalhes do schedule...")
            response = requests.get(f"{server['url']}/schedule-details", timeout=5)
            if response.status_code == 200:
                details = response.json()
                print(f"   ✓ Detalhes do schedule: {details}")
            else:
                print(f"   ✗ Erro nos detalhes: {response.status_code}")
                
        except Exception as e:
            print(f"   ✗ Erro de conexão: {e}")
        
        print()

def test_webhook():
    """Testa o webhook com um CPF de teste"""
    
    print("=== TESTE DO WEBHOOK ===")
    
    # CPF de teste (deve existir no banco)
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
        else:
            print(f"✗ Erro no webhook: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"✗ Erro ao testar webhook: {e}")

def test_database_config():
    """Testa a configuração no banco de dados"""
    
    print("=== TESTE DA CONFIGURAÇÃO NO BANCO ===")
    
    try:
        # Testa a configuração no primeiro servidor
        response = requests.get("http://localhost:8083/config", timeout=5)
        if response.status_code == 200:
            config = response.json()
            viz_config = config.get('visualization_config', {})
            
            print("Configurações no banco de dados:")
            for viz_name, viz_data in viz_config.items():
                print(f"  {viz_name}:")
                print(f"    - Porta: {viz_data.get('port')}")
                print(f"    - Delay: {viz_data.get('delay_seconds')}s")
                print(f"    - Display: {viz_data.get('display_seconds')}s")
                print(f"    - Ativo: {viz_data.get('is_active')}")
        else:
            print(f"✗ Erro ao obter configuração: {response.status_code}")
            
    except Exception as e:
        print(f"✗ Erro ao testar configuração: {e}")

if __name__ == "__main__":
    test_database_config()
    print()
    test_visualization_status()
    print()
    test_webhook() 