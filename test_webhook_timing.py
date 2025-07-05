#!/usr/bin/env python3
"""
Script para testar o webhook respeitando os tempos de exibição configurados.
Este script agenda a exibição de imagens já cadastradas no sistema com intervalos apropriados.
"""

import requests
import time
import sys
from datetime import datetime, timedelta

# Lista de CPFs do banco (já cadastrados)
CPFS_DO_BANCO = [
    "88888888888",
    "77777777777", 
    "66666666666",
    "55555555555",
    "44444444444",
    "33333333333",
    "22222222227",
    "22222222226",
    "22222222225",
    "22222222224",
    "22222222223",
    "22222222222",
    "22222222221",
    "11111111119",
    "11111111118",
    "11111111117",
    "11111111116",
    "11111111115",
    "11111111114",
    "11111111113",
    "11111111112",
    "11111111111",
    "99999999999",
    "00000000000"
]

# Configuração do webhook
WEBHOOK_URL = "http://localhost:5002/webhook"

# Configuração dos tempos (baseado no visualization_config.json)
DISPLAY_SECONDS = 10  # Tempo que cada imagem fica visível
DELAY_BETWEEN_CPFS = DISPLAY_SECONDS + 5  # 5 segundos de margem entre CPFs

def agendar_cpf(cpf):
    """Agenda a exibição de um CPF via webhook"""
    try:
        data = {'cpf': cpf}
        response = requests.post(WEBHOOK_URL, json=data, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ CPF {cpf} agendado com sucesso")
            return True
        else:
            print(f"❌ Erro ao agendar CPF {cpf}: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"⏰ Timeout ao agendar CPF {cpf}")
        return False
    except requests.exceptions.ConnectionError:
        print(f"🔌 Erro de conexão ao agendar CPF {cpf}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado ao agendar CPF {cpf}: {str(e)}")
        return False

def testar_webhook_com_timing():
    """Testa o webhook respeitando os tempos de exibição"""
    print("🚀 TESTE DO WEBHOOK - COM TIMING CORRETO")
    print("=" * 60)
    print(f"📋 Total de CPFs: {len(CPFS_DO_BANCO)}")
    print(f"⏱️  Tempo de exibição por imagem: {DISPLAY_SECONDS}s")
    print(f"⏱️  Delay entre CPFs: {DELAY_BETWEEN_CPFS}s")
    print(f"⏱️  Tempo total estimado: {len(CPFS_DO_BANCO) * DELAY_BETWEEN_CPFS / 60:.1f} minutos")
    print("=" * 60)
    
    sucessos = 0
    erros = 0
    start_time = datetime.now()
    
    for i, cpf in enumerate(CPFS_DO_BANCO, 1):
        print(f"\n[{i}/{len(CPFS_DO_BANCO)}] Agendando CPF: {cpf}")
        print(f"⏰ Horário atual: {datetime.now().strftime('%H:%M:%S')}")
        
        if agendar_cpf(cpf):
            sucessos += 1
        else:
            erros += 1
        
        # Delay entre agendamentos (exceto no último)
        if i < len(CPFS_DO_BANCO):
            print(f"⏳ Aguardando {DELAY_BETWEEN_CPFS}s até próximo CPF...")
            time.sleep(DELAY_BETWEEN_CPFS)
    
    end_time = datetime.now()
    duration = end_time - start_time
    
    # Resumo final
    print("\n" + "=" * 60)
    print("📊 RESUMO DO TESTE")
    print("=" * 60)
    print(f"📋 Total de CPFs processados: {len(CPFS_DO_BANCO)}")
    print(f"✅ Agendamentos com sucesso: {sucessos}")
    print(f"❌ Erros: {erros}")
    print(f"⏱️  Tempo total: {duration}")
    print("=" * 60)
    
    if sucessos > 0:
        print("🎉 Teste concluído!")
        print("📺 As imagens estão sendo exibidas nas telas de visualização")
        print("🔗 Acesse: http://localhost:8083, 8084, 8085, etc.")
        print("\n📋 SEQUÊNCIA DE EXIBIÇÃO:")
        print("• visualization1: aparece primeiro (delay 30s)")
        print("• visualization2: aparece 10s depois (delay 40s)")
        print("• visualization3: aparece 20s depois (delay 50s)")
        print("• visualization4: aparece 30s depois (delay 60s)")
        print("• visualization5: aparece 40s depois (delay 70s)")
        print("• visualization6: aparece 50s depois (delay 80s)")
    else:
        print("😞 Nenhum agendamento foi realizado com sucesso")

def testar_webhook_rapido():
    """Testa o webhook com todos os CPFs rapidamente (para comparação)"""
    print("⚡ TESTE DO WEBHOOK - AGENDAMENTO RÁPIDO")
    print("=" * 60)
    print(f"📋 Total de CPFs: {len(CPFS_DO_BANCO)}")
    print("⚡ Sem delay entre agendamentos")
    print("=" * 60)
    
    sucessos = 0
    erros = 0
    
    for i, cpf in enumerate(CPFS_DO_BANCO, 1):
        print(f"[{i}/{len(CPFS_DO_BANCO)}] Agendando CPF: {cpf}")
        
        if agendar_cpf(cpf):
            sucessos += 1
        else:
            erros += 1
    
    # Resumo final
    print("\n" + "=" * 60)
    print("📊 RESUMO DO TESTE RÁPIDO")
    print("=" * 60)
    print(f"📋 Total de CPFs processados: {len(CPFS_DO_BANCO)}")
    print(f"✅ Agendamentos com sucesso: {sucessos}")
    print(f"❌ Erros: {erros}")
    print("=" * 60)

def testar_cpf_especifico(cpf):
    """Testa o webhook com um CPF específico"""
    print(f"🎯 TESTE DO WEBHOOK - CPF ESPECÍFICO: {cpf}")
    print("=" * 60)
    
    if agendar_cpf(cpf):
        print("✅ Teste concluído com sucesso!")
    else:
        print("❌ Teste falhou!")

def main():
    print("🔧 TESTE DO WEBHOOK - SISTEMA DE GESTÃO DE IMAGENS")
    print("=" * 60)
    print("Escolha uma opção:")
    print("1. Teste com timing correto (recomendado)")
    print("2. Teste rápido (sem delay)")
    print("3. Teste CPF específico")
    print("4. Sair")
    print("=" * 60)
    
    while True:
        try:
            opcao = input("\nDigite sua opção (1-4): ").strip()
            
            if opcao == "1":
                testar_webhook_com_timing()
                break
                
            elif opcao == "2":
                testar_webhook_rapido()
                break
                
            elif opcao == "3":
                cpf = input("Digite o CPF para testar: ").strip()
                if len(cpf) == 11 and cpf.isdigit():
                    testar_cpf_especifico(cpf)
                else:
                    print("❌ CPF inválido! Deve ter 11 dígitos.")
                break
                
            elif opcao == "4":
                print("👋 Saindo...")
                break
                
            else:
                print("❌ Opção inválida! Digite 1, 2, 3 ou 4.")
                
        except KeyboardInterrupt:
            print("\n\n❌ Operação cancelada pelo usuário")
            break
        except Exception as e:
            print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main() 