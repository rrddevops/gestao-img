#!/usr/bin/env python3
"""
Script para testar o sistema em tempo real
"""

import requests
import json
import time
from datetime import datetime

def testar_sistema_tempo_real():
    """Testa o sistema em tempo real"""
    
    print("=== TESTE DO SISTEMA EM TEMPO REAL ===")
    print("Enviando webhook e monitorando as visualizações...")
    print()
    
    # 1. Envia webhook
    cpf_teste = "22222222221"
    webhook_url = "http://localhost:5002/webhook"
    data = {"cpf": cpf_teste}
    
    try:
        print(f"1. Enviando webhook para CPF: {cpf_teste}")
        response = requests.post(webhook_url, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Webhook sucesso: {result['message']}")
            print(f"  Wait time: {result['wait_time']}")
            print()
        else:
            print(f"✗ Erro no webhook: {response.status_code}")
            return
            
    except Exception as e:
        print(f"✗ Erro ao enviar webhook: {e}")
        return
    
    # 2. Monitora as visualizações por 2 minutos
    print("2. Monitorando visualizações por 2 minutos...")
    print("   (Pressione Ctrl+C para parar)")
    print()
    
    start_time = time.time()
    duration = 120  # 2 minutos
    
    try:
        while time.time() - start_time < duration:
            current_time = datetime.now().strftime('%H:%M:%S')
            print(f"[{current_time}] Verificando visualizações...")
            
            # URLs dos servidores de visualização
            servers = [
                {"name": "visualization1", "url": "http://localhost:8083"},
                {"name": "visualization2", "url": "http://localhost:8084"},
                {"name": "visualization3", "url": "http://localhost:8085"},
                {"name": "visualization4", "url": "http://localhost:8086"},
                {"name": "visualization5", "url": "http://localhost:8087"},
                {"name": "visualization6", "url": "http://localhost:8088"}
            ]
            
            status_line = ""
            for server in servers:
                try:
                    current_url = f"{server['url']}/current-image"
                    response = requests.get(current_url, timeout=2)
                    
                    if response.status_code == 200:
                        data = response.json()
                        image_url = data.get('image_url')
                        if image_url:
                            cpf = image_url.split('/')[-1]
                            status_line += f"{server['name']}: {cpf} | "
                        else:
                            status_line += f"{server['name']}: --- | "
                    else:
                        status_line += f"{server['name']}: ERR | "
                        
                except Exception as e:
                    status_line += f"{server['name']}: ERR | "
            
            print(f"   {status_line}")
            
            # Aguarda 5 segundos antes da próxima verificação
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n\nTeste interrompido pelo usuário.")
    
    print("\n=== TESTE CONCLUÍDO ===")

if __name__ == "__main__":
    testar_sistema_tempo_real() 