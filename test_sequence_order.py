#!/usr/bin/env python3
"""
Script para testar se a sequência no banco está correta (1, 2, 3, 4, 5, 6)
"""

import requests
import json
from datetime import datetime
import time

def test_sequence_order():
    """Testa se a sequência no banco está correta"""
    
    # Configuração
    webhook_url = "http://localhost:5002/schedule"
    schedule_details_url = "http://localhost:8083/schedule-details"
    
    print("🧪 Testando sequência correta no banco de dados...")
    print("=" * 60)
    
    # Teste 1: Agendar uma imagem
    test_cpf = "99999999999"
    print(f"📅 Agendando CPF: {test_cpf}")
    
    try:
        response = requests.post(webhook_url, json={'cpf': test_cpf}, timeout=10)
        if response.status_code == 200:
            print(f"✅ Agendamento realizado com sucesso")
            result = response.json()
            print(f"   Resposta: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Erro no agendamento: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erro ao fazer agendamento: {e}")
        return False
    
    # Aguarda um pouco para garantir que os registros foram criados
    print("⏳ Aguardando criação dos registros...")
    time.sleep(2)
    
    # Teste 2: Verificar detalhes dos agendamentos
    print(f"\n📋 Verificando sequência dos agendamentos...")
    
    try:
        response = requests.get(schedule_details_url, timeout=10)
        if response.status_code == 200:
            details = response.json()
            entries = details.get('schedule_entries', [])
            
            # Filtra apenas os registros do CPF de teste
            test_entries = [entry for entry in entries if entry['cpf'] == test_cpf]
            
            print(f"✅ Encontrados {len(test_entries)} agendamentos para CPF {test_cpf}")
            
            if len(test_entries) == 0:
                print("❌ Nenhum agendamento encontrado para o CPF de teste")
                return False
            
            # Verifica se há exatamente 6 visualizações
            if len(test_entries) != 6:
                print(f"❌ Esperado 6 visualizações, encontrado {len(test_entries)}")
                return False
            
            # Ordena por sequence_id para verificar a sequência
            test_entries.sort(key=lambda x: x['sequence_id'])
            
            print("\n📊 Sequência encontrada:")
            print("sequence_id | ID | visualization_name")
            print("-" * 50)
            
            expected_sequence = []
            for i, entry in enumerate(test_entries):
                sequence_id = entry['sequence_id']
                entry_id = entry['id']
                viz_name = entry['visualization_name']
                viz_number = viz_name.replace('visualization', '')
                
                print(f"{sequence_id:11} | {entry_id} | {viz_name}")
                expected_sequence.append(int(viz_number))
            
            # Verifica se a sequência está correta (1, 2, 3, 4, 5, 6)
            correct_sequence = [1, 2, 3, 4, 5, 6]
            
            print(f"\n🔍 Sequência esperada: {correct_sequence}")
            print(f"🔍 Sequência encontrada: {expected_sequence}")
            
            if expected_sequence == correct_sequence:
                print("✅ SEQUÊNCIA CORRETA! Os registros estão na ordem 1, 2, 3, 4, 5, 6")
                return True
            else:
                print("❌ SEQUÊNCIA INCORRETA! Os registros não estão na ordem esperada")
                return False
                
        else:
            print(f"❌ Erro ao buscar detalhes: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao buscar detalhes: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando testes de sequência...")
    print()
    
    # Teste de sequência
    success = test_sequence_order()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Teste de sequência passou!")
        print("✅ A sequência no banco está correta (1, 2, 3, 4, 5, 6)")
    else:
        print("❌ Teste falhou")
        print("🔧 Verifique os logs e tente novamente")
    
    print("\n📋 Resumo das mudanças implementadas:")
    print("   1. Agendamento centralizado na visualization1")
    print("   2. Criação de todos os registros em sequência")
    print("   3. Ordenação por número da visualização")
    print("   4. Commit único para garantir consistência") 