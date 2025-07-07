#!/usr/bin/env python3
"""
Script para analisar a sequência cronológica dos eventos
"""

def analisar_sequencia():
    """
    Analisa a sequência cronológica dos eventos fornecidos
    """
    print("🔍 ANÁLISE DA SEQUÊNCIA CRONOLÓGICA")
    print("=" * 60)
    
    # Dados fornecidos pelo usuário
    dados = [
        (811, "12345678901", "visualization1", "19:19:53", "00:00:06.285177", "19:19:59", "19:20:09"),
        (812, "12345678901", "visualization2", "19:19:53", "00:00:16.285177", "19:20:09", "19:20:19"),
        (813, "12345678901", "visualization3", "19:19:53", "00:00:26.285177", "19:20:19", "19:20:29"),
        (814, "12345678901", "visualization4", "19:19:53", "00:00:36.285177", "19:20:29", "19:20:39"),
        (815, "12345678901", "visualization5", "19:19:53", "00:00:46.285177", "19:20:39", "19:20:49"),
        (816, "12345678901", "visualization6", "19:19:53", "00:00:56.285177", "19:20:49", "19:20:59"),
        (817, "89778060037", "visualization1", "19:20:24", "00:00:15.615123", "19:20:39", "19:20:49"),
        (818, "89778060037", "visualization2", "19:20:24", "00:00:35.615123", "19:20:59", "19:21:09"),
        (819, "89778060037", "visualization3", "19:20:24", "00:00:05.615123", "19:20:29", "19:20:39"),
        (820, "89778060037", "visualization4", "19:20:24", "00:00:15.615123", "19:20:39", "19:20:49"),
        (821, "89778060037", "visualization5", "19:20:24", "00:00:25.615123", "19:20:49", "19:20:59"),
        (822, "89778060037", "visualization6", "19:20:24", "00:00:35.615123", "19:20:59", "19:21:09"),
            (805, "11111111111", "visualization1", "19:19:19", "00:00:30", "19:19:49", "19:19:59"),
    (806, "11111111111", "visualization2", "19:19:19", "00:00:40", "19:19:59", "19:20:09"),
    (807, "11111111111", "visualization3", "19:19:19", "00:00:50", "19:20:09", "19:20:19"),
    (808, "11111111111", "visualization4", "19:19:19", "00:01:00", "19:20:19", "19:20:29"),
    (809, "11111111111", "visualization5", "19:19:19", "00:01:10", "19:20:29", "19:20:39"),
    (810, "11111111111", "visualization6", "19:19:19", "00:01:20", "19:20:39", "19:20:49"),
    ]
    
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
        print("-" * 40)
        
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
            
            print(f"  {id_evento:3d} | {cpf} | {hora_acesso} → {hora_exibicao} → {hora_fim} | Delay: {delay}")
    
    # Analisar problemas específicos
    print(f"\n🔍 PROBLEMAS IDENTIFICADOS:")
    print("=" * 40)
    
    # Problema 1: Evento 819 (visualization3) tem delay muito baixo
    print("1. Evento 819 (visualization3) tem delay de apenas 5.6s, mas deveria ser 26.6s")
    print("   - CPF 89778060037 enviado às 19:20:24")
    print("   - Deveria começar às 19:20:50 (19:20:24 + 26.6s)")
    print("   - Mas está começando às 19:20:29")
    
    # Problema 2: Sobreposição na visualization3
    print("\n2. Sobreposição na visualization3:")
    print("   - Evento 813 (12345678901): 19:20:19 → 19:20:29")
    print("   - Evento 819 (89778060037): 19:20:29 → 19:20:39")
    print("   - Evento 807 (11111111111): 19:20:09 → 19:20:19")
    print("   - Ordem cronológica correta deveria ser: 807 → 813 → 819")
    
    # Problema 3: Inconsistência nos delays
    print("\n3. Inconsistência nos delays para CPF 89778060037:")
    print("   - visualization1: 15.6s (correto)")
    print("   - visualization2: 35.6s (correto)")
    print("   - visualization3: 5.6s (ERRADO - deveria ser 25.6s)")
    print("   - visualization4: 15.6s (correto)")
    print("   - visualization5: 25.6s (correto)")
    print("   - visualization6: 35.6s (correto)")

if __name__ == "__main__":
    analisar_sequencia() 