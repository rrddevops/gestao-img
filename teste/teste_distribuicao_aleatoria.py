#!/usr/bin/env python3
"""
Script para testar a distribuição aleatória de CPFs entre visualizações
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

def listar_eventos():
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
            print("\n🕐 DISTRIBUIÇÃO POR VISUALIZAÇÃO:")
            print("=" * 80)
            
            for viz in sorted(viz_events.keys()):
                print(f"\n📺 {viz}:")
                for i, evento in enumerate(viz_events[viz], 1):
                    cpf = evento['cpf']
                    inicio = evento['hora_exibicao']
                    fim = evento['hora_fim']
                    print(f"   {i:2d}. CPF {cpf}: {inicio} → {fim}")
            
            # Mostrar estatísticas
            print(f"\n📊 ESTATÍSTICAS:")
            print("-" * 40)
            for viz in sorted(viz_events.keys()):
                count = len(viz_events[viz])
                cpfs = [e['cpf'] for e in viz_events[viz]]
                print(f"📺 {viz}: {count} eventos - CPFs: {', '.join(cpfs)}")
            
            return eventos
        else:
            print(f"❌ Erro ao listar eventos: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Erro: {e}")
        return []

def main():
    print("🎲 TESTE DE DISTRIBUIÇÃO ALEATÓRIA")
    print("=" * 50)
    
    # 1. Limpar eventos existentes
    print("\n1️⃣ Limpando eventos existentes...")
    limpar_eventos()
    
    # 2. Lista de CPFs para teste
    cpfs_teste = [
        "11111111111", "22222222222", "33333333333", 
        "44444444444", "55555555555", "66666666666",
        "77777777777", "88888888888", "99999999999",
        "00000000000", "12345678901", "98765432109"
    ]
    
    # 3. Enviar webhooks
    print(f"\n2️⃣ Enviando {len(cpfs_teste)} webhooks...")
    sucessos = 0
    for cpf in cpfs_teste:
        if enviar_webhook(cpf):
            sucessos += 1
        time.sleep(0.1)  # Pequena pausa entre webhooks
    
    print(f"\n✅ {sucessos}/{len(cpfs_teste)} webhooks enviados com sucesso")
    
    # 4. Listar eventos
    print("\n3️⃣ Listando distribuição dos eventos...")
    eventos = listar_eventos()
    
    # 5. Verificar distribuição
    print(f"\n4️⃣ ANÁLISE DA DISTRIBUIÇÃO:")
    print("-" * 40)
    
    if eventos:
        # Contar eventos por visualização
        viz_count = {}
        for evento in eventos:
            viz = evento['visualization']
            viz_count[viz] = viz_count.get(viz, 0) + 1
        
        print("📊 Eventos por visualização:")
        for viz in sorted(viz_count.keys()):
            count = viz_count[viz]
            print(f"   📺 {viz}: {count} eventos")
        
        # Verificar se a distribuição está balanceada
        counts = list(viz_count.values())
        if counts:
            min_count = min(counts)
            max_count = max(counts)
            diferenca = max_count - min_count
            
            print(f"\n⚖️  Balanceamento:")
            print(f"   Mínimo: {min_count} eventos")
            print(f"   Máximo: {max_count} eventos")
            print(f"   Diferença: {diferenca} eventos")
            
            if diferenca <= 2:
                print("   ✅ Distribuição bem balanceada!")
            elif diferenca <= 4:
                print("   ⚠️  Distribuição moderadamente balanceada")
            else:
                print("   ❌ Distribuição desbalanceada")
    
    print(f"\n✅ Teste concluído!")
    print("   Acesse: http://localhost/webhook/eventos para ver os eventos")

if __name__ == "__main__":
    main() 