#!/usr/bin/env python3
"""
Teste para verificar se cada visualização tem sua própria sequência independente
"""

import requests
import json
import time
from datetime import datetime
import pytz

# Configurações
WEBHOOK_URL = "http://localhost:8000/webhook/"
EVENTOS_URL = "http://localhost:8000/webhook/eventos"
TIMEZONE_BRASILIA = pytz.timezone('America/Sao_Paulo')

def obter_hora_brasilia():
    """Obtém a hora atual em Brasília"""
    return datetime.now(TIMEZONE_BRASILIA)

def enviar_webhook(cpf):
    """Envia webhook para um CPF"""
    try:
        payload = {"cpf": cpf}
        response = requests.post(WEBHOOK_URL, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Webhook enviado para CPF {cpf}: {result['message']}")
            return True
        else:
            print(f"❌ Erro ao enviar webhook para CPF {cpf}: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erro de conexão para CPF {cpf}: {str(e)}")
        return False

def listar_eventos():
    """Lista todos os eventos"""
    try:
        response = requests.get(EVENTOS_URL)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Erro ao listar eventos: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Erro de conexão ao listar eventos: {str(e)}")
        return []

def analisar_sequencia_eventos(eventos):
    """Analisa a sequência de eventos por visualização"""
    print("\n" + "="*80)
    print("ANÁLISE DA SEQUÊNCIA DE EVENTOS POR VISUALIZAÇÃO")
    print("="*80)
    
    # Agrupar eventos por visualização
    eventos_por_visualizacao = {}
    for evento in eventos:
        viz = evento['visualization']
        if viz not in eventos_por_visualizacao:
            eventos_por_visualizacao[viz] = []
        eventos_por_visualizacao[viz].append(evento)
    
    # Analisar cada visualização
    for viz in sorted(eventos_por_visualizacao.keys()):
        eventos_viz = eventos_por_visualizacao[viz]
        print(f"\n📺 {viz.upper()}:")
        print("-" * 60)
        
        if len(eventos_viz) == 0:
            print("   Nenhum evento encontrado")
            continue
        
        # Ordenar por hora de exibição
        eventos_viz.sort(key=lambda x: x['hora_exibicao'])
        
        for i, evento in enumerate(eventos_viz):
            print(f"   {i+1:2d}. CPF: {evento['cpf']} | Exibição: {evento['hora_exibicao']} | Fim: {evento['hora_fim']}")
        
        # Verificar se há gaps
        print(f"\n   📊 Análise de gaps:")
        gaps_encontrados = 0
        
        for i in range(len(eventos_viz) - 1):
            evento_atual = eventos_viz[i]
            proximo_evento = eventos_viz[i + 1]
            
            # Converter horários para análise
            fim_atual = datetime.strptime(evento_atual['hora_fim'], '%H:%M:%S').time()
            inicio_proximo = datetime.strptime(proximo_evento['hora_exibicao'], '%H:%M:%S').time()
            
            # Calcular diferença em segundos
            fim_sec = fim_atual.hour * 3600 + fim_atual.minute * 60 + fim_atual.second
            inicio_sec = inicio_proximo.hour * 3600 + inicio_proximo.minute * 60 + inicio_proximo.second
            
            # Ajustar para mudança de hora se necessário
            if inicio_sec < fim_sec:
                inicio_sec += 24 * 3600  # Adicionar 24 horas
            
            gap_segundos = inicio_sec - fim_sec
            
            if gap_segundos > 5:  # Gap maior que 5 segundos
                print(f"      ⚠️  Gap detectado: {gap_segundos}s entre eventos {i+1} e {i+2}")
                gaps_encontrados += 1
            else:
                print(f"      ✅ Sequência contínua entre eventos {i+1} e {i+2} (gap: {gap_segundos}s)")
        
        if gaps_encontrados == 0:
            print(f"   🎉 {viz}: Sequência contínua sem gaps!")
        else:
            print(f"   ⚠️  {viz}: {gaps_encontrados} gaps encontrados")

def main():
    """Função principal do teste"""
    print("🧪 TESTE DE SEQUÊNCIA INDIVIDUAL POR VISUALIZAÇÃO")
    print("="*60)
    print(f"⏰ Hora atual (Brasília): {obter_hora_brasilia().strftime('%H:%M:%S')}")
    
    # Lista de CPFs para teste
    cpfs_teste = [
        "11111111111",
        "22222222222", 
        "33333333333",
        "44444444444",
        "55555555555"
    ]
    
    print(f"\n📋 Enviando {len(cpfs_teste)} webhooks...")
    
    # Enviar webhooks
    for i, cpf in enumerate(cpfs_teste, 1):
        print(f"\n{i}/{len(cpfs_teste)} - Enviando webhook para CPF {cpf}...")
        sucesso = enviar_webhook(cpf)
        
        if sucesso:
            # Aguardar um pouco entre webhooks
            time.sleep(1)
        else:
            print("❌ Parando teste devido a erro")
            return
    
    print(f"\n⏳ Aguardando 5 segundos para processamento...")
    time.sleep(5)
    
    # Listar e analisar eventos
    print(f"\n📊 Obtendo eventos do sistema...")
    eventos = listar_eventos()
    
    if eventos:
        print(f"✅ {len(eventos)} eventos encontrados")
        analisar_sequencia_eventos(eventos)
    else:
        print("❌ Nenhum evento encontrado")
    
    print(f"\n🏁 Teste concluído!")

if __name__ == "__main__":
    main() 