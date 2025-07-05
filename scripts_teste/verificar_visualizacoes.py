#!/usr/bin/env python3
"""
Script para verificar o status de todas as visualizações
"""

import requests
import json
import time

def verificar_visualizacoes():
    """Verifica o status de todas as visualizações"""
    
    print("=== VERIFICANDO STATUS DAS VISUALIZAÇÕES ===")
    print(f"Horário atual: {time.strftime('%H:%M:%S')}")
    print()
    
    # URLs dos servidores de visualização
    servers = [
        {"name": "visualization1", "url": "http://localhost:8083"},
        {"name": "visualization2", "url": "http://localhost:8084"},
        {"name": "visualization3", "url": "http://localhost:8085"},
        {"name": "visualization4", "url": "http://localhost:8086"},
        {"name": "visualization5", "url": "http://localhost:8087"},
        {"name": "visualization6", "url": "http://localhost:8088"}
    ]
    
    for server in servers:
        try:
            # Testa o endpoint de imagem atual
            current_url = f"{server['url']}/current-image"
            response = requests.get(current_url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                image_url = data.get('image_url')
                if image_url:
                    # Extrai o CPF da URL da imagem
                    cpf = image_url.split('/')[-1]
                    print(f"{server['name']}: {cpf}")
                else:
                    print(f"{server['name']}: Nenhuma imagem")
            else:
                print(f"{server['name']}: Erro {response.status_code}")
                
        except Exception as e:
            print(f"{server['name']}: Erro de conexão - {e}")

if __name__ == "__main__":
    verificar_visualizacoes() 