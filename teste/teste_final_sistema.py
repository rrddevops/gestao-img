#!/usr/bin/env python3
"""
Teste final completo do sistema após as correções
Verifica se cada visualização tem sua própria sequência independente
"""

import requests
import json
import time
from datetime import datetime, timedelta
import pytz

# Configurações
WEBHOOK_URL = "http://localhost:8000/webhook/"
EVENTOS_URL = "http://localhost:8000/webhook/eventos"
STATUS_URL = "http://localhost:8000/webhook/status"
TIMEZONE_BRASILIA = pytz.timezone('America/Sao_Paulo')

def obter_hora_brasilia():
    """Obtém a hora atual em Brasília"""
    return datetime.now(TIMEZONE_BRASILIA)

def verificar_status_sistema():
    """Verifica se o sistema está rodando"""
    try:
        response = requests.get(STATUS_URL)
        if response.status_code == 200:
            print("✅ Sistema está rodando")
            return True
        else:
            print(f"❌ Sistema não está respondendo: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao verificar status: {str(e)}")
        return False

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

def limpar_eventos():
    """Limpa todos os eventos do sistema"""
    try:
        response = requests.delete(f"{WEBHOOK_URL}eventos")
        if response.status_code == 200:
            print("✅ Todos os eventos foram limpos")
            return True
        else:
            print(f"❌ Erro ao limpar eventos: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao limpar eventos: {str(e)}")
        return False

def analisar_sequencia_perfeita(eventos):
    """Analisa se a sequência está perfeita (sem gaps)"""
    print("\n" + "="*80)
    print("ANÁLISE FINAL DA SEQUÊNCIA")
    print("="*80)
    
    if not eventos:
        print("❌ Nenhum evento para analisar")
        return False
    
    # Agrupar por visualização
    eventos_por_viz = {}
    for evento in eventos:
        viz = evento['visualization']
        if viz not in eventos_por_viz:
            eventos_por_viz[viz] = []
        eventos_por_viz[viz].append(evento)
    
    sequencia_perfeita = True
    total_gaps = 0
    
    for viz in sorted(eventos_por_viz.keys()):
        eventos_viz = eventos_por_viz[viz]
        print(f"\n📺 {viz.upper()}:")
        print("-" * 50)
        
        if len(eventos_viz) < 2:
            print(f"   ⚠️  Apenas {len(eventos_viz)} evento(s) - insuficiente para análise")
            continue
        
        # Ordenar por hora de exibição
        eventos_viz.sort(key=lambda x: x['hora_exibicao'])
        
        gaps_viz = 0
        for i in range(len(eventos_viz) - 1):
            evento_atual = eventos_viz[i]
            proximo_evento = eventos_viz[i + 1]
            
            # Converter horários
            fim_atual = datetime.strptime(evento_atual['hora_fim'], '%H:%M:%S').time()
            inicio_proximo = datetime.strptime(proximo_evento['hora_exibicao'], '%H:%M:%S').time()
            
            # Calcular gap
            fim_sec = fim_atual.hour * 3600 + fim_atual.minute * 60 + fim_atual.second
            inicio_sec = inicio_proximo.hour * 3600 + inicio_proximo.minute * 60 + inicio_proximo.second
            
            if inicio_sec < fim_sec:
                inicio_sec += 24 * 3600
            
            gap_segundos = inicio_sec - fim_sec
            
            if gap_segundos > 5:
                print(f"   ❌ Gap de {gap_segundos}s entre eventos {i+1} e {i+2}")
                gaps_viz += 1
                sequencia_perfeita = False
            else:
                print(f"   ✅ Gap de {gap_segundos}s entre eventos {i+1} e {i+2}")
        
        total_gaps += gaps_viz
        
        if gaps_viz == 0:
            print(f"   🎉 {viz}: Sequência PERFEITA!")
        else:
            print(f"   ⚠️  {viz}: {gaps_viz} gaps encontrados")
    
    print(f"\n📊 RESUMO FINAL:")
    print("-" * 30)
    print(f"   Total de visualizações: {len(eventos_por_viz)}")
    print(f"   Total de eventos: {len(eventos)}")
    print(f"   Total de gaps: {total_gaps}")
    
    if sequencia_perfeita:
        print(f"   🎉 SISTEMA FUNCIONANDO PERFEITAMENTE!")
        return True
    else:
        print(f"   ⚠️  SISTEMA COM PROBLEMAS - {total_gaps} gaps encontrados")
        return False

def testar_fluxo_completo():
    """Testa o fluxo completo do sistema"""
    print("🧪 TESTE FINAL COMPLETO DO SISTEMA")
    print("="*60)
    print(f"⏰ Hora atual (Brasília): {obter_hora_brasilia().strftime('%H:%M:%S')}")
    
    # 1. Verificar se o sistema está rodando
    print(f"\n1️⃣ Verificando status do sistema...")
    if not verificar_status_sistema():
        return False
    
    # 2. Limpar eventos existentes
    print(f"\n2️⃣ Limpando eventos existentes...")
    if not limpar_eventos():
        print("⚠️  Continuando mesmo com erro na limpeza...")
    
    # 3. Aguardar um pouco
    print(f"\n3️⃣ Aguardando 3 segundos...")
    time.sleep(3)
    
    # 4. Enviar sequência de webhooks
    cpfs_teste = [
        "11111111111",
        "22222222222", 
        "33333333333",
        "44444444444",
        "55555555555",
        "66666666666",
        "77777777777"
    ]
    
    print(f"\n4️⃣ Enviando {len(cpfs_teste)} webhooks...")
    sucessos = 0
    
    for i, cpf in enumerate(cpfs_teste, 1):
        print(f"\n   {i}/{len(cpfs_teste)} - Enviando webhook para CPF {cpf}...")
        if enviar_webhook(cpf):
            sucessos += 1
            time.sleep(0.5)  # Pequena pausa entre webhooks
        else:
            print(f"❌ Falha no webhook {i}")
    
    if sucessos < len(cpfs_teste):
        print(f"⚠️  Apenas {sucessos}/{len(cpfs_teste)} webhooks foram enviados com sucesso")
    
    # 5. Aguardar processamento
    print(f"\n5️⃣ Aguardando 5 segundos para processamento...")
    time.sleep(5)
    
    # 6. Analisar resultados
    print(f"\n6️⃣ Analisando resultados...")
    eventos = listar_eventos()
    
    if eventos:
        print(f"✅ {len(eventos)} eventos criados")
        return analisar_sequencia_perfeita(eventos)
    else:
        print("❌ Nenhum evento foi criado")
        return False

def main():
    """Função principal"""
    try:
        resultado = testar_fluxo_completo()
        
        print(f"\n" + "="*60)
        if resultado:
            print("🎉 TESTE FINAL: SUCESSO!")
            print("✅ O sistema está funcionando corretamente")
            print("✅ Cada visualização tem sua própria sequência")
            print("✅ Não há gaps entre eventos")
        else:
            print("❌ TESTE FINAL: FALHOU!")
            print("⚠️  O sistema ainda tem problemas")
            print("💡 Verifique os logs e tente novamente")
        
        print("="*60)
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {str(e)}")

if __name__ == "__main__":
    main() 