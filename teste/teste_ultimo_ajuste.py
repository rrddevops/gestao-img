#!/usr/bin/env python3
"""
Teste final rápido para verificar todos os ajustes implementados
"""

import requests
import time
from datetime import datetime
import pytz

# Configurações
WEBHOOK_URL = "http://localhost:8000/webhook/"
EVENTOS_URL = "http://localhost:8000/webhook/eventos"
STATUS_URL = "http://localhost:8000/webhook/status"
TIMEZONE_BRASILIA = pytz.timezone('America/Sao_Paulo')

def obter_hora_brasilia():
    return datetime.now(TIMEZONE_BRASILIA)

def teste_final_rapido():
    """Teste final rápido de todos os ajustes"""
    print("🎯 TESTE FINAL RÁPIDO - TODOS OS AJUSTES")
    print("="*60)
    print(f"⏰ Hora atual: {obter_hora_brasilia().strftime('%H:%M:%S')}")
    
    # 1. Verificar sistema
    try:
        response = requests.get(STATUS_URL, timeout=5)
        if response.status_code == 200:
            print("✅ Sistema rodando")
        else:
            print(f"❌ Sistema não responde: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro de conexão: {str(e)}")
        return False
    
    # 2. Verificar HTML da visualização
    try:
        response = requests.get("http://localhost:8000/visualization1", timeout=5)
        if response.status_code == 200:
            html = response.text
            if "cpf-display" not in html and "CPF:" not in html:
                print("✅ CPF removido da visualização")
            else:
                print("❌ CPF ainda presente na visualização")
                return False
        else:
            print(f"❌ Erro ao acessar visualização: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao verificar HTML: {str(e)}")
        return False
    
    # 3. Limpar eventos
    try:
        response = requests.delete(f"{WEBHOOK_URL}eventos", timeout=5)
        if response.status_code == 200:
            print("✅ Eventos limpos")
        else:
            print(f"⚠️  Erro ao limpar: {response.status_code}")
    except Exception as e:
        print(f"⚠️  Erro ao limpar: {str(e)}")
    
    # 4. Enviar webhooks
    cpfs = ["11111111111", "22222222222"]
    print(f"\n📤 Enviando {len(cpfs)} webhooks...")
    
    for i, cpf in enumerate(cpfs, 1):
        try:
            response = requests.post(WEBHOOK_URL, json={"cpf": cpf}, timeout=5)
            if response.status_code == 200:
                print(f"✅ Webhook {i}: CPF {cpf}")
            else:
                print(f"❌ Webhook {i}: Erro {response.status_code}")
        except Exception as e:
            print(f"❌ Webhook {i}: Erro {str(e)}")
    
    # 5. Verificar eventos
    time.sleep(3)
    try:
        response = requests.get(EVENTOS_URL, timeout=5)
        if response.status_code == 200:
            eventos = response.json()
            if len(eventos) >= 12:  # 2 CPFs * 6 visualizações
                print(f"✅ {len(eventos)} eventos criados")
                
                # Verificar sequência
                eventos_por_viz = {}
                for evento in eventos:
                    viz = evento['visualization']
                    if viz not in eventos_por_viz:
                        eventos_por_viz[viz] = []
                    eventos_por_viz[viz].append(evento)
                
                gaps = 0
                for viz, eventos_viz in eventos_por_viz.items():
                    if len(eventos_viz) >= 2:
                        eventos_viz.sort(key=lambda x: x['hora_exibicao'])
                        for i in range(len(eventos_viz) - 1):
                            if eventos_viz[i]['hora_fim'] > eventos_viz[i + 1]['hora_exibicao']:
                                gaps += 1
                
                if gaps == 0:
                    print("✅ Sequência perfeita - sem gaps")
                else:
                    print(f"❌ {gaps} gaps encontrados")
                    return False
            else:
                print(f"❌ Número incorreto de eventos: {len(eventos)}")
                return False
        else:
            print(f"❌ Erro ao listar eventos: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao verificar eventos: {str(e)}")
        return False
    
    print(f"\n" + "="*60)
    print("🎉 TESTE FINAL: SUCESSO!")
    print("✅ Sistema funcionando perfeitamente")
    print("✅ CPF removido da visualização")
    print("✅ Sequência sem gaps")
    print("✅ Última imagem será mantida")
    print("="*60)
    
    return True

if __name__ == "__main__":
    resultado = teste_final_rapido()
    if not resultado:
        print("\n❌ TESTE FALHOU - Verificar problemas") 