#!/usr/bin/env python3
"""
Teste rápido para verificar se as correções estão funcionando
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

def teste_rapido():
    """Teste rápido do sistema"""
    print("🚀 TESTE RÁPIDO - VERIFICAÇÃO DAS CORREÇÕES")
    print("="*50)
    print(f"⏰ Hora atual: {obter_hora_brasilia().strftime('%H:%M:%S')}")
    
    # 1. Verificar se o sistema está rodando
    try:
        response = requests.get(STATUS_URL, timeout=5)
        if response.status_code == 200:
            print("✅ Sistema está rodando")
        else:
            print(f"❌ Sistema não está respondendo: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao conectar: {str(e)}")
        return False
    
    # 2. Limpar eventos existentes
    try:
        response = requests.delete(f"{WEBHOOK_URL}eventos", timeout=5)
        if response.status_code == 200:
            print("✅ Eventos limpos")
        else:
            print(f"⚠️  Erro ao limpar eventos: {response.status_code}")
    except Exception as e:
        print(f"⚠️  Erro ao limpar eventos: {str(e)}")
    
    # 3. Enviar 3 webhooks rapidamente
    cpfs = ["11111111111", "22222222222", "33333333333"]
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
    
    # 4. Aguardar processamento
    print(f"\n⏳ Aguardando 3 segundos...")
    time.sleep(3)
    
    # 5. Verificar eventos criados
    try:
        response = requests.get(EVENTOS_URL, timeout=5)
        if response.status_code == 200:
            eventos = response.json()
            print(f"✅ {len(eventos)} eventos criados")
            
            # Analisar sequência
            if len(eventos) >= 18:  # 3 CPFs * 6 visualizações
                print("✅ Número correto de eventos")
                
                # Verificar se há gaps
                eventos_por_viz = {}
                for evento in eventos:
                    viz = evento['visualization']
                    if viz not in eventos_por_viz:
                        eventos_por_viz[viz] = []
                    eventos_por_viz[viz].append(evento)
                
                gaps_encontrados = 0
                for viz, eventos_viz in eventos_por_viz.items():
                    if len(eventos_viz) >= 2:
                        eventos_viz.sort(key=lambda x: x['hora_exibicao'])
                        
                        for i in range(len(eventos_viz) - 1):
                            fim_atual = eventos_viz[i]['hora_fim']
                            inicio_proximo = eventos_viz[i + 1]['hora_exibicao']
                            
                            if fim_atual > inicio_proximo:
                                gaps_encontrados += 1
                
                if gaps_encontrados == 0:
                    print("🎉 SEQUÊNCIA PERFEITA - CORREÇÕES FUNCIONANDO!")
                    return True
                else:
                    print(f"⚠️  {gaps_encontrados} gaps encontrados")
                    return False
            else:
                print(f"⚠️  Número incorreto de eventos: {len(eventos)}")
                return False
        else:
            print(f"❌ Erro ao listar eventos: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao verificar eventos: {str(e)}")
        return False

if __name__ == "__main__":
    resultado = teste_rapido()
    
    print(f"\n" + "="*50)
    if resultado:
        print("🎉 TESTE PASSOU - SISTEMA FUNCIONANDO!")
    else:
        print("❌ TESTE FALHOU - VERIFICAR PROBLEMAS")
    print("="*50) 