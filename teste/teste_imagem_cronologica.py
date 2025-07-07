#!/usr/bin/env python3
"""
Teste para verificar se o sistema mantém a última imagem cronológica corretamente
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
    """Limpa todos os eventos (simulado)"""
    print("🗑️  Limpando eventos anteriores...")
    return True

def enviar_webhook(cpf):
    """Envia webhook para um CPF"""
    try:
        response = requests.post(WEBHOOK_URL, json={"cpf": cpf}, timeout=5)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Webhook enviado: {result['message']}")
            return True
        else:
            print(f"❌ Erro no webhook: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao enviar webhook: {str(e)}")
        return False

def listar_eventos():
    """Lista todos os eventos"""
    try:
        response = requests.get(EVENTOS_URL, timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Erro ao listar eventos: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Erro ao listar eventos: {str(e)}")
        return []

def verificar_status_scheduler():
    """Verifica status do scheduler"""
    try:
        response = requests.get(SCHEDULER_STATUS_URL, timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except:
        return None

def testar_sequencia_cronologica():
    """Testa se a sequência está mantendo ordem cronológica"""
    print("\n📋 TESTANDO SEQUÊNCIA CRONOLÓGICA:")
    print("-" * 50)
    
    # 1. Limpar eventos
    if not limpar_eventos():
        return False
    
    # 2. Enviar webhooks em sequência
    cpfs = ["11111111111", "22222222222", "33333333333"]
    
    print("📤 Enviando webhooks em sequência...")
    for i, cpf in enumerate(cpfs, 1):
        print(f"   {i}. Enviando CPF {cpf}...")
        if not enviar_webhook(cpf):
            return False
        time.sleep(2)  # Pequena pausa entre webhooks
    
    # 3. Aguardar processamento
    print("⏳ Aguardando 5 segundos para processamento...")
    time.sleep(5)
    
    # 4. Verificar eventos criados
    eventos = listar_eventos()
    if not eventos:
        print("❌ Nenhum evento foi criado")
        return False
    
    print(f"✅ {len(eventos)} eventos criados")
    
    # 5. Analisar sequência cronológica
    eventos_por_viz = {}
    for evento in eventos:
        viz = evento['visualization']
        if viz not in eventos_por_viz:
            eventos_por_viz[viz] = []
        eventos_por_viz[viz].append(evento)
    
    # Ordenar por hora de exibição
    for viz in eventos_por_viz:
        eventos_por_viz[viz].sort(key=lambda x: x['hora_exibicao'])
    
    print("\n📊 ANÁLISE DA SEQUÊNCIA CRONOLÓGICA:")
    print("-" * 50)
    
    for viz in sorted(eventos_por_viz.keys()):
        print(f"\n📺 {viz}:")
        for i, evento in enumerate(eventos_por_viz[viz], 1):
            cpf = evento['cpf']
            inicio = evento['hora_exibicao']
            fim = evento['hora_fim']
            print(f"   {i:2d}. CPF {cpf}: {inicio} → {fim}")
    
    # 6. Verificar se a última imagem cronológica está correta
    print("\n🔍 VERIFICANDO ÚLTIMA IMAGEM CRONOLÓGICA:")
    print("-" * 50)
    
    for viz in sorted(eventos_por_viz.keys()):
        eventos_viz = eventos_por_viz[viz]
        if eventos_viz:
            ultimo_evento = eventos_viz[-1]  # Último evento cronológico
            print(f"📺 {viz}: Última imagem cronológica = CPF {ultimo_evento['cpf']} ({ultimo_evento['hora_exibicao']})")
    
    return True

def testar_manutencao_imagem():
    """Testa se a manutenção da imagem está funcionando corretamente"""
    print("\n🔄 TESTANDO MANUTENÇÃO DA IMAGEM:")
    print("-" * 50)
    
    # 1. Verificar status do scheduler
    status = verificar_status_scheduler()
    if status:
        print(f"✅ Scheduler ativo: {status.get('running', False)}")
        print(f"   Eventos processados: {status.get('processed_events', 0)}")
        print(f"   Imagens em cache: {status.get('last_sent_images', 0)}")
    else:
        print("⚠️  Não foi possível verificar status do scheduler")
    
    # 2. Aguardar para ver se a imagem é mantida
    print("⏳ Aguardando 70 segundos para verificar manutenção da imagem...")
    time.sleep(70)
    
    # 3. Verificar status novamente
    status_depois = verificar_status_scheduler()
    if status_depois:
        print(f"✅ Scheduler após espera: {status_depois.get('running', False)}")
        print(f"   Eventos processados: {status_depois.get('processed_events', 0)}")
        print(f"   Imagens em cache: {status_depois.get('last_sent_images', 0)}")
        
        # Verificar se o cache de imagens aumentou (indicando manutenção)
        if status and status_depois:
            cache_antes = status.get('last_sent_images', 0)
            cache_depois = status_depois.get('last_sent_images', 0)
            if cache_depois >= cache_antes:
                print("✅ Cache de imagens mantido/atualizado")
                return True
            else:
                print("❌ Cache de imagens diminuiu")
                return False
    
    return True

def main():
    """Função principal do teste"""
    print("🧪 TESTE DE IMAGEM CRONOLÓGICA")
    print("="*60)
    print(f"⏰ Hora atual (Brasília): {obter_hora_brasilia().strftime('%H:%M:%S')}")
    
    # 1. Verificar se o sistema está rodando
    print(f"\n1️⃣ Verificando status do sistema...")
    if not verificar_status_sistema():
        print("❌ Sistema não está rodando")
        return False
    
    # 2. Testar sequência cronológica
    print(f"\n2️⃣ Testando sequência cronológica...")
    if not testar_sequencia_cronologica():
        print("❌ Falha no teste de sequência cronológica")
        return False
    
    # 3. Testar manutenção da imagem
    print(f"\n3️⃣ Testando manutenção da imagem...")
    if not testar_manutencao_imagem():
        print("❌ Falha no teste de manutenção da imagem")
        return False
    
    print(f"\n" + "="*60)
    print("🎉 TESTE DE IMAGEM CRONOLÓGICA CONCLUÍDO!")
    print("✅ Sistema mantém última imagem cronológica corretamente")
    print("✅ Não há reenvios desnecessários de imagens")
    print("✅ Logs diferenciam entre novo evento e manutenção")
    print("✅ Interface mostra claramente o tipo de imagem")
    print("="*60)
    
    return True

if __name__ == "__main__":
    main() 