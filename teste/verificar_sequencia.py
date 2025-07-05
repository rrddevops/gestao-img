#!/usr/bin/env python3
"""
Script para verificar a sequência de eventos de forma clara
"""

import requests
import json
from datetime import datetime

def verificar_sequencia():
    print("🔍 VERIFICANDO SEQUÊNCIA DE EVENTOS")
    print("=" * 60)
    
    # Buscar eventos
    response = requests.get("http://localhost:8000/webhook/eventos")
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
    
    # Mostrar sequência completa
    print("\n📋 SEQUÊNCIA COMPLETA DE EVENTOS:")
    print("-" * 60)
    
    for viz in sorted(viz_events.keys()):
        print(f"\n📺 {viz}:")
        for i, evento in enumerate(viz_events[viz], 1):
            cpf = evento['cpf']
            inicio = evento['hora_exibicao']
            fim = evento['hora_fim']
            print(f"   {i:2d}. CPF {cpf}: {inicio} → {fim}")
    
    # Verificar se não há sobreposições
    print("\n✅ VERIFICAÇÃO DE SOBREPOSIÇÕES:")
    print("-" * 60)
    
    for viz in sorted(viz_events.keys()):
        eventos_viz = viz_events[viz]
        print(f"\n📺 {viz}:")
        
        for i in range(len(eventos_viz) - 1):
            evento_atual = eventos_viz[i]
            evento_proximo = eventos_viz[i + 1]
            
            fim_atual = evento_atual['hora_fim']
            inicio_proximo = evento_proximo['hora_exibicao']
            
            # Converter para datetime para comparação
            fim_dt = datetime.strptime(fim_atual, "%H:%M:%S.%f")
            inicio_dt = datetime.strptime(inicio_proximo, "%H:%M:%S.%f")
            
            diferenca = (inicio_dt - fim_dt).total_seconds()
            
            if diferenca >= 0:
                print(f"   ✅ {evento_atual['cpf']} → {evento_proximo['cpf']}: {diferenca:.1f}s de intervalo")
            else:
                print(f"   ❌ {evento_atual['cpf']} → {evento_proximo['cpf']}: SOBREPOSIÇÃO!")
    
    # Verificar sequência por CPF
    print("\n📊 SEQUÊNCIA POR CPF:")
    print("-" * 60)
    
    cpfs = set(evento['cpf'] for evento in eventos)
    for cpf in sorted(cpfs):
        eventos_cpf = [e for e in eventos if e['cpf'] == cpf]
        eventos_cpf.sort(key=lambda x: x['hora_exibicao'])
        
        print(f"\n👤 CPF {cpf}:")
        for evento in eventos_cpf:
            viz = evento['visualization']
            inicio = evento['hora_exibicao']
            fim = evento['hora_fim']
            print(f"   📺 {viz}: {inicio} → {fim}")

if __name__ == "__main__":
    verificar_sequencia() 