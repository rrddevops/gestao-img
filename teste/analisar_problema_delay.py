#!/usr/bin/env python3
"""
Script para analisar detalhadamente o problema dos delays incorretos
"""

from datetime import datetime, time, timedelta

def analisar_problema_delay():
    """
    Analisa o problema dos delays incorretos
    """
    print("🔍 ANÁLISE DETALHADA DO PROBLEMA DE DELAY")
    print("=" * 60)
    
    # Parâmetros do sistema
    tempo_inicial = 30  # segundos
    incremento = 10     # segundos
    duracao_exibicao = 10  # segundos
    
    print(f"⚙️  Parâmetros: tempo_inicial={tempo_inicial}s, incremento={incremento}s")
    print()
    
    # Analisar cada grupo de eventos
    print("📊 ANÁLISE DOS EVENTOS:")
    print("-" * 60)
    
    # Grupo 1: 847-852 (12345678901 às 19:31:43)
    print("Grupo 1: CPF 12345678901 às 19:31:43")
    hora_webhook1 = datetime.strptime("19:31:43", "%H:%M:%S").time()
    hora_webhook1_dt = datetime.combine(datetime.today(), hora_webhook1)
    
    for i, viz in enumerate(["visualization1", "visualization2", "visualization3", "visualization4", "visualization5", "visualization6"]):
        delay_inicial = tempo_inicial + (i * incremento)
        hora_exibicao = hora_webhook1_dt + timedelta(seconds=delay_inicial)
        print(f"  {viz}: delay={delay_inicial}s, exibição={hora_exibicao.strftime('%H:%M:%S')}")
    
    print()
    
    # Grupo 2: 853-858 (89778060037 às 19:32:14)
    print("Grupo 2: CPF 89778060037 às 19:32:14")
    hora_webhook2 = datetime.strptime("19:32:14", "%H:%M:%S").time()
    hora_webhook2_dt = datetime.combine(datetime.today(), hora_webhook2)
    
    # Último evento de cada visualização (do grupo anterior)
    ultimos_eventos = {
        "visualization1": datetime.strptime("19:32:23", "%H:%M:%S").time(),
        "visualization2": datetime.strptime("19:32:33", "%H:%M:%S").time(),
        "visualization3": datetime.strptime("19:32:43", "%H:%M:%S").time(),
        "visualization4": datetime.strptime("19:32:53", "%H:%M:%S").time(),
        "visualization5": datetime.strptime("19:33:03", "%H:%M:%S").time(),
        "visualization6": datetime.strptime("19:33:13", "%H:%M:%S").time(),
    }
    
    for i, viz in enumerate(["visualization1", "visualization2", "visualization3", "visualization4", "visualization5", "visualization6"]):
        delay_inicial = tempo_inicial + (i * incremento)
        hora_fim_ultimo = datetime.combine(hora_webhook2_dt.date(), ultimos_eventos[viz])
        
        if hora_fim_ultimo >= hora_webhook2_dt:
            # Último evento ainda está rodando
            hora_inicio = hora_fim_ultimo
            delay_calculado = (hora_inicio - hora_webhook2_dt).total_seconds()
            diff = 0  # Não há gap
        else:
            # Último evento já terminou
            diff = (hora_webhook2_dt - hora_fim_ultimo).total_seconds()
            if diff >= tempo_inicial:
                # Gap >= tempo_inicial - usar apenas tempo_inicial
                hora_inicio = hora_webhook2_dt + timedelta(seconds=tempo_inicial)
                delay_calculado = tempo_inicial
            else:
                # Gap < tempo_inicial - usar delay_inicial
                hora_inicio = hora_fim_ultimo + timedelta(seconds=delay_inicial)
                delay_calculado = (hora_inicio - hora_webhook2_dt).total_seconds()
        
        print(f"  {viz}: gap={diff:.1f}s, delay_calculado={delay_calculado:.1f}s, exibição={hora_inicio.strftime('%H:%M:%S')}")
    
    print()
    
    # Grupo 3: 859-864 (22673617876 às 19:32:35)
    print("Grupo 3: CPF 22673617876 às 19:32:35")
    hora_webhook3 = datetime.strptime("19:32:35", "%H:%M:%S").time()
    hora_webhook3_dt = datetime.combine(datetime.today(), hora_webhook3)
    
    # Último evento de cada visualização (do grupo anterior)
    ultimos_eventos2 = {
        "visualization1": datetime.strptime("19:32:33", "%H:%M:%S").time(),
        "visualization2": datetime.strptime("19:32:43", "%H:%M:%S").time(),
        "visualization3": datetime.strptime("19:32:53", "%H:%M:%S").time(),
        "visualization4": datetime.strptime("19:33:03", "%H:%M:%S").time(),
        "visualization5": datetime.strptime("19:33:13", "%H:%M:%S").time(),
        "visualization6": datetime.strptime("19:33:23", "%H:%M:%S").time(),
    }
    
    for i, viz in enumerate(["visualization1", "visualization2", "visualization3", "visualization4", "visualization5", "visualization6"]):
        delay_inicial = tempo_inicial + (i * incremento)
        hora_fim_ultimo = datetime.combine(hora_webhook3_dt.date(), ultimos_eventos2[viz])
        
        if hora_fim_ultimo >= hora_webhook3_dt:
            # Último evento ainda está rodando
            hora_inicio = hora_fim_ultimo
            delay_calculado = (hora_inicio - hora_webhook3_dt).total_seconds()
            diff = 0  # Não há gap
        else:
            # Último evento já terminou
            diff = (hora_webhook3_dt - hora_fim_ultimo).total_seconds()
            if diff >= tempo_inicial:
                # Gap >= tempo_inicial - usar apenas tempo_inicial
                hora_inicio = hora_webhook3_dt + timedelta(seconds=tempo_inicial)
                delay_calculado = tempo_inicial
            else:
                # Gap < tempo_inicial - usar delay_inicial
                hora_inicio = hora_fim_ultimo + timedelta(seconds=delay_inicial)
                delay_calculado = (hora_inicio - hora_webhook3_dt).total_seconds()
        
        print(f"  {viz}: gap={diff:.1f}s, delay_calculado={delay_calculado:.1f}s, exibição={hora_inicio.strftime('%H:%M:%S')}")

if __name__ == "__main__":
    analisar_problema_delay() 