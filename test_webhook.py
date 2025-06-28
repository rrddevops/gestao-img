import requests
import json

def test_schedule():
    """Testa o agendamento via webhook - apenas CPF"""
    url = "http://localhost:5002/schedule"
    
    data = {
        "cpf": "88888888888"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.json()
    except Exception as e:
        print(f"Erro: {e}")
        return None

def check_queues():
    """Verifica as filas de todos os visualizadores"""
    servers = [
        ("Servidor 1", "http://localhost:8083"),
        ("Servidor 2", "http://localhost:8084"),
        ("Servidor 3", "http://localhost:8085"),
        ("Servidor 4", "http://localhost:8086"),
        ("Servidor 5", "http://localhost:8087"),
        ("Servidor 6", "http://localhost:8088")
    ]
    
    print("Aguardando 3 segundos...")
    import time
    time.sleep(3)
    
    print("\n=== Status das Filas ===")
    for name, url in servers:
        try:
            response = requests.get(f"{url}/queue-status")
            if response.status_code == 200:
                data = response.json()
                print(f"{name}: {data['queue_size']} imagens na fila")
            else:
                print(f"{name}: Erro {response.status_code}")
        except Exception as e:
            print(f"{name}: Erro de conexão - {e}")

if __name__ == "__main__":
    print("Testando agendamento via webhook...")
    result = test_schedule()
    check_queues() 