#!/usr/bin/env python3
"""
Script para testar as rotas do Flask
"""

import requests
import json

def test_routes():
    base_url = "http://localhost:8083"
    
    # Testa rota básica
    print("Testando rota /...")
    try:
        response = requests.get(f"{base_url}/")
        print(f"Status: {response.status_code}")
    except Exception as e:
        print(f"Erro: {e}")
    
    # Testa rota schedule-status
    print("\nTestando rota /schedule-status...")
    try:
        response = requests.get(f"{base_url}/schedule-status")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Dados: {json.dumps(data, indent=2)}")
    except Exception as e:
        print(f"Erro: {e}")
    
    # Testa rota schedule-details
    print("\nTestando rota /schedule-details...")
    try:
        response = requests.get(f"{base_url}/schedule-details")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Dados: {json.dumps(data, indent=2)}")
        else:
            print(f"Resposta: {response.text}")
    except Exception as e:
        print(f"Erro: {e}")
    
    # Testa rota queue-status
    print("\nTestando rota /queue-status...")
    try:
        response = requests.get(f"{base_url}/queue-status")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Dados: {json.dumps(data, indent=2)}")
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    test_routes() 