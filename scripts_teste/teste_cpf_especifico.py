#!/usr/bin/env python3
"""
Script para testar com um CPF específico que sabemos que existe
"""

import requests
import json
import time

def testar_cpf_especifico():
    """Testa com um CPF específico"""
    
    # CPF que vimos nos agendamentos do banco
    cpf_teste = "22222222221"
    
    print(f"=== TESTANDO COM CPF ESPECÍFICO: {cpf_teste} ===")
    
    try:
        # 1. Testa se a imagem existe no servidor de cadastro
        print("1. Verificando se a imagem existe...")
        cadastro_url = f"http://localhost:5001/image/{cpf_teste}"
        response = requests.get(cadastro_url, timeout=10)
        
        if response.status_code == 200:
            print(f"   ✓ Imagem existe para CPF {cpf_teste}")
            
            # 2. Testa o webhook
            print("2. Enviando webhook...")
            webhook_url = "http://localhost:5002/webhook"
            data = {"cpf": cpf_teste}
            
            webhook_response = requests.post(webhook_url, json=data, timeout=10)
            
            if webhook_response.status_code == 200:
                result = webhook_response.json()
                print(f"   ✓ Webhook sucesso: {result.get('message', 'OK')}")
                
                # 3. Aguarda um pouco e verifica os jobs
                print("3. Aguardando 3 segundos...")
                time.sleep(3)
                
                # 4. Verifica se os jobs foram criados em cada servidor
                print("4. Verificando jobs nos servidores...")
                for i in range(1, 7):
                    status_url = f"http://localhost:808{i+2}/schedule-status"
                    try:
                        status_response = requests.get(status_url, timeout=5)
                        if status_response.status_code == 200:
                            status = status_response.json()
                            jobs_count = len(status.get('scheduled_jobs', {}))
                            current_image = status.get('current_images', {}).get(f'visualization{i}')
                            print(f"   visualization{i}: {jobs_count} jobs, imagem atual: {current_image}")
                        else:
                            print(f"   visualization{i}: erro {status_response.status_code}")
                    except Exception as e:
                        print(f"   visualization{i}: erro de conexão - {e}")
                
                # 5. Força recarregamento e verifica novamente
                print("5. Forçando recarregamento...")
                for i in range(1, 7):
                    reload_url = f"http://localhost:808{i+2}/reload-schedules"
                    try:
                        reload_response = requests.post(reload_url, timeout=10)
                        if reload_response.status_code == 200:
                            print(f"   visualization{i}: recarregamento OK")
                        else:
                            print(f"   visualization{i}: erro no recarregamento")
                    except Exception as e:
                        print(f"   visualization{i}: erro no recarregamento - {e}")
                
                # 6. Verifica novamente após recarregamento
                print("6. Verificando após recarregamento...")
                time.sleep(2)
                for i in range(1, 7):
                    status_url = f"http://localhost:808{i+2}/schedule-status"
                    try:
                        status_response = requests.get(status_url, timeout=5)
                        if status_response.status_code == 200:
                            status = status_response.json()
                            jobs_count = len(status.get('scheduled_jobs', {}))
                            current_image = status.get('current_images', {}).get(f'visualization{i}')
                            print(f"   visualization{i}: {jobs_count} jobs, imagem atual: {current_image}")
                        else:
                            print(f"   visualization{i}: erro {status_response.status_code}")
                    except Exception as e:
                        print(f"   visualization{i}: erro de conexão - {e}")
                        
            else:
                print(f"   ✗ Erro no webhook: {webhook_response.status_code} - {webhook_response.text}")
                
        else:
            print(f"   ✗ Imagem não existe para CPF {cpf_teste} (status: {response.status_code})")
            
    except Exception as e:
        print(f"   ✗ Erro geral: {e}")

def testar_agendamento_direto():
    """Testa agendamento direto no servidor de visualização"""
    
    print(f"\n=== TESTANDO AGENDAMENTO DIRETO ===")
    
    cpf_teste = "22222222221"
    entry_time = "13:10:00"
    wait_time = "00:00:30"
    
    try:
        # Testa agendamento direto no primeiro servidor
        url = "http://localhost:8083/schedule"
        data = {
            "cpf": cpf_teste,
            "entry_time": entry_time,
            "wait_time": wait_time
        }
        
        print(f"Enviando agendamento direto para {cpf_teste}")
        response = requests.post(url, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Agendamento direto sucesso: {result}")
            
            # Verifica se os jobs foram criados
            time.sleep(2)
            status_url = "http://localhost:8083/schedule-status"
            status_response = requests.get(status_url, timeout=5)
            if status_response.status_code == 200:
                status = status_response.json()
                jobs_count = len(status.get('scheduled_jobs', {}))
                print(f"Jobs criados: {jobs_count}")
            else:
                print(f"Erro ao verificar status: {status_response.status_code}")
                
        else:
            print(f"✗ Erro no agendamento direto: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"✗ Erro ao testar agendamento direto: {e}")

if __name__ == "__main__":
    testar_cpf_especifico()
    testar_agendamento_direto() 