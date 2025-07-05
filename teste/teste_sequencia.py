#!/usr/bin/env python3
"""
Script para testar a sequência correta de eventos no webhook
"""

import requests
import time
import json

def limpar_eventos():
    """Limpa todos os eventos existentes"""
    try:
        response = requests.delete("http://localhost:8000/webhook/eventos")
        if response.status_code == 200:
            print("✅ Eventos limpos")
            return True
        else:
            print(f"❌ Erro ao limpar eventos: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao limpar eventos: {e}")
        return False

def enviar_webhook(cpf):
    """Envia webhook para um CPF"""
    try:
        data = {"cpf": cpf}
        response = requests.post(
            "http://localhost:8000/webhook",
            headers={"Content-Type": "application/json"},
            json=data
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ CPF {cpf}: {result['message']}")
            return True
        else:
            print(f"❌ CPF {cpf}: Erro {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao enviar webhook para {cpf}: {e}")
        return False

def listar_eventos():
    """Lista todos os eventos"""
    try:
        response = requests.get("http://localhost:8000/webhook/eventos")
        if response.status_code == 200:
            eventos = response.json()
            print(f"\n📋 Total de eventos: {len(eventos)}")
            
            # Agrupar por CPF
            cpfs = {}
            for evento in eventos:
                cpf = evento['cpf']
                if cpf not in cpfs:
                    cpfs[cpf] = []
                cpfs[cpf].append(evento)
            
            # Mostrar sequência
            print("\n🕐 SEQUÊNCIA DE EVENTOS:")
            print("=" * 80)
            
            for cpf in sorted(cpfs.keys()):
                print(f"\n👤 CPF: {cpf}")
                eventos_cpf = sorted(cpfs[cpf], key=lambda x: x['hora_exibicao'])
                
                for evento in eventos_cpf:
                    print(f"   {evento['visualization']}: {evento['hora_exibicao']} → {evento['hora_fim']}")
            
            return eventos
        else:
            print(f"❌ Erro ao listar eventos: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Erro ao listar eventos: {e}")
        return []

def verificar_sequencia(eventos):
    """Verifica se a sequência está correta"""
    print("\n🔍 VERIFICAÇÃO DA SEQUÊNCIA:")
    print("=" * 50)
    
    # Agrupar por visualização
    visualizations = {}
    for evento in eventos:
        viz = evento['visualization']
        if viz not in visualizations:
            visualizations[viz] = []
        visualizations[viz].append(evento)
    
    # Verificar cada visualização
    for viz in sorted(visualizations.keys()):
        eventos_viz = sorted(visualizations[viz], key=lambda x: x['hora_exibicao'])
        print(f"\n📺 {viz}:")
        
        for i, evento in enumerate(eventos_viz):
            print(f"   {i+1}. CPF {evento['cpf']}: {evento['hora_exibicao']} → {evento['hora_fim']}")
        
        # Verificar se há sobreposição
        for i in range(len(eventos_viz) - 1):
            fim_atual = eventos_viz[i]['hora_fim']
            inicio_proximo = eventos_viz[i+1]['hora_exibicao']
            
            if fim_atual >= inicio_proximo:
                print(f"   ⚠️  SOBREPOSIÇÃO: {fim_atual} ≥ {inicio_proximo}")
            else:
                print(f"   ✅ Sequência correta: {fim_atual} < {inicio_proximo}")

def main():
    print("🧪 TESTE DE SEQUÊNCIA DE EVENTOS")
    print("=" * 50)
    
    # CPFs para teste
    cpfs_teste = [
        "22222222223",
        "22222222222", 
        "22222222221",
        "22222222224",
        "11111111111"
    ]
    
    # 1. Limpar eventos existentes
    print("\n1️⃣ Limpando eventos existentes...")
    if not limpar_eventos():
        return
    
    # 2. Enviar webhooks sequencialmente
    print("\n2️⃣ Enviando webhooks...")
    for cpf in cpfs_teste:
        enviar_webhook(cpf)
        time.sleep(0.5)  # Pequena pausa entre envios
    
    # 3. Listar eventos
    print("\n3️⃣ Listando eventos...")
    eventos = listar_eventos()
    
    if eventos:
        # 4. Verificar sequência
        verificar_sequencia(eventos)
        
        # 5. Mostrar status
        print("\n4️⃣ Status do sistema:")
        try:
            response = requests.get("http://localhost:8000/webhook/status")
            if response.status_code == 200:
                status = response.json()
                print(f"   Total de eventos: {status['total_eventos']}")
                print(f"   CPFs ativos: {status['cpfs_ativos']}")
        except:
            print("   Não foi possível obter status")
    
    print("\n✅ Teste concluído!")
    print("   Acesse: http://localhost/webhook/eventos para ver os eventos")

if __name__ == "__main__":
    main() 