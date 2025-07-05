#!/usr/bin/env python3
"""
Script para testar o webhook com CPFs específicos do banco de dados.
Este script agenda a exibição de imagens já cadastradas no sistema.
"""

import requests
import time
import sys

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

def testar_webhook_sequencial(delay_segundos=2):
    """Testa o webhook com todos os CPFs em sequência"""
    print("🚀 TESTE DO WEBHOOK - AGENDAMENTO SEQUENCIAL")
    print("=" * 60)
    print(f"📋 Total de CPFs: {len(CPFS_DO_BANCO)}")
    print(f"⏱️  Delay entre agendamentos: {delay_segundos}s")
    print("=" * 60)
    
    sucessos = 0
    erros = 0
    
    for i, cpf in enumerate(CPFS_DO_BANCO, 1):
        print(f"\n[{i}/{len(CPFS_DO_BANCO)}] Agendando CPF: {cpf}")
        
        if agendar_cpf(cpf):
            sucessos += 1
        else:
            erros += 1
        
        # Delay entre agendamentos (exceto no último)
        if i < len(CPFS_DO_BANCO):
            print(f"⏳ Aguardando {delay_segundos}s...")
            time.sleep(delay_segundos)
    
    # Resumo final
    print("\n" + "=" * 60)
    print("📊 RESUMO DO TESTE")
    print("=" * 60)
    print(f"📋 Total de CPFs processados: {len(CPFS_DO_BANCO)}")
    print(f"✅ Agendamentos com sucesso: {sucessos}")
    print(f"❌ Erros: {erros}")
    print("=" * 60)
    
    if sucessos > 0:
        print("🎉 Teste concluído!")
        print("📺 As imagens estão sendo exibidas nas telas de visualização")
        print("🔗 Acesse: http://localhost:8083, 8084, 8085, etc.")
    else:
        print("😞 Nenhum agendamento foi realizado com sucesso")

def testar_webhook_rapido():
    """Testa o webhook com todos os CPFs rapidamente (sem delay)"""
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
    print("1. Teste sequencial (com delay)")
    print("2. Teste rápido (sem delay)")
    print("3. Teste CPF específico")
    print("4. Sair")
    print("=" * 60)
    
    while True:
        try:
            opcao = input("\nDigite sua opção (1-4): ").strip()
            
            if opcao == "1":
                delay = input("Delay entre agendamentos (segundos) [2]: ").strip()
                delay = int(delay) if delay.isdigit() else 2
                testar_webhook_sequencial(delay)
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