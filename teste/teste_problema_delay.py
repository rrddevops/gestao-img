#!/usr/bin/env python3
"""
Teste para simular o problema do delay incorreto
"""

from datetime import datetime, time, timedelta

def simular_problema_delay():
    """
    Simula o problema do delay incorreto
    """
    print("🔍 SIMULAÇÃO DO PROBLEMA DE DELAY")
    print("=" * 50)
    
    # Parâmetros do sistema
    tempo_inicial = 30  # segundos
    incremento = 10     # segundos
    duracao_exibicao = 10  # segundos
    
    # Cenário: CPF 89778060037 enviado às 19:20:24
    hora_webhook = datetime.strptime("19:20:24", "%H:%M:%S").time()
    hora_webhook_dt = datetime.combine(datetime.today(), hora_webhook)
    
    print(f"📅 Webhook recebido às: {hora_webhook}")
    print(f"⚙️  Parâmetros: tempo_inicial={tempo_inicial}s, incremento={incremento}s")
    print()
    
    # Simular o que aconteceu para cada visualização
    visualizations = ["visualization1", "visualization2", "visualization3", 
                     "visualization4", "visualization5", "visualization6"]
    
    for i, viz in enumerate(visualizations):
        delay_inicial = tempo_inicial + (i * incremento)
        
        print(f"📺 {viz}:")
        print(f"   Delay calculado: {delay_inicial}s")
        
        # Simular o último evento desta visualização
        if viz == "visualization3":
            # Para visualization3, o último evento terminou às 19:20:29
            hora_fim_ultimo = datetime.strptime("19:20:29", "%H:%M:%S").time()
            hora_fim_ultimo_dt = datetime.combine(datetime.today(), hora_fim_ultimo)
            
            print(f"   Último evento terminou às: {hora_fim_ultimo}")
            
            # Calcular diferença
            diff = (hora_webhook_dt - hora_fim_ultimo_dt).total_seconds()
            print(f"   Diferença: {diff:.1f}s")
            
            if diff >= tempo_inicial:
                # PROBLEMA AQUI: Está usando delay_inicial (25s) ao invés de tempo_inicial (30s)
                hora_inicio_dt = hora_webhook_dt + timedelta(seconds=delay_inicial)
                print(f"   ❌ PROBLEMA: Usando delay_inicial ({delay_inicial}s) ao invés de tempo_inicial ({tempo_inicial}s)")
            else:
                hora_inicio_dt = hora_fim_ultimo_dt + timedelta(seconds=delay_inicial)
                print(f"   Usando: hora_fim_ultimo + delay_inicial")
            
            hora_exibicao = hora_inicio_dt.time()
            print(f"   Hora de exibição: {hora_exibicao}")
            
            # Calcular delay real
            delay_real = (hora_inicio_dt - hora_webhook_dt).total_seconds()
            print(f"   Delay real: {delay_real:.1f}s")
            
            # O que deveria ter acontecido
            hora_inicio_correto = hora_webhook_dt + timedelta(seconds=tempo_inicial)
            hora_exibicao_correto = hora_inicio_correto.time()
            print(f"   ✅ CORRETO seria: {hora_exibicao_correto} (delay: {tempo_inicial}s)")
            
        else:
            # Para outras visualizações, simular normalmente
            hora_inicio_dt = hora_webhook_dt + timedelta(seconds=delay_inicial)
            hora_exibicao = hora_inicio_dt.time()
            print(f"   Hora de exibição: {hora_exibicao}")
        
        print()

def explicar_solucao():
    """
    Explica a solução para o problema
    """
    print("🔧 SOLUÇÃO PARA O PROBLEMA")
    print("=" * 40)
    print()
    print("O problema está na lógica do webhook.py, linhas 95-105:")
    print()
    print("❌ LÓGICA ATUAL (INCORRETA):")
    print("   if diff >= tempo_inicial:")
    print("       hora_inicio_dt = agora_naive + timedelta(seconds=delay_inicial)")
    print()
    print("✅ LÓGICA CORRETA DEVERIA SER:")
    print("   if diff >= tempo_inicial:")
    print("       hora_inicio_dt = agora_naive + timedelta(seconds=tempo_inicial)")
    print()
    print("EXPLICAÇÃO:")
    print("- Quando há um gap >= tempo_inicial, significa que a visualização está 'livre'")
    print("- Neste caso, devemos usar apenas o tempo_inicial, não o delay_inicial")
    print("- O delay_inicial (que inclui incremento) só deve ser usado quando não há gap")
    print("- Isso garante que cada visualização mantenha sua sequência cronológica correta")

if __name__ == "__main__":
    simular_problema_delay()
    print()
    explicar_solucao() 