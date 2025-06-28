# Sistema de Agendamento Baseado em DateTime

## Visão Geral

O sistema foi completamente reescrito para usar controle de tempo baseado em **datetime** em vez de milissegundos, garantindo precisão na ordem de exibição das imagens, especialmente em filas grandes.

## Principais Mudanças

### 1. Controle de Tempo
- **Antes**: Milissegundos (ex: 30000ms)
- **Agora**: Formato HH:MM:SS (ex: 00:00:30)

### 2. Estrutura de Dados
O sistema agora recebe três colunas:
- **CPF**: Identificador da pessoa
- **entry_time**: Horário de entrada (formato HH:MM:SS)
- **wait_time**: Tempo até aparecer na primeira visualização (formato HH:MM:SS)

### 3. Lógica de Exibição
1. **Primeira exibição**: `entry_time + wait_time`
2. **Demais visualizações**: A cada 10 segundos após a anterior
3. **Ordem cronológica**: Respeita a ordem de chegada por horário de entrada

## Exemplo de Funcionamento

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

### 1. Agendamento Baseado em Horário (NOVO)
```http
POST /schedule
Content-Type: application/json

{
    "cpf": "12345678901",
    "entry_time": "20:00:00",
    "wait_time": "00:00:30"
}
```

### 2. Agendamento Legado (Compatibilidade)
```http
POST /display
Content-Type: application/json

{
    "cpf": "12345678901",
    "display_time": 30000
}
```

### 3. Status dos Agendamentos
```http
GET /schedule-status
```

### 4. Status da Fila (Legado)
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

### 1. Via Webhook (Recomendado)
```python
import requests

# Agendamento baseado em horário
payload = {
    'cpf': '12345678901',
    'entry_time': '20:00:00',
    'wait_time': '00:00:30'
}

response = requests.post('http://localhost:5002/schedule', json=payload)
```

### 2. Via Script de Teste
```bash
python test_scheduler.py
```

### 3. Monitoramento em Tempo Real
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
    id VARCHAR PRIMARY KEY,           -- CPF + timestamp
    cpf VARCHAR NOT NULL,             -- CPF da pessoa
    entry_time TIME NOT NULL,         -- Horário de entrada (HH:MM:SS)
    wait_time TIME NOT NULL,          -- Tempo de espera (HH:MM:SS)
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Tecnologias Utilizadas

- **APScheduler**: Agendamento de tarefas
- **SQLAlchemy**: ORM para banco de dados
- **Flask**: Framework web
- **PostgreSQL**: Banco de dados principal

## Vantagens do Novo Sistema

1. **Precisão**: Controle exato de horários
2. **Escalabilidade**: Suporte a filas grandes
3. **Ordenação**: Respeita ordem cronológica
4. **Flexibilidade**: Configuração por visualização
5. **Compatibilidade**: Mantém APIs legadas

## Tratamento de Erros

### Validação de Formato
- **entry_time**: Deve estar no formato HH:MM:SS
- **wait_time**: Deve estar no formato HH:MM:SS
- **CPF**: Deve existir no banco de dados

### Tratamento de Horários
- Se o horário já passou hoje, agenda para amanhã
- Suporte a horários que passam da meia-noite
- Validação de formato de tempo

## Monitoramento

### Status dos Agendamentos
```python
response = requests.get('http://localhost:5002/schedule-status')
status = response.json()

print(f"Total de jobs: {status['total_jobs']}")
print(f"Imagens atuais: {status['current_images']}")
print(f"Jobs agendados: {status['scheduled_jobs']}")
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

## Troubleshooting

### Problemas Comuns

1. **Imagem não aparece**
   - Verificar se CPF existe no banco
   - Verificar formato dos horários
   - Verificar logs do scheduler

2. **Horário incorreto**
   - Validar formato HH:MM:SS
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

# Testar agendamento
python test_scheduler.py

# Verificar banco de dados
docker-compose exec postgres psql -U postgres -d gestao_img -c "SELECT * FROM schedule_entries;"

docker-compose exec postgres psql -U postgres -d gestao_img -c "SELECT COUNT(*) as total_entries FROM schedule_entries;"

docker-compose exec postgres psql -U postgres -d gestao_img -c "DELETE FROM schedule_entries;"

curl -X POST http://localhost:5002/schedule \
  -H "Content-Type: application/json" \
  -d '{"cpf": "88888888888"}'
``` 