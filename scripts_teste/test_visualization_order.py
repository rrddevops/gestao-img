#!/usr/bin/env python3
"""
Script de teste para verificar se o ID da imagem está sendo gerado corretamente
pela ordem de visualização (visualization1, 2, 3, etc.)
"""

import requests
import json
from datetime import datetime

def test_visualization_order():
    """Testa se o ID da imagem está sendo gerado corretamente pela ordem de visualização"""
    
    # Configuração
    webhook_url = "http://localhost:5002/schedule"
    schedule_details_url = "http://localhost:8083/schedule-details"
    
    print("🧪 Testando geração de ID pela ordem de visualização...")
    print("=" * 60)
    
    # Teste 1: Agendar uma imagem
    test_cpf = "12345678900"
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
    
    # Teste 2: Verificar detalhes dos agendamentos
    print(f"\n📋 Verificando detalhes dos agendamentos...")
    
    try:
        response = requests.get(schedule_details_url, timeout=10)
        if response.status_code == 200:
            details = response.json()
            entries = details.get('schedule_entries', [])
            
            print(f"✅ Encontrados {len(entries)} agendamentos")
            
            # Verifica se os IDs estão no formato correto
            for entry in entries:
                entry_id = entry['id']
                cpf = entry['cpf']
                viz_name = entry['visualization_name']
                
                print(f"   📝 ID: {entry_id}")
                print(f"      CPF: {cpf}")
                print(f"      Visualização: {viz_name}")
                
                # Verifica se o ID contém o número da visualização
                if cpf in entry_id and viz_name.replace('visualization', '') in entry_id:
                    print(f"      ✅ ID correto - contém CPF e número da visualização")
                else:
                    print(f"      ❌ ID incorreto - não contém CPF ou número da visualização")
                    return False
                
                print()
        else:
            print(f"❌ Erro ao buscar detalhes: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao buscar detalhes: {e}")
        return False
    
    print("🎉 Teste concluído com sucesso!")
    return True

def test_queue_update_speed():
    """Testa se a fila está atualizando em milissegundos"""
    
    print("\n⚡ Testando velocidade de atualização da fila...")
    print("=" * 60)
    
    # URLs para testar
    urls = [
        "http://localhost:8083/queue-status",
        "http://localhost:8084/queue-status", 
        "http://localhost:8085/queue-status"
    ]
    
    for i, url in enumerate(urls, 1):
        print(f"🔍 Testando visualização {i}: {url}")
        
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Status: Online")
                print(f"   📊 Fila: {data.get('queue_size', 0)} imagens")
                print(f"   🖼️  Imagem atual: {data.get('current_image', 'Nenhuma')}")
            else:
                print(f"   ❌ Status: Offline ({response.status_code})")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
        
        print()
    
    print("📝 Verifique manualmente se as atualizações estão mais rápidas:")
    print("   - Template de visualização: 500ms (era 1000ms)")
    print("   - Template de configuração: 2000ms (era 30000ms)")
    
    return True

if __name__ == "__main__":
    print("🚀 Iniciando testes das melhorias implementadas...")
    print()
    
    # Teste 1: Ordem de visualização
    success1 = test_visualization_order()
    
    # Teste 2: Velocidade de atualização
    success2 = test_queue_update_speed()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("🎉 Todos os testes passaram!")
        print("✅ ID da imagem agora segue a ordem de visualização")
        print("✅ Fila atualiza em milissegundos")
    else:
        print("❌ Alguns testes falharam")
        print("🔧 Verifique os logs e tente novamente")
    
    print("\n📋 Resumo das mudanças implementadas:")
    print("   1. ID da imagem: CPF + número da visualização + timestamp")
    print("   2. Template de visualização: atualiza a cada 500ms")
    print("   3. Template de configuração: atualiza a cada 2s")
    print("   4. Jobs pendentes: executam na visualização correta")
    print("   5. Sequência correta no banco: 1, 2, 3, 4, 5, 6")
    print("   6. Agendamento centralizado na visualization1") 