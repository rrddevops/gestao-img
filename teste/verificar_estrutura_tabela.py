#!/usr/bin/env python3
"""
Script para verificar e sugerir melhorias na estrutura da tabela de eventos
"""

import requests
import json
from datetime import datetime
import pytz

# Configurações
EVENTOS_URL = "http://localhost:8000/webhook/eventos"
TIMEZONE_BRASILIA = pytz.timezone('America/Sao_Paulo')

def obter_hora_brasilia():
    """Obtém a hora atual em Brasília"""
    return datetime.now(TIMEZONE_BRASILIA)

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

def analisar_estrutura_eventos(eventos):
    """Analisa a estrutura dos eventos e sugere melhorias"""
    print("\n" + "="*80)
    print("ANÁLISE DA ESTRUTURA DOS EVENTOS")
    print("="*80)
    
    if not eventos:
        print("❌ Nenhum evento encontrado para análise")
        return
    
    print(f"📊 Total de eventos: {len(eventos)}")
    
    # Agrupar por visualização
    eventos_por_viz = {}
    for evento in eventos:
        viz = evento['visualization']
        if viz not in eventos_por_viz:
            eventos_por_viz[viz] = []
        eventos_por_viz[viz].append(evento)
    
    print(f"\n📺 Distribuição por visualização:")
    for viz in sorted(eventos_por_viz.keys()):
        count = len(eventos_por_viz[viz])
        print(f"   {viz}: {count} eventos")
    
    # Verificar se há eventos duplicados ou conflitantes
    print(f"\n🔍 Verificando conflitos de horário:")
    conflitos_encontrados = 0
    
    for viz, eventos_viz in eventos_por_viz.items():
        # Ordenar por hora de exibição
        eventos_viz.sort(key=lambda x: x['hora_exibicao'])
        
        for i in range(len(eventos_viz) - 1):
            evento_atual = eventos_viz[i]
            proximo_evento = eventos_viz[i + 1]
            
            # Verificar sobreposição
            fim_atual = evento_atual['hora_fim']
            inicio_proximo = proximo_evento['hora_exibicao']
            
            if fim_atual > inicio_proximo:
                print(f"   ⚠️  {viz}: Sobreposição detectada!")
                print(f"      Evento {i+1} termina em {fim_atual}")
                print(f"      Evento {i+2} começa em {inicio_proximo}")
                conflitos_encontrados += 1
    
    if conflitos_encontrados == 0:
        print("   ✅ Nenhum conflito de horário encontrado")
    
    # Sugerir melhorias na estrutura
    print(f"\n💡 SUGESTÕES DE MELHORIA NA ESTRUTURA:")
    print("-" * 50)
    
    print("1. ÍNDICES RECOMENDADOS:")
    print("   - Índice composto em (visualization, hora_exibicao)")
    print("   - Índice em hora_fim para consultas de eventos ativos")
    print("   - Índice em cpf para consultas por CPF")
    
    print("\n2. ESTRUTURA DE TABELA OTIMIZADA:")
    print("   CREATE INDEX idx_eventos_viz_hora ON eventos (visualization, hora_exibicao);")
    print("   CREATE INDEX idx_eventos_fim ON eventos (hora_fim);")
    print("   CREATE INDEX idx_eventos_cpf ON eventos (cpf);")
    
    print("\n3. CONSULTAS OTIMIZADAS:")
    print("   - Para buscar próximo evento de uma visualização:")
    print("     SELECT * FROM eventos WHERE visualization = ? AND hora_exibicao > ? ORDER BY hora_exibicao LIMIT 1")
    print("   - Para buscar último evento de uma visualização:")
    print("     SELECT * FROM eventos WHERE visualization = ? ORDER BY hora_fim DESC LIMIT 1")
    
    print("\n4. VANTAGENS DA ESTRUTURA ATUAL:")
    print("   ✅ Cada visualização tem sua própria sequência")
    print("   ✅ Fácil consulta por visualização")
    print("   ✅ Controle independente de timing")
    
    print("\n5. POSSÍVEIS MELHORIAS:")
    print("   🔄 Adicionar campo 'status' (ativo, concluído, cancelado)")
    print("   🔄 Adicionar campo 'prioridade' para eventos especiais")
    print("   🔄 Adicionar campo 'created_at' para auditoria")

def verificar_performance_consultas(eventos):
    """Simula consultas para verificar performance"""
    print(f"\n⚡ SIMULAÇÃO DE CONSULTAS:")
    print("-" * 40)
    
    if not eventos:
        return
    
    # Simular consulta por visualização
    viz_teste = "visualization1"
    eventos_viz = [e for e in eventos if e['visualization'] == viz_teste]
    
    print(f"📊 Consulta por visualização '{viz_teste}':")
    print(f"   Eventos encontrados: {len(eventos_viz)}")
    
    if eventos_viz:
        # Ordenar por hora de exibição
        eventos_viz.sort(key=lambda x: x['hora_exibicao'])
        
        print(f"   Primeiro evento: {eventos_viz[0]['hora_exibicao']}")
        print(f"   Último evento: {eventos_viz[-1]['hora_fim']}")
        
        # Simular busca de próximo evento
        hora_atual = obter_hora_brasilia().time()
        proximos_eventos = [e for e in eventos_viz if e['hora_exibicao'] > str(hora_atual)]
        
        if proximos_eventos:
            proximos_eventos.sort(key=lambda x: x['hora_exibicao'])
            print(f"   Próximo evento: {proximos_eventos[0]['hora_exibicao']} (CPF: {proximos_eventos[0]['cpf']})")
        else:
            print(f"   Nenhum evento futuro encontrado")

def main():
    """Função principal"""
    print("🔍 VERIFICAÇÃO DA ESTRUTURA DA TABELA DE EVENTOS")
    print("="*60)
    print(f"⏰ Hora atual (Brasília): {obter_hora_brasilia().strftime('%H:%M:%S')}")
    
    # Listar eventos
    print(f"\n📊 Obtendo eventos do sistema...")
    eventos = listar_eventos()
    
    if eventos:
        print(f"✅ {len(eventos)} eventos encontrados")
        analisar_estrutura_eventos(eventos)
        verificar_performance_consultas(eventos)
    else:
        print("❌ Nenhum evento encontrado")
        print("💡 Execute primeiro o teste de sequência individual para gerar eventos")
    
    print(f"\n🏁 Verificação concluída!")

if __name__ == "__main__":
    main() 