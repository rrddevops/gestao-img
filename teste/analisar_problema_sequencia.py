#!/usr/bin/env python3
"""
Script para analisar o problema de sequência cronológica
"""

def analisar_dados_problema():
    """Analisa os dados fornecidos para identificar o problema de sequência"""
    
    # Dados fornecidos pelo usuário
    dados = [
        (1, "11111111111", "visualization1", "11:05:20", "00:00:30", "11:05:50", "11:06:00"),
        (2, "11111111111", "visualization2", "11:05:20", "00:00:40", "11:06:00", "11:06:10"),
        (3, "11111111111", "visualization3", "11:05:20", "00:00:50", "11:06:10", "11:06:20"),
        (4, "11111111111", "visualization4", "11:05:20", "00:01:00", "11:06:20", "11:06:30"),
        (5, "11111111111", "visualization5", "11:05:20", "00:01:10", "11:06:30", "11:06:40"),
        (6, "11111111111", "visualization6", "11:05:20", "00:01:20", "11:06:40", "11:06:50"),
        (7, "00000000000", "visualization1", "11:06:20", "00:00:10.102373", "11:06:30", "11:06:40"),
        (8, "00000000000", "visualization2", "11:06:20", "00:00:30.102373", "11:06:50", "11:07:00"),
        (9, "00000000000", "visualization3", "11:06:20", "00:00:50.102373", "11:07:10", "11:07:20"),
        (10, "00000000000", "visualization4", "11:06:20", "00:01:10.102373", "11:07:30", "11:07:40"),
        (11, "00000000000", "visualization5", "11:06:20", "00:01:30.102373", "11:07:50", "11:08:00"),
        (12, "00000000000", "visualization6", "11:06:20", "00:01:50.102373", "11:08:10", "11:08:20"),
        (13, "22222222222", "visualization1", "11:07:07", "00:00:02.711901", "11:07:10", "11:07:20"),
        (14, "22222222222", "visualization2", "11:07:07", "00:00:32.711901", "11:07:40", "11:07:50"),
        (15, "22222222222", "visualization3", "11:07:07", "00:01:02.711901", "11:08:10", "11:08:20"),
        (16, "22222222222", "visualization4", "11:07:07", "00:01:32.711901", "11:08:40", "11:08:50"),
        (17, "22222222222", "visualization5", "11:07:07", "00:02:02.711901", "11:09:10", "11:09:20"),
        (18, "22222222222", "visualization6", "11:07:07", "00:02:32.711901", "11:09:40", "11:09:50"),
        (19, "33333333333", "visualization1", "11:08:11", "00:00:30", "11:08:41", "11:08:51"),
        (20, "33333333333", "visualization2", "11:08:11", "00:00:18.833233", "11:08:30", "11:08:40"),
        (21, "33333333333", "visualization3", "11:08:11", "00:00:58.833233", "11:09:10", "11:09:20"),
        (22, "33333333333", "visualization4", "11:08:11", "00:01:38.833233", "11:09:50", "11:10:00"),
        (23, "33333333333", "visualization5", "11:08:11", "00:02:18.833233", "11:10:30", "11:10:40"),
        (24, "33333333333", "visualization6", "11:08:11", "00:02:58.833233", "11:11:10", "11:11:20"),
        (25, "44444444444", "visualization1", "11:08:18", "00:01:02.482463", "11:09:21", "11:09:31"),
        (26, "44444444444", "visualization2", "11:08:18", "00:01:01.315696", "11:09:20", "11:09:30"),
        (27, "44444444444", "visualization3", "11:08:18", "00:01:51.315696", "11:10:10", "11:10:20"),
        (28, "44444444444", "visualization4", "11:08:18", "00:02:41.315696", "11:11:00", "11:11:10"),
        (29, "44444444444", "visualization5", "11:08:18", "00:03:31.315696", "11:11:50", "11:12:00"),
        (30, "44444444444", "visualization6", "11:08:18", "00:04:21.315696", "11:12:40", "11:12:50"),
    ]
    
    print("🔍 ANÁLISE DO PROBLEMA DE SEQUÊNCIA CRONOLÓGICA")
    print("=" * 60)
    
    # Organizar por visualização
    visualizations = {}
    for evento in dados:
        viz = evento[2]
        if viz not in visualizations:
            visualizations[viz] = []
        visualizations[viz].append(evento)
    
    # Analisar cada visualização
    for viz in sorted(visualizations.keys()):
        print(f"\n📺 {viz.upper()}:")
        print("-" * 50)
        
        eventos = sorted(visualizations[viz], key=lambda x: x[6])  # Ordenar por hora_exibicao
        
        for i, evento in enumerate(eventos):
            id_evento, cpf, viz, hora_acesso, delay, hora_exibicao, hora_fim = evento
            
            # Verificar sobreposição com evento anterior
            if i > 0:
                evento_anterior = eventos[i-1]
                hora_fim_anterior = evento_anterior[6]
                
                if hora_exibicao < hora_fim_anterior:
                    print(f"❌ SOBREPOSIÇÃO: Evento {id_evento} ({hora_exibicao}) começa antes do fim do anterior ({hora_fim_anterior})")
                elif hora_exibicao == hora_fim_anterior:
                    print(f"⚠️  SEM GAP: Evento {id_evento} começa exatamente quando o anterior termina")
                else:
                    gap = f"Gap: {hora_exibicao} - {hora_fim_anterior}"
                    print(f"✅ OK: {gap}")
            
            print(f"  {id_evento:2d} | {cpf} | {hora_acesso} → {hora_exibicao} → {hora_fim} | Delay: {delay}")
    
    # Identificar problemas específicos
    print(f"\n🚨 PROBLEMAS IDENTIFICADOS:")
    print("=" * 40)
    
    # Problema 1: CPF 33333333333 - visualization2 aparece antes da visualization1
    print("1. CPF 33333333333 - SEQUÊNCIA INVERTIDA:")
    print("   - visualization1 (ID 19): 11:08:41 → 11:08:51")
    print("   - visualization2 (ID 20): 11:08:30 → 11:08:40  ← PROBLEMA!")
    print("   - A visualization2 deveria aparecer DEPOIS da visualization1")
    
    # Problema 2: CPF 44444444444 - visualization2 aparece antes da visualization1
    print("\n2. CPF 44444444444 - SEQUÊNCIA INVERTIDA:")
    print("   - visualization1 (ID 25): 11:09:21 → 11:09:31")
    print("   - visualization2 (ID 26): 11:09:20 → 11:09:30  ← PROBLEMA!")
    print("   - A visualization2 deveria aparecer DEPOIS da visualization1")
    
    # Problema 3: Delays inconsistentes
    print("\n3. DELAYS INCONSISTENTES:")
    print("   - CPF 22222222222: visualization1 tem delay de apenas 2.7s (deveria ser 30s)")
    print("   - CPF 33333333333: visualization2 tem delay de apenas 18.8s (deveria ser 40s)")
    print("   - CPF 44444444444: visualization2 tem delay de apenas 61.3s (deveria ser 40s)")
    
    # Análise da causa raiz
    print(f"\n🔧 ANÁLISE DA CAUSA RAIZ:")
    print("=" * 30)
    print("O problema está na lógica do webhook que calcula os horários:")
    print("1. Quando há eventos simultâneos, a lógica de 'último evento' pode estar")
    print("   considerando eventos de outras visualizações")
    print("2. O cálculo de delay não está considerando corretamente a sequência")
    print("3. A lógica de 'gap' pode estar causando inversões na ordem")
    
    print(f"\n💡 SOLUÇÃO RECOMENDADA:")
    print("=" * 30)
    print("1. Garantir que cada visualização tenha sua própria sequência independente")
    print("2. Simplificar a lógica de cálculo de horários")
    print("3. Sempre usar o último evento da visualização específica")
    print("4. Aplicar delays consistentes baseados nos parâmetros da tabela")

if __name__ == "__main__":
    analisar_dados_problema() 