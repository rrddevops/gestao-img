# Changelog - Sistema de Gerenciamento de Imagens

## Versão 2.1.0 - Interface Simplificada do Webhook

### 🆕 Novas Funcionalidades

#### 1. Interface Simplificada do Webhook
- **Apenas CPF necessário** para agendamento
- **Gerenciamento automático** de horários pelo servidor
- **Tempo de espera padrão** de 10 segundos
- **Resposta detalhada** com horários agendados

#### 2. Formato Simplificado (Recomendado)
```json
{
    "cpf": "12345678900"
}
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

#### 3. Melhorias no App2-Webhook
- **Detecção automática** do formato de entrada
- **Validação inteligente** de parâmetros
- **Gerenciamento de horários** baseado no tempo do servidor
- **Compatibilidade total** com formato anterior

### 🔧 Melhorias Técnicas

#### 1. Lógica de Agendamento
- **Tempo atual do servidor** como referência
- **Cálculo automático** de horários de exibição
- **Sincronização precisa** entre visualizações
- **Tratamento de horários** que passam da meia-noite

#### 2. Validação e Tratamento de Erros
- **Validação de CPF** no banco de dados
- **Tratamento de formatos** de entrada
- **Mensagens de erro** mais claras
- **Logs detalhados** de processamento

### 📖 Documentação Atualizada

#### Novos Arquivos
- `EXAMPLES.md` - Exemplos práticos de uso
- `test_webhook.py` - Script de teste do formato simplificado

#### Documentação Atualizada
- `README.md` - Destaque para formato simplificado
- `README_SCHEDULER.md` - Seção sobre interface simplificada

### 🧪 Scripts de Teste

#### Novo Script
- `test_webhook.py` - Teste rápido do formato simplificado
- **Agendamento automático** com apenas CPF
- **Verificação de filas** em todos os visualizadores
- **Monitoramento** de sincronização

### 🔄 Compatibilidade

#### Formato Anterior Mantido
- **Formato manual** ainda suportado
- **Controle de horários** personalizado
- **Transição gradual** possível
- **Sem quebra de funcionalidades**

### 🚀 Vantagens da Nova Interface

#### 1. Simplicidade
- **Menos parâmetros** para enviar
- **Menos erros** de configuração
- **Implementação mais rápida**
- **Menor curva de aprendizado**

#### 2. Automatização
- **Horários gerenciados** automaticamente
- **Sincronização precisa** garantida
- **Menos configuração** manual
- **Menos pontos de falha**

#### 3. Flexibilidade
- **Dois formatos** disponíveis
- **Escolha do usuário** baseada na necessidade
- **Migração gradual** possível
- **Compatibilidade total**

### 📊 Exemplos de Uso

#### Formato Simplificado (Recomendado)
```bash
curl -X POST http://localhost:5002/schedule \
  -H "Content-Type: application/json" \
  -d '{"cpf": "12345678900"}'
```

#### Formato Manual (Avançado)
```bash
curl -X POST http://localhost:5002/schedule \
  -H "Content-Type: application/json" \
  -d '{
    "cpf": "12345678900",
    "entry_time": "20:00:00",
    "wait_time": "00:00:30"
  }'
```

### 🎯 Próximos Passos

#### Melhorias Futuras
- **Interface web** para agendamento
- **Dashboard** de monitoramento
- **Notificações** em tempo real
- **API REST** completa
- **Autenticação** e autorização

---

## Versão 2.0.0 - Sistema de Agendamento Baseado em DateTime

### 🆕 Novas Funcionalidades

#### 1. Sistema de Agendamento Preciso
- **Controle de tempo baseado em datetime** em vez de milissegundos
- **Formato HH:MM:SS** para entrada e tempo de espera
- **APScheduler** para agendamento preciso de tarefas
- **6 visualizações simultâneas** com delays configuráveis

#### 2. APIs Novas
- `POST /schedule` - Agendamento baseado em horário
- `GET /schedule-status` - Status dos agendamentos
- Suporte a múltiplas visualizações (8083-8088)

#### 3. Estrutura de Dados Melhorada
- Nova tabela `schedule_entries` para rastreamento
- Campos `entry_time` e `wait_time` em formato TIME
- Ordenação cronológica automática

### 🔧 Melhorias Técnicas

#### 1. App3-Visualizacao
- **Reescrita completa** do sistema de agendamento
- **APScheduler** para gerenciamento de jobs
- **Configuração centralizada** das visualizações
- **Compatibilidade** com sistema anterior
- **Logs detalhados** de agendamento e exibição

#### 2. App2-Webhook
- **Suporte duplo** a sistemas legado e novo
- **Validação de formato** de tempo
- **Notificação assíncrona** para todas as visualizações
- **Status centralizado** dos agendamentos

#### 3. Banco de Dados
- **PostgreSQL** como banco principal
- **Tabela schedule_entries** para rastreamento
- **Índices otimizados** para consultas de tempo

### 📊 Configuração das Visualizações

| Visualização | Porta | Delay | Descrição |
|--------------|-------|-------|-----------|
| visualization1 | 8083 | 0s | Primeira exibição |
| visualization2 | 8084 | 10s | +10 segundos |
| visualization3 | 8085 | 20s | +20 segundos |
| visualization4 | 8086 | 30s | +30 segundos |
| visualization5 | 8087 | 40s | +40 segundos |
| visualization6 | 8088 | 50s | +50 segundos |

### 🧪 Scripts de Teste

#### Novos Scripts
- `test_scheduler.py` - Teste rápido do agendamento
- `example_usage.py` - Exemplos detalhados de uso
- `test_complete_system.py` - Teste completo do sistema
- `start_system.py` - Inicialização automática

#### Funcionalidades dos Scripts
- **Criação automática** de imagens de teste
- **Upload em lote** de imagens
- **Agendamento programático** de exibições
- **Monitoramento em tempo real** do sistema
- **Validação de funcionalidades**

### 📖 Documentação

#### Documentação Atualizada
- `README.md` - Visão geral do sistema
- `README_SCHEDULER.md` - Documentação detalhada do agendamento
- `CHANGELOG.md` - Este arquivo de mudanças

#### Exemplos de Uso
- **Agendamento via API REST**
- **Scripts de teste automatizados**
- **Monitoramento de status**
- **Troubleshooting**

### 🔄 Compatibilidade

#### Sistema Legado
- **APIs antigas mantidas** para compatibilidade
- **Conversão automática** de milissegundos para datetime
- **Transição gradual** possível
- **Sem quebra de funcionalidades**

#### Migração
- **Dados existentes preservados**
- **Configuração automática** de novas funcionalidades
- **Rollback possível** se necessário

### 🚀 Vantagens do Novo Sistema

#### 1. Precisão
- **Controle exato** de horários
- **Sincronização precisa** entre visualizações
- **Eliminação de drift** de tempo

#### 2. Escalabilidade
- **Suporte a filas grandes**
- **Ordenação cronológica** automática
- **Gerenciamento eficiente** de recursos

#### 3. Flexibilidade
- **Configuração por visualização**
- **Tempos de espera personalizáveis**
- **Horários de entrada flexíveis**

#### 4. Monitoramento
- **Status em tempo real**
- **Logs detalhados**
- **Métricas de performance**

### 🐛 Correções

#### Problemas Resolvidos
- **Imprecisão de tempo** com milissegundos
- **Falta de ordenação** cronológica
- **Limitação** a uma visualização
- **Dificuldade de monitoramento**

### 📦 Dependências

#### Novas Dependências
- `APScheduler==3.10.1` - Agendamento de tarefas
- `Pillow==9.5.0` - Processamento de imagens (testes)

#### Dependências Mantidas
- `Flask==2.0.1` - Framework web
- `SQLAlchemy==1.4.23` - ORM
- `psycopg2-binary==2.9.3` - PostgreSQL
- `requests==2.28.1` - HTTP client

### 🔧 Configuração

#### Variáveis de Ambiente
- `POSTGRES_DB=gestao_img`
- `POSTGRES_USER=postgres`
- `POSTGRES_PASSWORD=postgres`
- `POSTGRES_HOST=postgres`
- `DELAY` - Delay específico por visualização

#### Docker Compose
- **6 instâncias** de visualização
- **Portas mapeadas** 8083-8088
- **Volumes persistentes** para dados
- **Rede interna** para comunicação

### 🎯 Próximos Passos

#### Melhorias Futuras
- **Interface web** para agendamento
- **Dashboard** de monitoramento
- **Notificações** em tempo real
- **API REST** completa
- **Autenticação** e autorização

#### Otimizações
- **Cache** de imagens
- **Compressão** automática
- **CDN** para distribuição
- **Load balancing** automático

---

## Como Usar

### Inicialização Rápida
```bash
python start_system.py
```

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

### Teste Completo
```bash
python test_complete_system.py
```

### Parar Sistema
```bash
docker-compose down
```

---

**Data da Release:** $(date)
**Versão:** 2.1.0
**Compatibilidade:** Total com versão anterior 