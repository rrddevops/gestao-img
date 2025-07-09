#!/usr/bin/env python3
"""
Script para cadastrar CPF de teste e testar a correção da sequência cronológica
"""

import requests
import time
import json

def cadastrar_cpf_teste():
    """Cadastra um CPF de teste"""
    print("📝 CADASTRANDO CPF DE TESTE")
    print("=" * 40)
    
    # Imagem de teste (1x1 pixel transparente em base64)
    imagem_teste = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    
    data = {
        "cpf": "12345678901",
        "imagem_base64": imagem_teste
    }
    
    try:
        response = requests.post("http://localhost:8000/cadastro/", json=data)
        if response.status_code == 200:
            print("✅ CPF 12345678901 cadastrado com sucesso")
            return True
        else:
            print(f"❌ Erro ao cadastrar CPF: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erro ao cadastrar CPF: {e}")
        return False

def testar_sequencia():
    """Testa a sequência cronológica"""
    print("\n🧪 TESTANDO SEQUÊNCIA CRONOLÓGICA")
    print("=" * 40)
    
    # Limpar eventos existentes
    print("1. Limpando eventos...")
    try:
        requests.delete("http://localhost:8000/webhook/eventos")
        print("✅ Eventos limpos")
    except Exception as e:
        print(f"❌ Erro ao limpar eventos: {e}")
    
    # Enviar webhook
    print("2. Enviando webhook...")
    data = {"cpf": "12345678901"}
    
    try:
        response = requests.post("http://localhost:8000/webhook/", json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Webhook enviado: {result['eventos_criados']} eventos criados")
            
            # Aguardar processamento
            time.sleep(2)
            
            # Listar eventos
            print("3. Listando eventos...")
            response = requests.get("http://localhost:8000/webhook/eventos")
            if response.status_code == 200:
                eventos = response.json()
                print(f"📊 Total de eventos: {len(eventos)}")
                
                if eventos:
                    # Analisar sequência
                    print("\n🔍 ANÁLISE DA SEQUÊNCIA:")
                    print("-" * 30)
                    
                    # Ordenar por hora de exibição
                    eventos_ordenados = sorted(eventos, key=lambda x: x['hora_exibicao'])
                    
                    # Mostrar sequência
                    for i, evento in enumerate(eventos_ordenados):
                        print(f"{i+1:2d}. {evento['visualization']}: {evento['hora_exibicao']} → {evento['hora_fim']} | Delay: {evento['delay']}")
                    
                    # Verificar se há inversões
                    print(f"\n🔍 VERIFICANDO ORDEM:")
                    problemas = []
                    
                    for i in range(len(eventos_ordenados) - 1):
                        atual = eventos_ordenados[i]
                        proximo = eventos_ordenados[i + 1]
                        
                        num_atual = int(atual['visualization'].replace('visualization', ''))
                        num_proximo = int(proximo['visualization'].replace('visualization', ''))
                        
                        if num_atual > num_proximo:
                            problema = f"❌ ORDEM INVERTIDA: {atual['visualization']} ({atual['hora_exibicao']}) vem antes de {proximo['visualization']} ({proximo['hora_exibicao']})"
                            print(problema)
                            problemas.append(problema)
                    
                    if not problemas:
                        print("✅ NENHUM PROBLEMA ENCONTRADO!")
                        print("   A sequência cronológica está correta.")
                        return True
                    else:
                        print(f"\n❌ {len(problemas)} PROBLEMAS ENCONTRADOS!")
                        return False
                else:
                    print("❌ Nenhum evento foi criado!")
                    return False
            else:
                print(f"❌ Erro ao listar eventos: {response.status_code}")
                return False
        else:
            print(f"❌ Erro ao enviar webhook: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 TESTE DA CORREÇÃO DA SEQUÊNCIA CRONOLÓGICA")
    print("=" * 60)
    
    # Cadastrar CPF de teste
    if cadastrar_cpf_teste():
        # Testar sequência
        if testar_sequencia():
            print("\n🎉 TESTE CONCLUÍDO COM SUCESSO!")
            print("   A correção da sequência cronológica está funcionando.")
        else:
            print("\n❌ TESTE FALHOU!")
            print("   Ainda há problemas na sequência cronológica.")
    else:
        print("\n❌ Não foi possível cadastrar CPF de teste.")

if __name__ == "__main__":
    main() 