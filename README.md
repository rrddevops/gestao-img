# Sistema de Gerenciamento de Imagens

Este sistema é composto por três aplicações que trabalham em conjunto para gerenciar o upload, processamento e visualização de imagens associadas a CPFs.

## 🆕 NOVO: Sistema de Agendamento Simplificado

O sistema foi completamente atualizado para usar controle de tempo baseado em **datetime** em vez de milissegundos, garantindo precisão na ordem de exibição das imagens, especialmente em filas grandes.

### Principais Melhorias
- ✅ Controle de tempo em formato HH:MM:SS
- ✅ Agendamento preciso baseado em horário de entrada
- ✅ Ordenação cronológica automática
- ✅ Suporte a 6 visualizações simultâneas
- ✅ **NOVO**: Interface simplificada - apenas CPF necessário
- ✅ Compatibilidade com sistema anterior

### Exemplo de Funcionamento
Quando um CPF é enviado via webhook:
```
Horário atual: 20:00:00
Tempo de espera padrão: 10 segundos

Visualization1: 20:00:10 (atual + 10s)
Visualization2: 20:00:20 (+10s)
Visualization3: 20:00:30 (+10s)
Visualization4: 20:00:40 (+10s)
Visualization5: 20:00:50 (+10s)
Visualization6: 20:01:00 (+10s)
```

**📖 Para mais detalhes, consulte [README_SCHEDULER.md](README_SCHEDULER.md)**

## Estrutura do Sistema

### App 1 - Cadastro de Imagens (Porta 5001)
- Responsável pelo upload e armazenamento de imagens
- Armazena as imagens no banco de dados PostgreSQL
- Endpoint: POST /upload

### App 2 - Webhook (Porta 5002)
- Recebe notificações via webhook
- Encaminha solicitações para as aplicações de visualização
- **NOVO**: Interface simplificada - apenas CPF necessário
- **NOVO**: Gerenciamento automático de horários
- Endpoints:
  - POST /webhook (sistema legado)
  - POST /schedule (novo sistema simplificado)
  - GET /schedule-status

### App 3 - Visualização (Portas 8083-8088)
- Gerencia a exibição temporizada das imagens
- **NOVO**: 6 instâncias com agendamento preciso
- **NOVO**: Sistema de agendamento baseado em APScheduler
- Endpoints:
  - POST /display (sistema legado)
  - POST /schedule (novo sistema)
  - GET /schedule-status
  - GET /view/
  - GET /image/<cpf>

## Configuração e Execução

### Usando Docker Compose (Recomendado)

1. Construa e inicie todos os serviços:
```bash
docker-compose up -d --build
```

2. Para parar todos os serviços:
```bash
docker-compose down
```

### Usando Python local (Desenvolvimento)

1. Instale as dependências de cada aplicação:
```bash
cd app1-cadastro && pip install -r requirements.txt
cd ../app2-webhook && pip install -r requirements.txt
cd ../app3-visualizacao && pip install -r requirements.txt
```

2. Inicie cada aplicação em um terminal separado:
```bash
# Terminal 1
cd app1-cadastro && python app.py

# Terminal 2
cd app2-webhook && python app.py

# Terminal 3
cd app3-visualizacao && python app.py
```

## Como Usar

### 1. Cadastrar uma Imagem

```bash
curl -X POST -F "image=@caminho/para/imagem.jpg" -F "cpf=12345678900" http://localhost:5001/upload
```

### 2. Agendamento Simplificado (NOVO - RECOMENDADO)

**Apenas CPF é necessário!** O sistema gerencia automaticamente os horários:

```bash
# Formato simplificado - apenas CPF
curl -X POST -H "Content-Type: application/json" \
  -d '{"cpf": "12345678900"}' \
  http://localhost:5002/schedule
```

**Resposta:**
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

### 3. Agendamento Manual (Sistema Avançado)

Para controle manual de horários:

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{
    "cpf": "12345678900",
    "entry_time": "20:00:00",
    "wait_time": "00:00:30"
  }' \
  http://localhost:5002/schedule
```

### 4. Solicitar Visualização via Webhook (Sistema Legado)

```bash
curl -X POST -H "Content-Type: application/json" -d '{"cpf":"12345678900"}' http://localhost:5002/webhook
```

### 5. Visualizar as Imagens

Após o agendamento, acesse as visualizações:
```
http://localhost:8083/view/ (Visualization1)
http://localhost:8084/view/ (Visualization2)
http://localhost:8085/view/ (Visualization3)
http://localhost:8086/view/ (Visualization4)
http://localhost:8087/view/ (Visualization5)
http://localhost:8088/view/ (Visualization6)
```

### 6. Verificar Status dos Agendamentos

```bash
curl http://localhost:5002/schedule-status
```

## Scripts de Teste

### Teste Rápido do Webhook Simplificado
```bash
python test_webhook.py
```

### Teste Completo do Sistema
```bash
python test_scheduler.py
```

### Exemplos Detalhados
```bash
python example_usage.py
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

## APIs Disponíveis

### Novo Sistema Simplificado (Recomendado)
- `POST /schedule` - Agendamento simplificado (apenas CPF)
- `GET /schedule-status` - Status dos agendamentos

### Sistema Avançado
- `POST /schedule` - Agendamento com controle manual de horários
- `GET /schedule-status` - Status dos agendamentos

### Sistema Legado (Compatibilidade)
- `POST /webhook` - Webhook tradicional
- `POST /display` - Agendamento com milissegundos
- `GET /queue-status` - Status da fila

## Estrutura do Banco de Dados

### Tabela: images
```sql
CREATE TABLE images (
    cpf VARCHAR PRIMARY KEY,
    image_data BYTEA NOT NULL,
    content_type VARCHAR NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Tabela: schedule_entries (NOVO)
```sql
CREATE TABLE schedule_entries (
    id VARCHAR PRIMARY KEY,
    cpf VARCHAR NOT NULL,
    entry_time TIME NOT NULL,
    wait_time TIME NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Tecnologias Utilizadas

- **Flask**: Framework web
- **PostgreSQL**: Banco de dados principal
- **SQLAlchemy**: ORM
- **APScheduler**: Agendamento de tarefas (NOVO)
- **Docker Compose**: Orquestração de containers

## Vantagens do Novo Sistema

1. **Simplicidade**: Apenas CPF necessário para agendamento
2. **Precisão**: Controle exato de horários
3. **Escalabilidade**: Suporte a filas grandes
4. **Ordenação**: Respeita ordem cronológica
5. **Flexibilidade**: Configuração por visualização
6. **Compatibilidade**: Mantém APIs legadas

## Exemplos de Uso

### Python
```python
import requests

# Agendamento simplificado
response = requests.post('http://localhost:5002/schedule', 
                        json={'cpf': '12345678900'})
print(response.json())

# Verificar status
status = requests.get('http://localhost:5002/schedule-status').json()
print(f"Total de jobs: {status['total_jobs']}")
```

### JavaScript/Node.js
```javascript
const response = await fetch('http://localhost:5002/schedule', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ cpf: '12345678900' })
});
const result = await response.json();
console.log(result);
```

### cURL
```bash
# Agendamento simples
curl -X POST http://localhost:5002/schedule \
  -H "Content-Type: application/json" \
  -d '{"cpf": "12345678900"}'

# Verificar filas
curl http://localhost:8083/queue-status
```

## Notas

- O banco de dados PostgreSQL é compartilhado entre todas as aplicações
- As imagens são armazenadas diretamente no banco como dados binários
- O sistema mantém compatibilidade total com a versão anterior
- As aplicações se comunicam através de uma rede Docker interna
- Os dados persistem mesmo após reiniciar os containers devido ao uso de volumes Docker
- O novo sistema usa APScheduler para agendamento preciso de tarefas
- **NOVO**: O webhook simplificado gerencia automaticamente os horários baseado no tempo atual do servidor 