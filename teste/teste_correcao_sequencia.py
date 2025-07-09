#!/usr/bin/env python3
"""
Script para testar a correção da sequência cronológica
"""

import requests
import time
import json
from datetime import datetime

def limpar_eventos():
    """Limpa todos os eventos existentes"""
    try:
        response = requests.delete("http://localhost:8000/webhook/eventos")
        if response.status_code == 200:
            print("✅ Eventos limpos com sucesso")
        else:
            print(f"❌ Erro ao limpar eventos: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao limpar eventos: {e}")

def cadastrar_cpf(cpf, imagem_base64):
    """Cadastra um CPF com imagem"""
    try:
        data = {
            "cpf": cpf,
            "caminho_imagem": imagem_base64
        }
        response = requests.post("http://localhost:8000/cadastro/", json=data)
        if response.status_code == 200:
            print(f"✅ CPF {cpf} cadastrado com sucesso")
            return True
        else:
            print(f"❌ Erro ao cadastrar CPF {cpf}: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao cadastrar CPF {cpf}: {e}")
        return False

def enviar_webhook(cpf):
    """Envia webhook para um CPF"""
    try:
        data = {"cpf": cpf}
        response = requests.post("http://localhost:8000/webhook/", json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Webhook enviado para CPF {cpf}: {result['eventos_criados']} eventos criados")
            return True
        else:
            print(f"❌ Erro ao enviar webhook para CPF {cpf}: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao enviar webhook para CPF {cpf}: {e}")
        return False

def listar_eventos():
    """Lista todos os eventos"""
    try:
        response = requests.get("http://localhost:8000/webhook/eventos")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Erro ao listar eventos: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Erro ao listar eventos: {e}")
        return []

def analisar_sequencia(eventos):
    """Analisa a sequência cronológica dos eventos"""
    print("\n🔍 ANÁLISE DA SEQUÊNCIA CRONOLÓGICA")
    print("=" * 50)
    
    # Organizar por visualização
    visualizations = {}
    for evento in eventos:
        viz = evento['visualization']
        if viz not in visualizations:
            visualizations[viz] = []
        visualizations[viz].append(evento)
    
    # Analisar cada visualização
    problemas_encontrados = []
    
    for viz in sorted(visualizations.keys()):
        print(f"\n📺 {viz}:")
        print("-" * 30)
        
        eventos_viz = sorted(visualizations[viz], key=lambda x: x['hora_exibicao'])
        
        for i, evento in enumerate(eventos_viz):
            print(f"  {evento['id']:2d} | {evento['cpf']} | {evento['hora_exibicao']} → {evento['hora_fim']} | Delay: {evento['delay']}")
            
            # Verificar sobreposição com evento anterior
            if i > 0:
                evento_anterior = eventos_viz[i-1]
                if evento['hora_exibicao'] < evento_anterior['hora_fim']:
                    problema = f"❌ SOBREPOSIÇÃO em {viz}: Evento {evento['id']} ({evento['hora_exibicao']}) começa antes do fim do anterior ({evento_anterior['hora_fim']})"
                    print(problema)
                    problemas_encontrados.append(problema)
    
    # Verificar se há inversões na ordem das visualizações
    print(f"\n🔍 VERIFICANDO ORDEM DAS VISUALIZAÇÕES:")
    print("-" * 40)
    
    # Agrupar por CPF
    cpfs = {}
    for evento in eventos:
        cpf = evento['cpf']
        if cpf not in cpfs:
            cpfs[cpf] = []
        cpfs[cpf].append(evento)
    
    for cpf, eventos_cpf in cpfs.items():
        print(f"\n👤 CPF {cpf}:")
        # Ordenar por hora de exibição
        eventos_ordenados = sorted(eventos_cpf, key=lambda x: x['hora_exibicao'])
        
        for evento in eventos_ordenados:
            print(f"  {evento['visualization']}: {evento['hora_exibicao']} → {evento['hora_fim']}")
        
        # Verificar se a ordem está correta (visualization1 deve vir antes de visualization2, etc.)
        for i in range(len(eventos_ordenados) - 1):
            atual = eventos_ordenados[i]
            proximo = eventos_ordenados[i + 1]
            
            # Extrair número da visualização
            num_atual = int(atual['visualization'].replace('visualization', ''))
            num_proximo = int(proximo['visualization'].replace('visualization', ''))
            
            if num_atual > num_proximo:
                problema = f"❌ ORDEM INVERTIDA no CPF {cpf}: {atual['visualization']} ({atual['hora_exibicao']}) vem antes de {proximo['visualization']} ({proximo['hora_exibicao']})"
                print(problema)
                problemas_encontrados.append(problema)
    
    return problemas_encontrados

def testar_correcao():
    """Testa a correção da sequência cronológica"""
    print("🧪 TESTE DA CORREÇÃO DA SEQUÊNCIA CRONOLÓGICA")
    print("=" * 60)
    
    # Imagem de teste (base64 simples)
    imagem_teste = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    
    # Limpar eventos existentes
    print("\n1. Limpando eventos existentes...")
    limpar_eventos()
    
    # Cadastrar CPFs de teste
    print("\n2. Cadastrando CPFs de teste...")
    cpfs_teste = ["11111111111", "22222222222", "33333333333"]
    
    for cpf in cpfs_teste:
        cadastrar_cpf(cpf, imagem_teste)
    
    # Aguardar um pouco
    print("\n3. Aguardando 2 segundos...")
    time.sleep(2)
    
    # Enviar webhooks em sequência rápida
    print("\n4. Enviando webhooks em sequência...")
    for i, cpf in enumerate(cpfs_teste):
        print(f"   Enviando webhook {i+1}/3 para CPF {cpf}...")
        enviar_webhook(cpf)
        time.sleep(1)  # Pequena pausa entre webhooks
    
    # Aguardar processamento
    print("\n5. Aguardando processamento...")
    time.sleep(3)
    
    # Listar e analisar eventos
    print("\n6. Analisando eventos criados...")
    eventos = listar_eventos()
    
    if eventos:
        print(f"📊 Total de eventos criados: {len(eventos)}")
        problemas = analisar_sequencia(eventos)
        
        if problemas:
            print(f"\n❌ PROBLEMAS ENCONTRADOS ({len(problemas)}):")
            for problema in problemas:
                print(f"   {problema}")
            return False
        else:
            print(f"\n✅ NENHUM PROBLEMA ENCONTRADO!")
            print("   A sequência cronológica está correta.")
            return True
    else:
        print("❌ Nenhum evento foi criado!")
        return False

if __name__ == "__main__":
    testar_correcao() 