#!/usr/bin/env python3
"""
Script simples para testar a correção da sequência cronológica
"""

import requests
import time
import json

def testar_webhook_simples():
    """Testa o webhook com dados simples"""
    print("🧪 TESTE SIMPLES DA CORREÇÃO")
    print("=" * 40)
    
    # Primeiro, verificar se há CPFs cadastrados
    try:
        response = requests.get("http://localhost:8000/cadastro/")
        if response.status_code == 200:
            cadastros = response.json()
            print(f"📋 CPFs cadastrados: {len(cadastros)}")
            
            if cadastros:
                # Usar o primeiro CPF disponível
                cpf_teste = cadastros[0]['cpf']
                print(f"🎯 Usando CPF: {cpf_teste}")
                
                # Limpar eventos existentes
                print("\n1. Limpando eventos...")
                requests.delete("http://localhost:8000/webhook/eventos")
                
                # Enviar webhook
                print("2. Enviando webhook...")
                data = {"cpf": cpf_teste}
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
                            
                            # Agrupar por visualização
                            visualizations = {}
                            for evento in eventos:
                                viz = evento['visualization']
                                if viz not in visualizations:
                                    visualizations[viz] = []
                                visualizations[viz].append(evento)
                            
                            # Mostrar sequência por visualização
                            for viz in sorted(visualizations.keys()):
                                print(f"\n📺 {viz}:")
                                eventos_viz = sorted(visualizations[viz], key=lambda x: x['hora_exibicao'])
                                
                                for evento in eventos_viz:
                                    print(f"  {evento['hora_exibicao']} → {evento['hora_fim']} | Delay: {evento['delay']}")
                            
                            # Verificar se há inversões
                            print(f"\n🔍 VERIFICANDO ORDEM:")
                            eventos_ordenados = sorted(eventos, key=lambda x: x['hora_exibicao'])
                            
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
                            else:
                                print(f"\n❌ {len(problemas)} PROBLEMAS ENCONTRADOS!")
                        else:
                            print("❌ Nenhum evento foi criado!")
                    else:
                        print(f"❌ Erro ao listar eventos: {response.status_code}")
                else:
                    print(f"❌ Erro ao enviar webhook: {response.status_code}")
                    print(f"   Resposta: {response.text}")
            else:
                print("❌ Nenhum CPF cadastrado. Cadastre um CPF primeiro.")
        else:
            print(f"❌ Erro ao listar cadastros: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    testar_webhook_simples() 