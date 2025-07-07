#!/usr/bin/env python3
"""
Teste final para verificar se a lógica cronológica está funcionando corretamente
"""

import requests
import json
import time
from datetime import datetime
import pytz

# Configurações
WEBHOOK_URL = "http://localhost:8000/webhook/"
EVENTOS_URL = "http://localhost:8000/webhook/eventos"
SCHEDULER_STATUS_URL = "http://localhost:8000/scheduler/status"
TIMEZONE_BRASILIA = pytz.timezone('America/Sao_Paulo')

def obter_hora_brasilia():
    return datetime.now(TIMEZONE_BRASILIA)

def verificar_status_sistema():
    """Verifica se o sistema está rodando"""
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        return response.status_code == 200
    except:
        return False

def limpar_eventos():
    """Limpa todos os eventos"""
    try:
        response = requests.delete(EVENTOS_URL)
        return response.status_code == 200
    except:
        return False

def enviar_webhook(cpf):
    """Envia webhook para um CPF específico"""
    try:
        data = {"cpf": cpf}
        response = requests.post(WEBHOOK_URL, json=data)
        return response.status_code == 200, response.json()
    except Exception as e:
        return False, str(e)

def listar_eventos():
    """Lista todos os eventos"""
    try:
        response = requests.get(EVENTOS_URL)
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

def verificar_sequencia_cronologica(eventos):
    """Verifica se a sequência cronológica está correta"""
    print("\n=== VERIFICAÇÃO DA SEQUÊNCIA CRONOLÓGICA ===")
    
    # Agrupar eventos por visualização
    visualizacoes = {}
    for evento in eventos:
        viz = evento['visualization']
        if viz not in visualizacoes:
            visualizacoes[viz] = []
        visualizacoes[viz].append(evento)
    
    # Verificar cada visualização
    for viz, eventos_viz in visualizacoes.items():
        print(f"\n📺 {viz}:")
        
        # Ordenar por hora de exibição
        eventos_ordenados = sorted(eventos_viz, key=lambda x: x['hora_exibicao'])
        
        for i, evento in enumerate(eventos_ordenados):
            status = "✅" if i == 0 else "⏭️"
            print(f"  {status} {evento['cpf']} - {evento['hora_exibicao']} → {evento['hora_fim']}")
    
    # Verificar se não há sobreposições
    print("\n🔍 VERIFICANDO SOBREPOSIÇÕES:")
    for viz, eventos_viz in visualizacoes.items():
        eventos_ordenados = sorted(eventos_viz, key=lambda x: x['hora_exibicao'])
        
        for i in range(len(eventos_ordenados) - 1):
            evento_atual = eventos_ordenados[i]
            evento_proximo = eventos_ordenados[i + 1]
            
            if evento_atual['hora_fim'] > evento_proximo['hora_exibicao']:
                print(f"❌ SOBREPOSIÇÃO DETECTADA em {viz}:")
                print(f"   Evento {i+1} termina em {evento_atual['hora_fim']}")
                print(f"   Evento {i+2} começa em {evento_proximo['hora_exibicao']}")
                return False
        
        print(f"✅ {viz}: Sem sobreposições")

def main():
    print("🧪 TESTE FINAL - VERIFICAÇÃO DA LÓGICA CRONOLÓGICA")
    print("=" * 60)
    
    # Verificar se o sistema está rodando
    if not verificar_status_sistema():
        print("❌ Sistema não está rodando!")
        return
    
    print("✅ Sistema está rodando")
    
    # Limpar eventos existentes
    print("\n🧹 Limpando eventos existentes...")
    if limpar_eventos():
        print("✅ Eventos limpos")
    else:
        print("❌ Erro ao limpar eventos")
        return
    
    # Aguardar um pouco
    time.sleep(2)
    
    # Enviar primeiro webhook
    print("\n📤 Enviando primeiro webhook (CPF: 11111111111)...")
    sucesso, resposta = enviar_webhook("11111111111")
    if sucesso:
        print(f"✅ Webhook enviado: {resposta}")
    else:
        print(f"❌ Erro no webhook: {resposta}")
        return
    
    # Aguardar um pouco
    time.sleep(3)
    
    # Enviar segundo webhook
    print("\n📤 Enviando segundo webhook (CPF: 12345678901)...")
    sucesso, resposta = enviar_webhook("12345678901")
    if sucesso:
        print(f"✅ Webhook enviado: {resposta}")
    else:
        print(f"❌ Erro no webhook: {resposta}")
        return
    
    # Aguardar um pouco
    time.sleep(3)
    
    # Enviar terceiro webhook
    print("\n📤 Enviando terceiro webhook (CPF: 89778060037)...")
    sucesso, resposta = enviar_webhook("89778060037")
    if sucesso:
        print(f"✅ Webhook enviado: {resposta}")
    else:
        print(f"❌ Erro no webhook: {resposta}")
        return
    
    # Aguardar um pouco
    time.sleep(2)
    
    # Listar eventos
    print("\n📋 Listando eventos criados...")
    eventos = listar_eventos()
    if eventos:
        print(f"✅ {len(eventos)} eventos encontrados")
        
        # Verificar sequência cronológica
        verificar_sequencia_cronologica(eventos)
        
        # Mostrar status do scheduler
        print("\n📊 Status do Scheduler:")
        try:
            response = requests.get(SCHEDULER_STATUS_URL)
            if response.status_code == 200:
                status = response.json()
                print(f"   Running: {status.get('running', False)}")
                print(f"   Jobs: {status.get('jobs', 0)}")
                print(f"   Processed Events: {status.get('processed_events', 0)}")
                print(f"   Last Sent Images: {status.get('last_sent_images', 0)}")
        except:
            print("   ❌ Erro ao obter status do scheduler")
    else:
        print("❌ Nenhum evento encontrado")
    
    print("\n🎯 TESTE CONCLUÍDO!")

if __name__ == "__main__":
    main() 