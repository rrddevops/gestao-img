# Sistema de Agendamento Baseado em DateTime

## Visão Geral

O sistema foi completamente reescrito para usar controle de tempo baseado em **datetime** em vez de milissegundos, garantindo precisão na ordem de exibição das imagens, especialmente em filas grandes.

## 🆕 NOVO: Interface Simplificada

**Agora você pode agendar imagens enviando apenas o CPF!** O sistema gerencia automaticamente os horários baseado no tempo atual do servidor.

### Formato Simplificado (Recomendado)
```json
{
    "cpf": "12345678901"
}
```

**Resposta:**
```json
{
    "message": "Agendamento realizado com sucesso",
    "cpf": "12345678901",
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

## Principais Mudanças

### 1. Controle de Tempo
- **Antes**: Milissegundos (ex: 30000ms)
- **Agora**: Formato HH:MM:SS (ex: 00:00:30)

### 2. Interface Simplificada
- **Antes**: CPF + entry_time + wait_time
- **Agora**: Apenas CPF (sistema gerencia horários automaticamente)

### 3. Estrutura de Dados
O sistema agora pode receber:
- **CPF**: Identificador da pessoa (formato simplificado)
- **entry_time**: Horário de entrada (formato HH:MM:SS) - opcional
- **wait_time**: Tempo até aparecer na primeira visualização (formato HH:MM:SS) - opcional

### 4. Lógica de Exibição
1. **Primeira exibição**: `entry_time + wait_time` (ou tempo atual + 10s no formato simplificado)
2. **Demais visualizações**: A cada 10 segundos após a anterior
3. **Ordem cronológica**: Respeita a ordem de chegada por horário de entrada

## Exemplo de Funcionamento

### Formato Simplificado
Se um CPF for enviado às **20:00:00**:

```
Visualization1: 20:00:10 (atual + 10s)
Visualization2: 20:00:20 (+10s)
Visualization3: 20:00:30 (+10s)
Visualization4: 20:00:40 (+10s)
Visualization5: 20:00:50 (+10s)
Visualization6: 20:01:00 (+10s)
```

### Formato Manual
Se alguém entrou às **20:00:00** com tempo de espera de **30 segundos**:

```
Visualization1: 20:00:30 (entrada + 30s)
Visualization2: 20:00:40 (+10s)
Visualization3: 20:00:50 (+10s)
Visualization4: 20:01:00 (+10s)
Visualization5: 20:01:10 (+10s)
Visualization6: 20:01:20 (+10s)
```

## APIs Disponíveis

### 1. Agendamento Simplificado (NOVO - RECOMENDADO)
```http
POST /schedule
Content-Type: application/json

{
    "cpf": "12345678901"
}
```

### 2. Agendamento Manual (Sistema Avançado)
```http
POST /schedule
Content-Type: application/json

{
    "cpf": "12345678901",
    "entry_time": "20:00:00",
    "wait_time": "00:00:30"
}
```

### 3. Agendamento Legado (Compatibilidade)
```http
POST /display
Content-Type: application/json

{
    "cpf": "12345678901",
    "display_time": 30000
}
```

### 4. Status dos Agendamentos
```http
GET /schedule-status
```

### 5. Status da Fila (Legado)
```http
GET /queue-status
```

## Configuração das Visualizações

| Visualização | Porta Externa | Delay (segundos) |
|--------------|---------------|------------------|
| visualization1 | 8083 | 0 |
| visualization2 | 8084 | 10 |
| visualization3 | 8085 | 20 |
| visualization4 | 8086 | 30 |
| visualization5 | 8087 | 40 |
| visualization6 | 8088 | 50 |

## Como Usar

### 1. Via Webhook Simplificado (Recomendado)
```python
import requests

# Agendamento simplificado - apenas CPF
payload = {'cpf': '12345678901'}
response = requests.post('http://localhost:5002/schedule', json=payload)
print(response.json())
```

### 2. Via Webhook Manual (Sistema Avançado)
```python
import requests

# Agendamento com controle manual de horários
payload = {
    'cpf': '12345678901',
    'entry_time': '20:00:00',
    'wait_time': '00:00:30'
}
response = requests.post('http://localhost:5002/schedule', json=payload)
```

### 3. Via Script de Teste Simplificado
```bash
python test_webhook.py
```

### 4. Via Script de Teste Completo
```bash
python test_scheduler.py
```

### 5. Monitoramento em Tempo Real
Acesse as URLs de visualização:
- http://localhost:8083/view/ (Visualization1)
- http://localhost:8084/view/ (Visualization2)
- http://localhost:8085/view/ (Visualization3)
- http://localhost:8086/view/ (Visualization4)
- http://localhost:8087/view/ (Visualization5)
- http://localhost:8088/view/ (Visualization6)

## Estrutura do Banco de Dados

### Tabela: schedule_entries
```sql
CREATE TABLE schedule_entries (
    sequence_id SERIAL PRIMARY KEY,   -- Campo autonumero sequencial
    id VARCHAR NOT NULL,              -- CPF + visualization + timestamp
    cpf VARCHAR NOT NULL,             -- CPF da pessoa
    visualization_name VARCHAR NOT NULL, -- Nome da visualização (ex: visualization1)
    entry_time TIME NOT NULL,         -- Horário de entrada (HH:MM:SS)
    wait_time TIME NOT NULL,          -- Tempo de espera (HH:MM:SS)
    display_time TIME NOT NULL,       -- Horário que será exibido (HH:MM:SS)
    display_datetime TIMESTAMP WITH TIME ZONE NOT NULL, -- Data e hora completa da exibição
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## Tecnologias Utilizadas

- **APScheduler**: Agendamento de tarefas
- **SQLAlchemy**: ORM para banco de dados
- **Flask**: Framework web
- **PostgreSQL**: Banco de dados principal

## Vantagens do Novo Sistema

1. **Simplicidade**: Apenas CPF necessário para agendamento
2. **Precisão**: Controle exato de horários
3. **Escalabilidade**: Suporte a filas grandes
4. **Ordenação**: Respeita ordem cronológica
5. **Flexibilidade**: Configuração por visualização
6. **Compatibilidade**: Mantém APIs legadas

## Tratamento de Erros

### Validação de Formato
- **CPF**: Deve existir no banco de dados
- **entry_time**: Deve estar no formato HH:MM:SS (quando fornecido)
- **wait_time**: Deve estar no formato HH:MM:SS (quando fornecido)

### Tratamento de Horários
- Se o horário já passou hoje, agenda para amanhã
- Suporte a horários que passam da meia-noite
- Validação de formato de tempo
- **NOVO**: Gerenciamento automático de horários no formato simplificado

## Monitoramento

### Status dos Agendamentos
```python
response = requests.get('http://localhost:5002/schedule-status')
status = response.json()

print(f"Total de jobs: {status['total_jobs']}")
print(f"Imagens atuais: {status['current_images']}")
print(f"Jobs agendados: {status['scheduled_jobs']}")
```

### Verificar Filas dos Visualizadores
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
    response = requests.get(f"{url}/queue-status")
    if response.status_code == 200:
        data = response.json()
        print(f"{name}: {data['queue_size']} imagens na fila")
```

### Logs do Sistema
O sistema gera logs detalhados:
- Agendamentos realizados
- Exibições em andamento
- Erros de processamento

## Migração do Sistema Anterior

O sistema mantém compatibilidade total com o anterior:
- APIs legadas continuam funcionando
- Conversão automática de milissegundos para datetime
- Transição gradual possível
- **NOVO**: Interface simplificada para novos usuários

## Troubleshooting

### Problemas Comuns

1. **Imagem não aparece**
   - Verificar se CPF existe no banco
   - Verificar formato dos horários (se usando formato manual)
   - Verificar logs do scheduler

2. **Horário incorreto**
   - Validar formato HH:MM:SS (se usando formato manual)
   - Verificar timezone do servidor
   - Confirmar horário de entrada

3. **Ordem incorreta**
   - Verificar horários de entrada
   - Confirmar configuração de delays
   - Verificar jobs agendados

### Comandos Úteis

```bash
# Verificar status dos containers
docker-compose ps

# Ver logs do scheduler
docker-compose logs app3-visualizacao

# Testar agendamento simplificado
python test_webhook.py

# Testar agendamento completo
python test_scheduler.py

# Verificar banco de dados
docker-compose exec postgres psql -U postgres -d gestao_img -c "SELECT * FROM schedule_entries;"

# Contar entradas na tabela
docker-compose exec postgres psql -U postgres -d gestao_img -c "SELECT COUNT(*) as total_entries FROM schedule_entries;"

# Limpar agendamentos
docker-compose exec postgres psql -U postgres -d gestao_img -c "DELETE FROM schedule_entries;"

# Reiniciar visualizadores
docker-compose restart visualization1 visualization2 visualization3 visualization4 visualization5 visualization6

# Teste rápido via cURL
curl -X POST http://localhost:5002/schedule \
  -H "Content-Type: application/json" \
  -d '{"cpf": "88888888888"}'

# Verificar filas
curl http://localhost:8083/queue-status
curl http://localhost:8084/queue-status
curl http://localhost:8085/queue-status
curl http://localhost:8086/queue-status
curl http://localhost:8087/queue-status
curl http://localhost:8088/queue-status
``` 