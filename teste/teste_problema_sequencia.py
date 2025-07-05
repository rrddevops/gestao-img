#!/usr/bin/env python3
"""
Script para testar e reproduzir o problema de sequência
"""

import requests
import time
import json
from datetime import datetime

def limpar_eventos():
    """Limpa todos os eventos existentes"""
    try:
        response = requests.delete("http://localhost:8000/webhook/eventos")
        if response.status_code == 200:
            print("✅ Eventos limpos")
        else:
            print("❌ Erro ao limpar eventos")
    except Exception as e:
        print(f"❌ Erro: {e}")

def enviar_webhook(cpf):
    """Envia webhook para um CPF específico"""
    try:
        data = {"cpf": cpf}
        response = requests.post("http://localhost:8000/webhook/", json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ CPF {cpf}: {result['message']}")
            return True
        else:
            print(f"❌ CPF {cpf}: Erro {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao enviar webhook para {cpf}: {e}")
        return False

def listar_eventos_ativos():
    """Lista eventos ativos no momento"""
    try:
        response = requests.get("http://localhost:8000/webhook/eventos")
        if response.status_code == 200:
            eventos = response.json()
            
            # Filtrar eventos ativos (hora atual)
            hora_atual = datetime.now().time()
            eventos_ativos = []
            
            for evento in eventos:
                hora_exibicao = datetime.strptime(evento['hora_exibicao'], "%H:%M:%S.%f").time()
                hora_fim = datetime.strptime(evento['hora_fim'], "%H:%M:%S.%f").time()
                
                if hora_exibicao <= hora_atual <= hora_fim:
                    eventos_ativos.append(evento)
            
            print(f"\n🕐 Eventos Ativos ({len(eventos_ativos)}):")
            print("-" * 60)
            
            for evento in eventos_ativos:
                print(f"📺 {evento['visualization']}: CPF {evento['cpf']} - {evento['hora_exibicao']} → {evento['hora_fim']}")
            
            return eventos_ativos
        else:
            print(f"❌ Erro ao listar eventos: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Erro: {e}")
        return []

def listar_todos_eventos():
    """Lista todos os eventos organizados por visualização"""
    try:
        response = requests.get("http://localhost:8000/webhook/eventos")
        if response.status_code == 200:
            eventos = response.json()
            
            # Organizar por visualização
            viz_events = {}
            for evento in eventos:
                viz = evento['visualization']
                if viz not in viz_events:
                    viz_events[viz] = []
                viz_events[viz].append(evento)
            
            # Ordenar cada visualização por hora de exibição
            for viz in viz_events:
                viz_events[viz].sort(key=lambda x: x['hora_exibicao'])
            
            print(f"\n📋 Total de eventos: {len(eventos)}")
            print("\n🕐 TODOS OS EVENTOS POR VISUALIZAÇÃO:")
            print("=" * 80)
            
            for viz in sorted(viz_events.keys()):
                print(f"\n📺 {viz}:")
                for i, evento in enumerate(viz_events[viz], 1):
                    cpf = evento['cpf']
                    inicio = evento['hora_exibicao']
                    fim = evento['hora_fim']
                    print(f"   {i:2d}. CPF {cpf}: {inicio} → {fim}")
            
            return eventos
        else:
            print(f"❌ Erro ao listar eventos: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Erro: {e}")
        return []

def verificar_status_scheduler():
    """Verifica o status do scheduler"""
    try:
        response = requests.get("http://localhost:8000/scheduler/status")
        if response.status_code == 200:
            status = response.json()
            print(f"\n📊 Status do Scheduler:")
            print(f"   Running: {status.get('running', 'N/A')}")
            print(f"   Jobs: {status.get('jobs', 'N/A')}")
            print(f"   Cache Size: {status.get('cache_size', 'N/A')}")
            print(f"   Next Run: {status.get('next_run_time', 'N/A')}")
            return status
        else:
            print(f"❌ Erro ao verificar status: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

def main():
    print("🧪 TESTE DE PROBLEMA DE SEQUÊNCIA")
    print("=" * 50)
    
    # 1. Limpar eventos existentes
    print("\n1️⃣ Limpando eventos existentes...")
    limpar_eventos()
    
    # 2. Lista de 5 CPFs para teste
    cpfs_teste = [
        "11111111111", "22222222222", "33333333333", "44444444444", "55555555555"
    ]
    
    # 3. Enviar webhooks
    print(f"\n2️⃣ Enviando {len(cpfs_teste)} webhooks...")
    sucessos = 0
    for i, cpf in enumerate(cpfs_teste, 1):
        if enviar_webhook(cpf):
            sucessos += 1
        print(f"   Progresso: {i}/{len(cpfs_teste)}")
        time.sleep(0.1)  # Pequena pausa entre webhooks
    
    print(f"\n✅ {sucessos}/{len(cpfs_teste)} webhooks enviados com sucesso")
    
    # 4. Listar todos os eventos
    print("\n3️⃣ Listando todos os eventos...")
    eventos = listar_todos_eventos()
    
    # 5. Verificar status do scheduler
    print("\n4️⃣ Verificando status do scheduler...")
    status = verificar_status_scheduler()
    
    # 6. Monitorar eventos ativos por 30 segundos
    print("\n5️⃣ Monitorando eventos ativos por 30 segundos...")
    for i in range(30):
        print(f"\n   Segundo {i+1}/30...")
        eventos_ativos = listar_eventos_ativos()
        
        # Se não há eventos ativos, mostrar que está vazio
        if not eventos_ativos:
            print("   ⚠️  Nenhum evento ativo no momento")
        
        time.sleep(1)
    
    print(f"\n✅ Teste concluído!")
    print("   Acesse: http://localhost/webhook/eventos para ver todos os eventos")

if __name__ == "__main__":
    main() 