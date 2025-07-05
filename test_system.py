#!/usr/bin/env python3
"""
Script de teste para o Sistema de Gerenciamento de Imagens
"""

import requests
import json
import time
import base64
from datetime import datetime

# Configurações
BASE_URL = "http://localhost:8000"
WEBHOOK_URL = f"{BASE_URL}/webhook/"
CADASTRO_URL = f"{BASE_URL}/cadastro/"

def test_cadastro():
    """Testa o cadastro de CPF e imagem"""
    print("🧪 Testando cadastro...")
    
    # Criar uma imagem de teste (1x1 pixel PNG)
    imagem_teste = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==")
    
    # Preparar dados do formulário
    files = {
        'imagem': ('teste.png', imagem_teste, 'image/png')
    }
    data = {
        'cpf': '12345678901'
    }
    
    try:
        response = requests.post(CADASTRO_URL, files=files, data=data)
        
        if response.status_code == 200:
            print("✅ Cadastro realizado com sucesso!")
            return True
        else:
            print(f"❌ Erro no cadastro: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False

def test_webhook():
    """Testa o webhook"""
    print("🧪 Testando webhook...")
    
    data = {
        'cpf': '12345678901'
    }
    
    try:
        response = requests.post(WEBHOOK_URL, json=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Webhook processado com sucesso!")
            print(f"   CPF: {result['cpf']}")
            print(f"   Hora de acesso: {result['hora_acesso']}")
            print(f"   Eventos criados: {result['eventos_criados']}")
            return True
        else:
            print(f"❌ Erro no webhook: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False

def test_websocket_status():
    """Testa o status do WebSocket"""
    print("🧪 Testando status do WebSocket...")
    
    try:
        response = requests.get(f"{BASE_URL}/websocket/status")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Status WebSocket: {result['total_connections']} conexões ativas")
            return True
        else:
            print(f"❌ Erro ao verificar status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False

def test_scheduler_status():
    """Testa o status do agendador"""
    print("🧪 Testando status do agendador...")
    
    try:
        response = requests.get(f"{BASE_URL}/scheduler/status")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Status do agendador: {'🟢 Ativo' if result['running'] else '🔴 Inativo'}")
            print(f"   Jobs ativos: {result['jobs']}")
            return True
        else:
            print(f"❌ Erro ao verificar agendador: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False

def test_eventos():
    """Testa a listagem de eventos"""
    print("🧪 Testando listagem de eventos...")
    
    try:
        response = requests.get(f"{BASE_URL}/webhook/eventos")
        
        if response.status_code == 200:
            eventos = response.json()
            print(f"✅ {len(eventos)} eventos encontrados")
            
            for evento in eventos[:3]:  # Mostrar apenas os 3 primeiros
                print(f"   - {evento['visualization']}: CPF {evento['cpf']} às {evento['hora_exibicao']}")
            
            return True
        else:
            print(f"❌ Erro ao listar eventos: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False

def test_visualizacoes():
    """Testa o acesso às páginas de visualização"""
    print("🧪 Testando páginas de visualização...")
    
    visualizacoes = ['visualization1', 'visualization2', 'visualization3']
    
    for viz in visualizacoes:
        try:
            response = requests.get(f"{BASE_URL}/{viz}")
            
            if response.status_code == 200:
                print(f"✅ {viz}: Acessível")
            else:
                print(f"❌ {viz}: Erro {response.status_code}")
                
        except Exception as e:
            print(f"❌ {viz}: Erro de conexão - {e}")

def main():
    """Função principal de teste"""
    print("🚀 Iniciando testes do Sistema de Gerenciamento de Imagens")
    print("=" * 60)
    
    # Aguardar um pouco para o sistema inicializar
    print("⏳ Aguardando inicialização do sistema...")
    time.sleep(5)
    
    # Testes
    tests = [
        ("Status do Agendador", test_scheduler_status),
        ("Status do WebSocket", test_websocket_status),
        ("Cadastro", test_cadastro),
        ("Webhook", test_webhook),
        ("Eventos", test_eventos),
        ("Visualizações", test_visualizacoes),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 40)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
            results.append((test_name, False))
    
    # Resumo
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Resultado: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 Todos os testes passaram! Sistema funcionando corretamente.")
    else:
        print("⚠️  Alguns testes falharam. Verifique os logs acima.")
    
    print("\n🌐 URLs do sistema:")
    print(f"   Página inicial: {BASE_URL}")
    print(f"   Documentação API: {BASE_URL}/docs")
    print(f"   Cadastro: {BASE_URL}/cadastro")
    print(f"   Visualização 1: {BASE_URL}/visualization1")
    print(f"   Visualização 2: {BASE_URL}/visualization2")
    print(f"   Visualização 3: {BASE_URL}/visualization3")

if __name__ == "__main__":
    main() 