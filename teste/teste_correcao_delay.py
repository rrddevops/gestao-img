#!/usr/bin/env python3
"""
Teste para verificar se a correção do delay funcionou
"""

import requests
import json
import time
from datetime import datetime

def testar_correcao_delay():
    """
    Testa se a correção do delay funcionou
    """
    print("🧪 TESTE: Correção do Delay")
    print("=" * 40)
    
    # URL base
    base_url = "http://localhost:8000"
    
    # 1. Verificar se o sistema está rodando
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code != 200:
            print("❌ Sistema não está rodando")
            return False
        print("✅ Sistema está rodando")
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return False
    
    # 2. Enviar webhook de teste
    print("\n📤 Enviando webhook de teste...")
    
    webhook_data = {
        "cpf": "12345678901",
        "visualization": "visualization1",
        "tempo_inicial_segundos": 30,
        "incremento_segundos": 10,
        "duracao_exibicao_seg": 10
    }
    
    try:
        response = requests.post(
            f"{base_url}/webhook",
            json=webhook_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Webhook enviado com sucesso")
            print(f"   CPF: {result['cpf']}")
            print(f"   Eventos criados: {result['eventos_criados']}")
        else:
            print(f"❌ Erro no webhook: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao enviar webhook: {e}")
        return False
    
    # 3. Aguardar um pouco para os eventos serem processados
    print("\n⏳ Aguardando processamento...")
    time.sleep(2)
    
    # 4. Verificar os eventos criados
    print("\n📋 Verificando eventos criados...")
    
    try:
        response = requests.get(f"{base_url}/webhook/eventos/12345678901")
        
        if response.status_code == 200:
            eventos = response.json()
            
            if not eventos:
                print("❌ Nenhum evento encontrado")
                return False
            
            print(f"✅ {len(eventos)} eventos encontrados")
            
            # Verificar se os delays estão corretos
            delays_esperados = [30, 40, 50, 60, 70, 80]  # tempo_inicial + (i * incremento)
            
            for i, evento in enumerate(eventos):
                viz = evento['visualization']
                delay_str = evento['delay']
                
                # Extrair segundos do delay
                if ':' in delay_str:
                    parts = delay_str.split(':')
                    if len(parts) >= 3:
                        delay_seconds = float(parts[2])
                    else:
                        delay_seconds = float(delay_str)
                else:
                    delay_seconds = float(delay_str)
                
                delay_esperado = delays_esperados[i]
                
                print(f"   {viz}: delay={delay_seconds:.1f}s (esperado: {delay_esperado}s)")
                
                # Verificar se o delay está correto (com tolerância de 1 segundo)
                if abs(delay_seconds - delay_esperado) <= 1:
                    print(f"   ✅ Delay correto")
                else:
                    print(f"   ❌ Delay incorreto")
                    return False
            
            print("\n✅ Todos os delays estão corretos!")
            return True
            
        else:
            print(f"❌ Erro ao buscar eventos: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar eventos: {e}")
        return False

def testar_cenario_gap():
    """
    Testa especificamente o cenário de gap que estava causando problemas
    """
    print("\n🔍 TESTE ESPECÍFICO: Cenário de Gap")
    print("=" * 40)
    
    base_url = "http://localhost:8000"
    
    # 1. Enviar primeiro webhook
    print("📤 Enviando primeiro webhook...")
    
    webhook1 = {
        "cpf": "11111111111",
        "visualization": "visualization1",
        "tempo_inicial_segundos": 30,
        "incremento_segundos": 10,
        "duracao_exibicao_seg": 10
    }
    
    try:
        response = requests.post(f"{base_url}/webhook", json=webhook1)
        if response.status_code != 200:
            print("❌ Erro no primeiro webhook")
            return False
        print("✅ Primeiro webhook enviado")
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False
    
    # 2. Aguardar para criar um gap
    print("⏳ Aguardando 35 segundos para criar gap...")
    time.sleep(35)
    
    # 3. Enviar segundo webhook (que deveria usar tempo_inicial, não delay_inicial)
    print("📤 Enviando segundo webhook...")
    
    webhook2 = {
        "cpf": "22222222222",
        "visualization": "visualization1",
        "tempo_inicial_segundos": 30,
        "incremento_segundos": 10,
        "duracao_exibicao_seg": 10
    }
    
    try:
        response = requests.post(f"{base_url}/webhook", json=webhook2)
        if response.status_code != 200:
            print("❌ Erro no segundo webhook")
            return False
        print("✅ Segundo webhook enviado")
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False
    
    # 4. Verificar eventos
    print("📋 Verificando eventos...")
    time.sleep(2)
    
    try:
        response = requests.get(f"{base_url}/webhook/eventos/22222222222")
        if response.status_code == 200:
            eventos = response.json()
            
            if eventos:
                evento = eventos[0]  # Primeiro evento do segundo CPF
                delay_str = evento['delay']
                
                # Extrair segundos do delay
                if ':' in delay_str:
                    parts = delay_str.split(':')
                    delay_seconds = float(parts[2]) if len(parts) >= 3 else float(delay_str)
                else:
                    delay_seconds = float(delay_str)
                
                print(f"   Delay do segundo evento: {delay_seconds:.1f}s")
                
                # Deveria ser aproximadamente 30s (tempo_inicial), não 40s (delay_inicial)
                if 29 <= delay_seconds <= 31:
                    print("✅ Delay correto (usando tempo_inicial)")
                    return True
                else:
                    print(f"❌ Delay incorreto (deveria ser ~30s, mas é {delay_seconds:.1f}s)")
                    return False
            else:
                print("❌ Nenhum evento encontrado")
                return False
        else:
            print(f"❌ Erro ao buscar eventos: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando testes de correção do delay...")
    
    # Teste básico
    if testar_correcao_delay():
        print("\n✅ Teste básico passou!")
    else:
        print("\n❌ Teste básico falhou!")
        exit(1)
    
    # Teste específico do cenário de gap
    if testar_cenario_gap():
        print("\n✅ Teste de gap passou!")
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("✅ A correção do delay funcionou corretamente!")
    else:
        print("\n❌ Teste de gap falhou!")
        exit(1) 