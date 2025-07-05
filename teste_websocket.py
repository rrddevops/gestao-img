#!/usr/bin/env python3
"""
Script para testar o sistema WebSocket
"""

import asyncio
import websockets
import json
import requests
from datetime import datetime
import pytz

# Configuração
TIMEZONE = pytz.timezone('America/Sao_Paulo')
WEBSOCKET_SERVER_URL = "ws://localhost:8765"
WEBHOOK_URL = "http://localhost:5002/webhook"

async def test_websocket_connection():
    """Testa conexão direta com o servidor WebSocket"""
    print("=" * 50)
    print("TESTE DE CONEXÃO WEBSOCKET")
    print("=" * 50)
    
    try:
        async with websockets.connect(WEBSOCKET_SERVER_URL) as websocket:
            print("✅ Conectado ao servidor WebSocket")
            
            # Envia comando de teste
            test_message = {
                'type': 'display_image',
                'cpf': '11111111111',
                'timestamp': datetime.now(TIMEZONE).isoformat()
            }
            
            await websocket.send(json.dumps(test_message))
            print("✅ Comando enviado via WebSocket")
            
            # Aguarda resposta
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"✅ Resposta recebida: {response}")
            except asyncio.TimeoutError:
                print("⚠️  Timeout aguardando resposta (pode ser normal)")
                
    except Exception as e:
        print(f"❌ Erro na conexão WebSocket: {e}")
        return False
    
    return True

def test_webhook_websocket():
    """Testa webhook que usa WebSocket"""
    print("\n" + "=" * 50)
    print("TESTE DE WEBHOOK COM WEBSOCKET")
    print("=" * 50)
    
    try:
        # Dados do teste
        test_data = {
            'cpf': '11111111112'
        }
        
        print(f"Enviando CPF {test_data['cpf']} via webhook...")
        
        # Faz requisição POST para o webhook
        response = requests.post(WEBHOOK_URL, json=test_data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Webhook executado com sucesso")
            print(f"📋 Resposta: {json.dumps(result, indent=2)}")
            
            # Verifica se usa WebSocket
            if 'websocket_result' in result:
                print("✅ WebSocket detectado na resposta")
            else:
                print("⚠️  WebSocket não detectado na resposta")
                
        else:
            print(f"❌ Erro no webhook: {response.status_code}")
            print(f"📋 Resposta: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro testando webhook: {e}")

def test_visualization_servers():
    """Testa se os servidores de visualização estão respondendo"""
    print("\n" + "=" * 50)
    print("TESTE DOS SERVIDORES DE VISUALIZAÇÃO")
    print("=" * 50)
    
    servers = [
        {'name': 'Visualization 1', 'url': 'http://localhost:8083'},
        {'name': 'Visualization 2', 'url': 'http://localhost:8084'},
        {'name': 'Visualization 3', 'url': 'http://localhost:8085'},
        {'name': 'Visualization 4', 'url': 'http://localhost:8086'},
        {'name': 'Visualization 5', 'url': 'http://localhost:8087'},
        {'name': 'Visualization 6', 'url': 'http://localhost:8088'}
    ]
    
    for server in servers:
        try:
            response = requests.get(f"{server['url']}/", timeout=5)
            if response.status_code == 200:
                print(f"✅ {server['name']} - Online")
            else:
                print(f"⚠️  {server['name']} - Status {response.status_code}")
        except Exception as e:
            print(f"❌ {server['name']} - Offline ({e})")

async def main():
    """Função principal"""
    print("🚀 INICIANDO TESTES DO SISTEMA WEBSOCKET")
    print(f"⏰ Horário: {datetime.now(TIMEZONE).strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Testa conexão WebSocket
    websocket_ok = await test_websocket_connection()
    
    # Testa webhook
    test_webhook_websocket()
    
    # Testa servidores de visualização
    test_visualization_servers()
    
    print("\n" + "=" * 50)
    print("RESUMO DOS TESTES")
    print("=" * 50)
    
    if websocket_ok:
        print("✅ Sistema WebSocket funcionando")
    else:
        print("❌ Sistema WebSocket com problemas")
    
    print("\n📝 Para verificar se as imagens estão sendo exibidas:")
    print("1. Acesse http://localhost:8083/view/")
    print("2. Acesse http://localhost:8084/view/")
    print("3. Acesse http://localhost:8085/view/")
    print("4. Acesse http://localhost:8086/view/")
    print("5. Acesse http://localhost:8087/view/")
    print("6. Acesse http://localhost:8088/view/")
    
    print("\n🔄 Para enviar mais testes:")
    print("curl -X POST http://localhost:5002/webhook -H 'Content-Type: application/json' -d '{\"cpf\":\"11111111111\"}'")
    print("curl -X POST http://localhost:5002/webhook -H 'Content-Type: application/json' -d '{\"cpf\":\"11111111112\"}'")
    print("curl -X POST http://localhost:5002/webhook -H 'Content-Type: application/json' -d '{\"cpf\":\"11111111113\"}'")

if __name__ == "__main__":
    asyncio.run(main()) 