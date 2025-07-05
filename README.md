# Sistema de Gerenciamento de Imagens com WebSockets

Este sistema é composto por aplicações que trabalham em conjunto para gerenciar o upload, processamento e visualização de imagens associadas a CPFs usando **comunicação em tempo real via WebSockets**.

## 🆕 NOVO: Sistema WebSocket em Tempo Real

O sistema foi completamente refatorado para usar **WebSockets** em vez de agendamento baseado em banco de dados, garantindo comunicação instantânea e exibição imediata das imagens.

### Principais Melhorias
- ✅ **Comunicação em tempo real** via WebSockets
- ✅ **Exibição instantânea** das imagens
- ✅ **Sincronização garantida** entre visualizadores
- ✅ **Conexões persistentes** com heartbeats
- ✅ **Reconexão automática** em caso de falha
- ✅ **Monitoramento em tempo real** dos servidores
- ✅ **Eliminação de delays** de agendamento

### Arquitetura WebSocket
```
┌─────────────────┐    WebSocket    ┌─────────────────┐
│   Webhook       │ ──────────────► │  Servidor       │
│   (Porta 5002)  │                 │  WebSocket      │
└─────────────────┘                 │  (Porta 8765)   │
                                    └─────────────────┘
                                           │
                                           │ Broadcast
                                           ▼
┌─────────────────┐    WebSocket    ┌─────────────────┐
│ Visualization1  │ ◄────────────── │                 │
│ (Porta 8083)    │                 │                 │
└─────────────────┘                 │                 │
                                    │                 │
┌─────────────────┐    WebSocket    │                 │
│ Visualization2  │ ◄────────────── │                 │
│ (Porta 8084)    │                 │                 │
└─────────────────┘                 │                 │
                                    │                 │
┌─────────────────┐    WebSocket    │                 │
│ Visualization3  │ ◄────────────── │                 │
│ (Porta 8085)    │                 │                 │
└─────────────────┘                 │                 │
                                    │                 │
┌─────────────────┐    WebSocket    │                 │
│ Visualization4  │ ◄────────────── │                 │
│ (Porta 8086)    │                 │                 │
└─────────────────┘                 │                 │
                                    │                 │
┌─────────────────┐    WebSocket    │                 │
│ Visualization5  │ ◄────────────── │                 │
│ (Porta 8087)    │                 │                 │
└─────────────────┘                 │                 │
                                    │                 │
┌─────────────────┐    WebSocket    │                 │
│ Visualization6  │ ◄────────────── │                 │
│ (Porta 8088)    │                 │                 │
└─────────────────┘                 └─────────────────┘
```

**📖 Para mais detalhes, consulte [README_WEBSOCKET.md](README_WEBSOCKET.md)**

## Estrutura do Sistema

### App 1 - Cadastro de Imagens (Porta 5001)
- Responsável pelo upload e armazenamento de imagens
- Armazena as imagens no banco de dados PostgreSQL
- Endpoint: POST /upload

### App 2 - Webhook (Porta 5002)
- Recebe notificações via webhook
- **NOVO**: Envia comandos via WebSocket para exibição instantânea
- **NOVO**: Comunicação em tempo real
- Endpoints:
  - POST /webhook (sistema WebSocket)
  - POST /schedule (sistema WebSocket)
  - GET /schedule-status

### Servidor WebSocket Central (Porta 8765)
- **NOVO**: Gerencia conexões de todos os servidores de visualização
- **NOVO**: Distribui comandos de exibição em tempo real
- **NOVO**: Monitora status dos clientes conectados
- **NOVO**: Suporte a heartbeats e reconexão automática

### App 3 - Visualização (Portas 8083-8088)
- **NOVO**: 6 instâncias com conexão WebSocket
- **NOVO**: Exibição instantânea via WebSocket
- **NOVO**: Cliente WebSocket que se conecta ao servidor central
- Endpoints:
  - GET /view/ (interface de visualização)
  - GET /current-image (imagem atual)
  - GET /image/<cpf> (imagem específica)
  - GET /schedule-status (status do servidor)

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

### 2. Exibição Instantânea via WebSocket (NOVO - RECOMENDADO)

**Exibição imediata via WebSocket!** O sistema envia comandos em tempo real:

```bash
# Enviar CPF para exibição instantânea
curl -X POST -H "Content-Type: application/json" \
  -d '{"cpf": "12345678900"}' \
  http://localhost:5002/webhook
```

**Resposta:**
```json
{
  "message": "CPF 12345678900 enviado para exibição via WebSocket",
  "cpf": "12345678900",
  "entry_time": "20:00:00",
  "wait_time": "00:00:30",
  "websocket_result": {
    "success": true,
    "message": "Comando enviado via WebSocket"
  },
  "view_urls": [
    {
      "server": "Servidor 1",
      "url": "http://localhost:8083/view/",
      "websocket_result": {"success": true}
    }
  ]
}
```

### 3. Verificar Status dos Servidores

```bash
# Status dos agendamentos
curl http://localhost:5002/schedule-status

# Status de cada visualização
curl http://localhost:8083/schedule-status
curl http://localhost:8084/schedule-status
# ... etc
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

### Teste do Sistema WebSocket (RECOMENDADO)
```bash
python teste_websocket.py
```
**Características:**
- Testa conexão com servidor WebSocket
- Verifica webhook com WebSocket
- Testa todos os servidores de visualização
- Mostra status completo do sistema

### Teste Manual via PowerShell
```powershell
# Enviar webhook
Invoke-RestMethod -Uri "http://localhost:5002/webhook" -Method POST -ContentType "application/json" -Body '{"cpf":"11111111111"}'

# Verificar status
Invoke-RestMethod -Uri "http://localhost:8083/schedule-status" -Method GET
```

### Teste Manual via curl (Linux/Mac)
```bash
# Enviar webhook
curl -X POST http://localhost:5002/webhook -H 'Content-Type: application/json' -d '{"cpf":"11111111111"}'

# Verificar status
curl http://localhost:8083/schedule-status

## Monitoramento e Logs

### Logs dos Containers
```bash
# Servidor WebSocket
docker logs gestao-img-websocket-server-1

# Webhook Server
docker logs gestao-img-app2-webhook-1

# Servidores de Visualização
docker logs gestao-img-visualization1-1
docker logs gestao-img-visualization2-1
# ... etc
```

### Status dos Serviços
```bash
# Verificar containers rodando
docker ps

# Verificar logs em tempo real
docker logs -f gestao-img-websocket-server-1
```

### Verificação de Conexões WebSocket
- O servidor WebSocket mostra conexões ativas
- Cada visualização envia heartbeats a cada 30 segundos
- Reconexão automática em caso de falha
- Logs detalhados de comandos enviados/recebidos

### Exemplos Detalhados
```bash
python example_usage.py
```

## Configuração Centralizada das Visualizações

A partir da versão mais recente, **todas as configurações de visualização** (delay, display_seconds, portas, etc.) são centralizadas na tabela `visualization_config` do banco de dados PostgreSQL.

- **Não é mais necessário configurar variáveis de ambiente DELAY** no `docker-compose.yml`.
- **Não é mais necessário editar arquivos JSON de configuração**.
- Todos os parâmetros podem ser consultados e alterados via API REST ou pelo script `gerenciar_configuracoes.py`.

### Como Gerenciar as Configurações

- Para ver todas as configurações atuais:
  ```bash
  python gerenciar_configuracoes.py mostrar
  ```
- Para atualizar uma visualização específica:
  ```bash
  python gerenciar_configuracoes.py atualizar visualization1 45 15
  # (atualiza o delay para 45s e o tempo de exibição para 15s)
  ```
- Para resetar todas as configurações para os valores padrão:
  ```bash
  python gerenciar_configuracoes.py resetar
  ```

### Endpoints Úteis

- `GET /config` — retorna a configuração resumida da instância
- `GET /config/all` — retorna todas as configurações detalhadas do banco
- `POST /config` — atualiza parâmetros de uma visualização
- `POST /config/reset` — reseta todas as configurações para os padrões

### Observações

- Ao alterar as configurações, os agendamentos são recarregados automaticamente.
- O sistema sempre consulta o banco para saber os parâmetros de cada visualização.
- O bloco de inicialização padrão só é usado se o banco estiver vazio (primeira execução ou reset).

## ⚠️ Problema de Timing Resolvido

**Problema anterior**: Durante testes em massa, as imagens não respeitavam os tempos de espera configurados.

**Solução implementada**:
- ✅ `wait_time` agora é baseado no `delay_seconds` da primeira visualização (30s)
- ✅ Novo script `test_webhook_timing.py` com timing correto
- ✅ Delay entre agendamentos para evitar sobreposição
- ✅ **CORRIGIDO**: Alinhamento entre docker-compose e visualization_config.json

**📖 Para detalhes completos, consulte [PROBLEMA_TIMING.md](PROBLEMA_TIMING.md)**

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
    sequence_id SERIAL PRIMARY KEY,
    id VARCHAR NOT NULL,
    cpf VARCHAR NOT NULL,
    visualization_name VARCHAR NOT NULL,
    entry_time TIME NOT NULL,
    wait_time TIME NOT NULL,
    display_time TIME NOT NULL,
    display_datetime TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
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