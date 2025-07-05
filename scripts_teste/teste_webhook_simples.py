#!/usr/bin/env python3
"""
Script simples para testar o webhook
"""

import requests
import json

def testar_webhook():
    """Testa o webhook com um CPF"""
    
    cpf_teste = "22222222221"
    
    print(f"=== TESTANDO WEBHOOK COM CPF: {cpf_teste} ===")
    
    try:
        # Testa o webhook
        webhook_url = "http://localhost:5002/webhook"
        data = {"cpf": cpf_teste}
        
        print("Enviando webhook...")
        response = requests.post(webhook_url, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Webhook sucesso: {result}")
        else:
            print(f"✗ Erro no webhook: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"✗ Erro ao testar webhook: {e}")

if __name__ == "__main__":
    testar_webhook() 