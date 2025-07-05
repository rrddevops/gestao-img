# Sistema de Visualização com WebSockets

## Visão Geral

Este sistema foi refatorado para usar **WebSockets** em vez de queues e agendamento baseado em banco de dados. A nova arquitetura oferece comunicação em tempo real e exibição imediata de imagens.

## Arquitetura

### Componentes

1. **Servidor WebSocket Central** (`websocket_server.py`)
   - Gerencia conexões de todos os servidores de visualização
   - Distribui comandos de exibição em tempo real
   - Monitora status dos clientes conectados

2. **Clientes WebSocket** (`app3-visualizacao/websocket_client.py`)
   - Cada servidor de visualização se conecta ao servidor central
   - Recebe comandos de exibição instantaneamente
   - Envia confirmações e heartbeats

3. **Servidor Webhook** (`app2-webhook/app.py`)
   - Recebe webhooks externos
   - Envia comandos via WebSocket para exibição imediata
   - Não depende mais de agendamento no banco

4. **Servidores de Visualização** (`app3-visualizacao/app.py`)
   - Mantêm conexão WebSocket ativa
   - Exibem imagens imediatamente ao receber comandos
   - Enviam confirmações de exibição

## Fluxo de Funcionamento

### 1. Inicialização
```
1. Servidor WebSocket central inicia na porta 8765
2. Cada servidor de visualização se conecta via WebSocket
3. Servidores se registram com nome e porta
4. Conexões são mantidas ativas com heartbeats
```

### 2. Recebimento de Webhook
```
1. Webhook recebe CPF via POST /webhook
2. Servidor webhook conecta ao WebSocket central
3. Envia comando 'display_image' com CPF
4. WebSocket central distribui para todos os clientes conectados
```

### 3. Exibição de Imagem
```
1. Cada servidor de visualização recebe comando via WebSocket
2. Busca imagem do CPF no banco de dados
3. Exibe imagem imediatamente
4. Envia confirmação de exibição
```

## Vantagens da Nova Arquitetura

### ✅ **Tempo Real**
- Exibição instantânea das imagens
- Sem delays de agendamento
- Comunicação bidirecional

### ✅ **Confiabilidade**
- Conexões persistentes
- Heartbeats para detectar desconexões
- Reconexão automática

### ✅ **Simplicidade**
- Elimina complexidade de agendamento
- Não depende de scheduler
- Menos pontos de falha

### ✅ **Monitoramento**
- Status em tempo real dos servidores
- Logs detalhados de comunicação
- Fácil debug

## Configuração

### Variáveis de Ambiente

```yaml
# Servidor WebSocket
WEBSOCKET_SERVER_URL: ws://websocket-server:8765

# Servidores de Visualização
EXTERNAL_PORT: 8083  # Porta externa para identificação
```

### Portas

- **WebSocket Server**: 8765
- **Webhook Server**: 5002
- **Visualization 1**: 8083
- **Visualization 2**: 8084
- **Visualization 3**: 8085
- **Visualization 4**: 8086
- **Visualization 5**: 8087
- **Visualization 6**: 8088

## Testes

### Script de Teste Automático
```bash
python teste_websocket.py
```

### Teste Manual via Webhook
```bash
curl -X POST http://localhost:5002/webhook \
  -H 'Content-Type: application/json' \
  -d '{"cpf":"12345678901"}'
```

### Verificação de Visualizações
- http://localhost:8083/view/
- http://localhost:8084/view/
- http://localhost:8085/view/
- http://localhost:8086/view/
- http://localhost:8087/view/
- http://localhost:8088/view/

## Logs e Debug

### Servidor WebSocket
```bash
docker logs websocket-server
```

### Servidores de Visualização
```bash
docker logs visualization1
docker logs visualization2
# ... etc
```

### Webhook Server
```bash
docker logs app2-webhook
```

## Mensagens WebSocket

### Registro de Cliente
```json
{
  "type": "register",
  "visualization_name": "visualization1",
  "port": 8083
}
```

### Comando de Exibição
```json
{
  "type": "display_image",
  "cpf": "12345678901",
  "timestamp": "2024-01-15T10:30:00-03:00"
}
```

### Confirmação de Exibição
```json
{
  "type": "image_displayed",
  "visualization_name": "visualization1",
  "cpf": "12345678901",
  "timestamp": "2024-01-15T10:30:05-03:00"
}
```

### Heartbeat
```json
{
  "type": "heartbeat",
  "visualization_name": "visualization1",
  "timestamp": "2024-01-15T10:30:30-03:00"
}
```

## Migração do Sistema Anterior

### O que Mudou
- ❌ Removido: Sistema de agendamento baseado em banco
- ❌ Removido: Scheduler APScheduler
- ❌ Removido: Endpoints de agendamento complexos
- ✅ Adicionado: WebSocket para comunicação em tempo real
- ✅ Adicionado: Exibição imediata de imagens
- ✅ Adicionado: Monitoramento de conexões

### Compatibilidade
- ✅ Webhook endpoint mantido (`/webhook`)
- ✅ Endpoints de visualização mantidos
- ✅ Banco de dados mantido para imagens
- ✅ Configurações mantidas

## Troubleshooting

### Servidor WebSocket não conecta
1. Verifique se o container `websocket-server` está rodando
2. Verifique logs: `docker logs websocket-server`
3. Teste conexão: `python teste_websocket.py`

### Visualizações não exibem imagens
1. Verifique se estão conectadas ao WebSocket
2. Verifique logs de cada visualização
3. Teste webhook: `curl -X POST http://localhost:5002/webhook -d '{"cpf":"12345678901"}'`

### Imagens não aparecem
1. Verifique se o CPF existe no banco
2. Verifique se a imagem foi cadastrada
3. Teste endpoint: `http://localhost:8083/image/12345678901`

## Próximos Passos

1. **Monitoramento Avançado**
   - Dashboard de status em tempo real
   - Métricas de performance
   - Alertas de desconexão

2. **Recursos Adicionais**
   - Controle de volume por visualização
   - Configuração de layout
   - Integração com sistemas externos

3. **Otimizações**
   - Compressão de imagens
   - Cache de imagens frequentes
   - Load balancing 