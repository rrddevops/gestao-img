#!/usr/bin/env python3
"""
Script para testar sequência simultânea de webhooks
"""

import requests
import time
import json
import threading

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

def enviar_webhook_simultaneo(cpf):
    """Envia webhook em thread separada para simular envio simultâneo"""
    time.sleep(0.1)  # Pequeno delay para simular simultaneidade
    enviar_webhook(cpf)

def listar_eventos_por_visualizacao():
    """Lista eventos agrupados por visualização"""
    try:
        response = requests.get("http://localhost:8000/webhook/eventos")
        if response.status_code == 200:
            eventos = response.json()
            print(f"\n📋 Total de eventos: {len(eventos)}")
            
            # Agrupar por visualização
            visualizations = {}
            for evento in eventos:
                viz = evento['visualization']
                if viz not in visualizations:
                    visualizations[viz] = []
                visualizations[viz].append(evento)
            
            # Mostrar sequência por visualização
            print("\n🕐 SEQUÊNCIA POR VISUALIZAÇÃO:")
            print("=" * 80)
            
            for viz in sorted(visualizations.keys()):
                print(f"\n📺 {viz}:")
                eventos_viz = sorted(visualizations[viz], key=lambda x: x['hora_exibicao'])
                
                for i, evento in enumerate(eventos_viz):
                    print(f"   {i+1}. CPF {evento['cpf']}: {evento['hora_exibicao']} → {evento['hora_fim']}")
                
                # Verificar sequência
                if len(eventos_viz) > 1:
                    for i in range(len(eventos_viz) - 1):
                        fim_atual = eventos_viz[i]['hora_fim']
                        inicio_proximo = eventos_viz[i+1]['hora_exibicao']
                        
                        if fim_atual >= inicio_proximo:
                            print(f"   ⚠️  SOBREPOSIÇÃO: {fim_atual} ≥ {inicio_proximo}")
                        else:
                            diferenca = calcular_diferenca_tempo(fim_atual, inicio_proximo)
                            print(f"   ✅ Intervalo: {diferenca} segundos")
            
            return eventos
        else:
            print(f"❌ Erro ao listar eventos: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Erro ao listar eventos: {e}")
        return []

def calcular_diferenca_tempo(tempo1_str, tempo2_str):
    """Calcula diferença entre dois tempos em segundos"""
    try:
        from datetime import datetime, time
        
        # Converter strings para time
        t1 = datetime.strptime(tempo1_str, "%H:%M:%S.%f").time()
        t2 = datetime.strptime(tempo2_str, "%H:%M:%S.%f").time()
        
        # Converter para datetime para cálculo
        dt1 = datetime.combine(datetime.today(), t1)
        dt2 = datetime.combine(datetime.today(), t2)
        
        # Calcular diferença
        diff = dt2 - dt1
        return diff.total_seconds()
    except:
        return "N/A"

def testar_sequencia_simultanea():
    """Testa envio simultâneo de webhooks"""
    print("🧪 TESTE DE SEQUÊNCIA SIMULTÂNEA")
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
    
    # 2. Enviar webhooks simultaneamente
    print("\n2️⃣ Enviando webhooks simultaneamente...")
    threads = []
    
    for cpf in cpfs_teste:
        thread = threading.Thread(target=enviar_webhook_simultaneo, args=(cpf,))
        threads.append(thread)
        thread.start()
    
    # Aguardar todas as threads terminarem
    for thread in threads:
        thread.join()
    
    # 3. Listar eventos por visualização
    print("\n3️⃣ Listando eventos por visualização...")
    eventos = listar_eventos_por_visualizacao()
    
    if eventos:
        # 4. Mostrar status
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

def main():
    testar_sequencia_simultanea()

if __name__ == "__main__":
    main() 