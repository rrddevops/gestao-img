# Exemplos de Uso - Sistema de Gerenciamento de Imagens

Este documento contém exemplos práticos de como usar o sistema de gerenciamento de imagens, incluindo o novo formato simplificado do webhook.

## 🆕 Formato Simplificado (Recomendado)

### 1. Agendamento Básico - Apenas CPF

**cURL:**
```bash
curl -X POST http://localhost:5002/schedule \
  -H "Content-Type: application/json" \
  -d '{"cpf": "12345678900"}'
```

**Python:**
```python
import requests

response = requests.post('http://localhost:5002/schedule', 
                        json={'cpf': '12345678900'})
print(response.json())
```

**JavaScript/Node.js:**
```javascript
const response = await fetch('http://localhost:5002/schedule', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ cpf: '12345678900' })
});
const result = await response.json();
console.log(result);
```

**Resposta Esperada:**
```json
{
  "message": "Agendamento realizado com sucesso",
  "cpf": "12345678900",
  "entry_time": "20:00:00",
  "wait_time": "00:00:10",
  "scheduled_times": {
    "visualization1": "20:00:10",
    "visualization2": "20:00:20",
    "visualization3": "20:00:30",
    "visualization4": "20:00:40",
    "visualization5": "20:00:50",
    "visualization6": "20:01:00"
  }
}
```

### 2. Upload de Imagem

**cURL:**
```bash
curl -X POST -F "image=@caminho/para/imagem.jpg" \
  -F "cpf=12345678900" \
  http://localhost:5001/upload
```

**Python:**
```python
import requests

with open('caminho/para/imagem.jpg', 'rb') as f:
    files = {'image': f}
    data = {'cpf': '12345678900'}
    response = requests.post('http://localhost:5001/upload', 
                           files=files, data=data)
print(response.json())
```

## Formato Avançado (Controle Manual)

### 3. Agendamento com Horários Específicos

**cURL:**
```bash
curl -X POST http://localhost:5002/schedule \
  -H "Content-Type: application/json" \
  -d '{
    "cpf": "12345678900",
    "entry_time": "20:00:00",
    "wait_time": "00:00:30"
  }'
```

**Python:**
```python
import requests

payload = {
    'cpf': '12345678900',
    'entry_time': '20:00:00',
    'wait_time': '00:00:30'
}
response = requests.post('http://localhost:5002/schedule', json=payload)
print(response.json())
```

## Monitoramento e Status

### 4. Verificar Status dos Agendamentos

**cURL:**
```bash
curl http://localhost:5002/schedule-status
```

**Python:**
```python
import requests

response = requests.get('http://localhost:5002/schedule-status')
status = response.json()
print(f"Total de jobs: {status['total_jobs']}")
print(f"Imagens atuais: {status['current_images']}")
print(f"Jobs agendados: {status['scheduled_jobs']}")
```

### 5. Verificar Filas dos Visualizadores

**cURL:**
```bash
curl http://localhost:8083/queue-status
curl http://localhost:8084/queue-status
curl http://localhost:8085/queue-status
curl http://localhost:8086/queue-status
curl http://localhost:8087/queue-status
curl http://localhost:8088/queue-status
```

**Python:**
```python
import requests

servers = [
    ("Visualization1", "http://localhost:8083"),
    ("Visualization2", "http://localhost:8084"),
    ("Visualization3", "http://localhost:8085"),
    ("Visualization4", "http://localhost:8086"),
    ("Visualization5", "http://localhost:8087"),
    ("Visualization6", "http://localhost:8088")
]

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
```

## Scripts de Teste

### 6. Teste Rápido do Webhook Simplificado

Execute o script `test_webhook.py`:
```bash
python test_webhook.py
```

**Conteúdo do script:**
```python
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
```

### 7. Teste Completo do Sistema

Execute o script `test_scheduler.py`:
```bash
python test_scheduler.py
```

## Exemplos de Fluxo Completo

### 8. Fluxo Completo: Upload + Agendamento + Visualização

```python
import requests
import time

# 1. Upload da imagem
print("1. Fazendo upload da imagem...")
with open('imagem.jpg', 'rb') as f:
    files = {'image': f}
    data = {'cpf': '12345678900'}
    response = requests.post('http://localhost:5001/upload', 
                           files=files, data=data)
print(f"Upload: {response.json()}")

# 2. Agendamento simplificado
print("\n2. Agendando exibição...")
response = requests.post('http://localhost:5002/schedule', 
                        json={'cpf': '12345678900'})
print(f"Agendamento: {response.json()}")

# 3. Verificar status
print("\n3. Verificando status...")
response = requests.get('http://localhost:5002/schedule-status')
status = response.json()
print(f"Status: {status}")

# 4. Aguardar e verificar filas
print("\n4. Aguardando 5 segundos...")
time.sleep(5)

servers = [
    ("Visualization1", "http://localhost:8083"),
    ("Visualization2", "http://localhost:8084"),
    ("Visualization3", "http://localhost:8085"),
    ("Visualization4", "http://localhost:8086"),
    ("Visualization5", "http://localhost:8087"),
    ("Visualization6", "http://localhost:8088")
]

print("\n5. Status das filas:")
for name, url in servers:
    response = requests.get(f"{url}/queue-status")
    if response.status_code == 200:
        data = response.json()
        print(f"{name}: {data['queue_size']} imagens na fila")

print("\n6. URLs de visualização:")
for name, url in servers:
    print(f"{name}: {url}/view/")
```

## Comandos de Manutenção

### 9. Limpar Agendamentos

```bash
# Limpar todos os agendamentos
docker-compose exec postgres psql -U postgres -d gestao_img -c "DELETE FROM schedule_entries;"

# Reiniciar visualizadores
docker-compose restart visualization1 visualization2 visualization3 visualization4 visualization5 visualization6
```

### 10. Verificar Logs

```bash
# Logs do webhook
docker-compose logs app2-webhook

# Logs dos visualizadores
docker-compose logs visualization1
docker-compose logs visualization2
docker-compose logs visualization3
docker-compose logs visualization4
docker-compose logs visualization5
docker-compose logs visualization6

# Logs com filtro
docker-compose logs visualization1 | grep -i "88888888888\|error\|exibindo"
```

### 11. Verificar Banco de Dados

```bash
# Ver todas as entradas
docker-compose exec postgres psql -U postgres -d gestao_img -c "SELECT * FROM schedule_entries;"

# Contar entradas
docker-compose exec postgres psql -U postgres -d gestao_img -c "SELECT COUNT(*) as total_entries FROM schedule_entries;"

# Ver imagens cadastradas
docker-compose exec postgres psql -U postgres -d gestao_img -c "SELECT cpf, created_at FROM images;"
```

## URLs de Acesso

### Visualizações
- **Visualization1**: http://localhost:8083/view/
- **Visualization2**: http://localhost:8084/view/
- **Visualization3**: http://localhost:8085/view/
- **Visualization4**: http://localhost:8086/view/
- **Visualization5**: http://localhost:8087/view/
- **Visualization6**: http://localhost:8088/view/

### APIs
- **Upload**: http://localhost:5001/upload
- **Webhook**: http://localhost:5002/schedule
- **Status**: http://localhost:5002/schedule-status

## Configuração dos Delays

| Visualização | Porta | Delay | Primeira Exibição |
|--------------|-------|-------|-------------------|
| visualization1 | 8083 | 0s | entry_time + wait_time |
| visualization2 | 8084 | 10s | +10s |
| visualization3 | 8085 | 20s | +20s |
| visualization4 | 8086 | 30s | +30s |
| visualization5 | 8087 | 40s | +40s |
| visualization6 | 8088 | 50s | +50s |

## Tratamento de Erros

### Erros Comuns e Soluções

1. **CPF não encontrado**
   ```json
   {"error": "CPF não encontrado no banco de dados"}
   ```
   **Solução**: Fazer upload da imagem primeiro

2. **Formato de horário inválido**
   ```json
   {"error": "Formato de horário inválido. Use HH:MM:SS"}
   ```
   **Solução**: Usar formato correto ou usar formato simplificado

3. **Servidor não disponível**
   ```json
   {"error": "Erro de conexão"}
   ```
   **Solução**: Verificar se os containers estão rodando

## Performance e Escalabilidade

### Teste de Múltiplos Agendamentos

```python
import requests
import time
from concurrent.futures import ThreadPoolExecutor

def schedule_cpf(cpf):
    """Agenda um CPF específico"""
    try:
        response = requests.post('http://localhost:5002/schedule', 
                               json={'cpf': cpf})
        return f"CPF {cpf}: {response.status_code}"
    except Exception as e:
        return f"CPF {cpf}: Erro - {e}"

# Teste com 10 CPFs simultâneos
cpfs = [f"1111111111{i:02d}" for i in range(10)]

print("Iniciando teste de performance...")
start_time = time.time()

with ThreadPoolExecutor(max_workers=5) as executor:
    results = list(executor.map(schedule_cpf, cpfs))

end_time = time.time()
print(f"Tempo total: {end_time - start_time:.2f} segundos")
for result in results:
    print(result)
``` 