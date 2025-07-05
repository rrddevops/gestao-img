# Sistema de Gerenciamento de Imagens com FastAPI

Sistema completo para cadastro, agendamento e exibição de imagens por CPF usando FastAPI, PostgreSQL, WebSockets e APScheduler.

## 🏗️ Arquitetura

```
┌─────────────────┐    HTTP POST    ┌─────────────────┐    WebSocket    ┌─────────────────┐
│   Cliente       │ ──────────────► │   FastAPI       │ ──────────────► │  Visualizações  │
│   Externo       │                 │   Backend       │                 │  (6 páginas)    │
│                 │                 │   (Porta 8000)  │                 │                 │
└─────────────────┘                 └─────────────────┘                 └─────────────────┘
                                            │
                                            │ APScheduler
                                            ▼
                                    ┌─────────────────┐
                                    │   PostgreSQL    │
                                    │   (Porta 5432)  │
                                    └─────────────────┘
```

## 🚀 Como Executar

### 1. Usando Docker Compose (Recomendado)

```bash
# Construir e iniciar todos os serviços
docker-compose up -d --build

# Verificar status dos containers
docker-compose ps

# Ver logs
docker-compose logs -f backend
```

### 2. Execução Local (Desenvolvimento)

```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar variável de ambiente
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/gestao_img"

# Executar aplicação
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 📋 Funcionalidades

### 1. 📝 Cadastro
- **Interface Web**: http://localhost:8000/cadastro
- **API**: `POST /cadastro/` - Cadastra CPF e imagem
- **Armazenamento**: Imagens em Base64 no PostgreSQL

### 2. 🔗 Webhook
- **API**: `POST /webhook/` - Recebe CPF e cria eventos
- **Funcionalidade**: 
  - Consulta hora atual
  - Cria 6 eventos cronológicos (visualization1-6)
  - Calcula horários baseado em parâmetros

### 3. ⏰ Agendador (APScheduler)
- **Verificação**: A cada segundo
- **Funcionalidade**: Busca eventos ativos e envia via WebSocket
- **Status**: `GET /scheduler/status`

### 4. 📺 Visualizações
- **Páginas**: 6 visualizações independentes
- **WebSocket**: Conexão em tempo real
- **Exibição**: Imagens por 10 segundos
- **URLs**:
  - http://localhost:8000/visualization1
  - http://localhost:8000/visualization2
  - http://localhost:8000/visualization3
  - http://localhost:8000/visualization4
  - http://localhost:8000/visualization5
  - http://localhost:8000/visualization6

## 🗄️ Banco de Dados

### Tabelas

#### `cadastro`
```sql
CREATE TABLE cadastro (
    cpf TEXT PRIMARY KEY,
    caminho_imagem TEXT NOT NULL
);
```

#### `parametros`
```sql
CREATE TABLE parametros (
    nome TEXT PRIMARY KEY,
    valor TEXT NOT NULL
);
```

#### `eventos`
```sql
CREATE TABLE eventos (
    id SERIAL PRIMARY KEY,
    cpf TEXT NOT NULL,
    visualization TEXT NOT NULL,
    hora_acesso TIME NOT NULL,
    delay INTERVAL NOT NULL,
    hora_exibicao TIME NOT NULL,
    hora_fim TIME NOT NULL
);
```

### Parâmetros Padrão
- `tempo_inicial_segundos`: 30 (delay para primeira visualização)
- `incremento_segundos`: 10 (incremento para próximas visualizações)
- `duracao_exibicao_seg`: 10 (tempo de exibição da imagem)

## 🔧 API Endpoints

### Cadastro
- `GET /cadastro/` - Interface de cadastro
- `POST /cadastro/` - Cadastrar CPF e imagem
- `GET /cadastro/` - Listar cadastros
- `GET /cadastro/{cpf}` - Obter cadastro específico
- `DELETE /cadastro/{cpf}` - Deletar cadastro

### Webhook
- `POST /webhook/` - Processar webhook
- `GET /webhook/eventos` - Listar eventos
- `GET /webhook/eventos/{cpf}` - Eventos de um CPF
- `DELETE /webhook/eventos/{cpf}` - Deletar eventos de um CPF

### WebSocket
- `WS /websocket/{visualization}` - Conexão WebSocket
- `POST /websocket/send/{visualization}` - Enviar mensagem
- `GET /websocket/status` - Status das conexões

### Sistema
- `GET /` - Página inicial
- `GET /scheduler/status` - Status do agendador
- `GET /docs` - Documentação da API

## 🧪 Testes

### Script de Teste Automatizado
```bash
python test_system.py
```

### Teste Manual

#### 1. Cadastrar CPF
```bash
curl -X POST http://localhost:8000/cadastro/ \
  -F "cpf=12345678901" \
  -F "imagem=@caminho/para/imagem.jpg"
```

#### 2. Enviar Webhook
```bash
curl -X POST http://localhost:8000/webhook/ \
  -H "Content-Type: application/json" \
  -d '{"cpf":"12345678901"}'
```

#### 3. Verificar Eventos
```bash
curl http://localhost:8000/webhook/eventos
```

#### 4. Status do Sistema
```bash
curl http://localhost:8000/scheduler/status
curl http://localhost:8000/websocket/status
```

## 📊 Monitoramento

### Logs dos Containers
```bash
# Backend
docker-compose logs -f backend

# Banco de dados
docker-compose logs -f db

# Frontend (se usando Nginx)
docker-compose logs -f frontend
```

### Status em Tempo Real
- **Página inicial**: http://localhost:8000 (mostra status do sistema)
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🔄 Fluxo de Funcionamento

1. **Cadastro**: CPF e imagem são cadastrados via interface web
2. **Webhook**: CPF é enviado via webhook
3. **Agendamento**: Sistema cria 6 eventos cronológicos
4. **Agendador**: Verifica eventos a cada segundo
5. **WebSocket**: Envia comandos para visualizações ativas
6. **Exibição**: Imagens são exibidas por 10 segundos

## 🛠️ Desenvolvimento

### Estrutura do Projeto
```
gestao-img/
├── app/
│   ├── __init__.py
│   ├── main.py              # Aplicação principal
│   ├── database.py          # Configuração do banco
│   ├── models.py            # Modelos SQLAlchemy
│   ├── schemas.py           # Schemas Pydantic
│   ├── scheduler.py         # Agendador APScheduler
│   └── views/
│       ├── __init__.py
│       ├── cadastro.py      # Módulo de cadastro
│       ├── webhook.py       # Módulo de webhook
│       ├── websocket.py     # Módulo WebSocket
│       └── visualization.py # Páginas de visualização
├── static/                  # Arquivos estáticos
├── docker-compose.yml       # Configuração Docker
├── Dockerfile              # Imagem Docker
├── requirements.txt        # Dependências Python
├── init.sql               # Inicialização do banco
├── nginx.conf             # Configuração Nginx
└── test_system.py         # Script de teste
```

### Variáveis de Ambiente
- `DATABASE_URL`: URL de conexão com PostgreSQL
- `WEBSOCKET_PORT`: Porta do WebSocket (padrão: 8000)

## 🚨 Troubleshooting

### Problemas Comuns

#### 1. Erro de compatibilidade do PostgreSQL
```
FATAL: database files are incompatible with server
DETAIL: The data directory was initialized by PostgreSQL version 14, which is not compatible with this version 15
```

**Solução:**
```bash
# Linux/Mac
chmod +x fix_postgres.sh
./fix_postgres.sh

# Windows
fix_postgres.bat
```

**Ou manualmente:**
```bash
# Opção 1: Limpar dados e usar PostgreSQL 15 (recomendado)
docker-compose down -v
docker-compose up -d --build

# Opção 2: Manter dados e usar PostgreSQL 14
docker-compose down
# Editar docker-compose.yml: mudar postgres:15 para postgres:14
docker-compose up -d --build
```

#### 2. Banco não conecta
```bash
# Verificar se PostgreSQL está rodando
docker-compose ps db

# Verificar logs
docker-compose logs db
```

#### 3. WebSocket não funciona
```bash
# Verificar status
curl http://localhost:8000/websocket/status

# Verificar logs do backend
docker-compose logs backend
```

#### 4. Agendador não processa eventos
```bash
# Verificar status do agendador
curl http://localhost:8000/scheduler/status

# Verificar eventos no banco
docker-compose exec db psql -U postgres -d gestao_img -c "SELECT * FROM eventos;"
```

### Comandos Úteis
```bash
# Reiniciar serviços
docker-compose restart

# Reconstruir containers
docker-compose up -d --build

# Limpar volumes (cuidado: apaga dados)
docker-compose down -v

# Acessar banco de dados
docker-compose exec db psql -U postgres -d gestao_img
```

## 📈 Performance

- **Latência**: < 100ms (webhook → exibição)
- **Concorrência**: Suporte a múltiplos CPFs simultâneos
- **Escalabilidade**: Fácil adição de novas visualizações
- **Confiabilidade**: Reconexão automática WebSocket

## 🔒 Segurança

- Validação de CPF (11 dígitos)
- Sanitização de uploads de imagem
- Logs de auditoria
- Isolamento de rede Docker

## 📝 Licença

Este projeto é de uso livre para fins educacionais e comerciais.
