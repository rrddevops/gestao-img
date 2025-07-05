#!/usr/bin/env python3
"""
Script para verificar quais CPFs existem no banco de dados
"""

import requests
import json

def verificar_cpfs():
    """Verifica quais CPFs existem no banco de dados"""
    
    print("=== VERIFICANDO CPFs NO BANCO DE DADOS ===")
    
    try:
        # Testa o endpoint de listagem de imagens
        url = "http://localhost:5001/list"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            # Tenta fazer parse do HTML para extrair CPFs
            html_content = response.text
            
            # Procura por CPFs no HTML (padrão simples)
            import re
            cpf_pattern = r'\b\d{11}\b'
            cpfs = re.findall(cpf_pattern, html_content)
            
            print(f"CPFs encontrados no banco: {cpfs}")
            
            if cpfs:
                print("\nTestando acesso direto às imagens:")
                for cpf in cpfs[:5]:  # Testa apenas os primeiros 5
                    try:
                        img_url = f"http://localhost:5001/image/{cpf}"
                        img_response = requests.get(img_url, timeout=5)
                        if img_response.status_code == 200:
                            print(f"  ✓ CPF {cpf}: Imagem acessível")
                        else:
                            print(f"  ✗ CPF {cpf}: Erro {img_response.status_code}")
                    except Exception as e:
                        print(f"  ✗ CPF {cpf}: Erro de conexão - {e}")
            else:
                print("Nenhum CPF encontrado no HTML")
                
        else:
            print(f"Erro ao acessar lista: {response.status_code}")
            
    except Exception as e:
        print(f"Erro ao verificar CPFs: {e}")

def testar_webhook_com_cpf_valido():
    """Testa o webhook com um CPF que sabemos que existe"""
    
    print("\n=== TESTANDO WEBHOOK COM CPF VÁLIDO ===")
    
    # CPFs que vimos no teste anterior
    cpfs_para_testar = ["22222222221", "22222222222", "22222222223", "22222222224"]
    
    for cpf in cpfs_para_testar:
        print(f"\nTestando CPF: {cpf}")
        
        try:
            # Primeiro verifica se a imagem existe
            img_url = f"http://localhost:5001/image/{cpf}"
            img_response = requests.get(img_url, timeout=5)
            
            if img_response.status_code == 200:
                print(f"  ✓ Imagem existe para CPF {cpf}")
                
                # Testa o webhook
                webhook_url = "http://localhost:5002/webhook"
                data = {"cpf": cpf}
                
                webhook_response = requests.post(webhook_url, json=data, timeout=10)
                
                if webhook_response.status_code == 200:
                    result = webhook_response.json()
                    print(f"  ✓ Webhook sucesso: {result.get('message', 'OK')}")
                    
                    # Verifica se os jobs foram criados
                    import time
                    time.sleep(2)
                    
                    for i in range(1, 4):  # Testa apenas os primeiros 3 servidores
                        status_url = f"http://localhost:808{i+2}/schedule-status"
                        try:
                            status_response = requests.get(status_url, timeout=5)
                            if status_response.status_code == 200:
                                status = status_response.json()
                                jobs_count = len(status.get('scheduled_jobs', {}))
                                print(f"    visualization{i}: {jobs_count} jobs")
                            else:
                                print(f"    visualization{i}: erro {status_response.status_code}")
                        except:
                            print(f"    visualization{i}: erro de conexão")
                    
                    break  # Para no primeiro CPF válido
                    
                else:
                    print(f"  ✗ Erro no webhook: {webhook_response.status_code}")
                    
            else:
                print(f"  ✗ Imagem não existe para CPF {cpf}")
                
        except Exception as e:
            print(f"  ✗ Erro ao testar CPF {cpf}: {e}")

if __name__ == "__main__":
    verificar_cpfs()
    testar_webhook_com_cpf_valido() 