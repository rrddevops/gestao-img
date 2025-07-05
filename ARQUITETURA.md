# Arquitetura do Sistema WebSocket

## Visão Geral da Arquitetura

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              SISTEMA DE VISUALIZAÇÃO                            │
│                              COM WEBSOCKETS                                     │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    HTTP POST    ┌─────────────────┐    WebSocket    ┌─────────────────┐
│   Cliente       │ ──────────────► │   Webhook       │ ──────────────► │  Servidor       │
│   Externo       │                 │   (Porta 5002)  │                 │  WebSocket      │
│                 │                 │                 │                 │  (Porta 8765)   │
└─────────────────┘                 └─────────────────┘                 └─────────────────┘
                                            │                                   │
                                            │ HTTP GET                         │ WebSocket
                                            ▼                                   │ Broadcast
┌─────────────────┐                 ┌─────────────────┐                        │
│   Cadastro      │ ◄────────────── │   PostgreSQL    │                        │
│   (Porta 5001)  │                 │   (Porta 5432)  │                        │
└─────────────────┘                 └─────────────────┘                        │
                                                                                │
                                                                                │
                                                                                ▼
┌─────────────────┐    WebSocket    ┌─────────────────┐    WebSocket    ┌─────────────────┐
│ Visualization1  │ ◄────────────── │                 │ ◄────────────── │                 │
│ (Porta 8083)    │                 │                 │                 │                 │
└─────────────────┘                 │                 │                 │                 │
                                    │                 │                 │                 │
┌─────────────────┐    WebSocket    │                 │                 │                 │
│ Visualization2  │ ◄────────────── │                 │                 │                 │
│ (Porta 8084)    │                 │                 │                 │                 │
└─────────────────┘                 │                 │                 │                 │
                                    │                 │                 │                 │
┌─────────────────┐    WebSocket    │                 │                 │                 │
│ Visualization3  │ ◄────────────── │                 │                 │                 │
│ (Porta 8085)    │                 │                 │                 │                 │
└─────────────────┘                 │                 │                 │                 │
                                    │                 │                 │                 │
┌─────────────────┐    WebSocket    │                 │                 │                 │
│ Visualization4  │ ◄────────────── │                 │                 │                 │
│ (Porta 8086)    │                 │                 │                 │                 │
└─────────────────┘                 │                 │                 │                 │
                                    │                 │                 │                 │
┌─────────────────┐    WebSocket    │                 │                 │                 │
│ Visualization5  │ ◄────────────── │                 │                 │                 │
│ (Porta 8087)    │                 │                 │                 │                 │
└─────────────────┘                 │                 │                 │                 │
                                    │                 │                 │                 │
┌─────────────────┐    WebSocket    │                 │                 │                 │
│ Visualization6  │ ◄────────────── │                 │                 │                 │
│ (Porta 8088)    │                 │                 │                 │                 │
└─────────────────┘                 └─────────────────┘                 └─────────────────┘
```

## Fluxo de Comunicação

### 1. Inicialização do Sistema
```
1. PostgreSQL inicia (porta 5432)
2. Servidor WebSocket inicia (porta 8765)
3. Webhook Server inicia (porta 5002)
4. Cada Visualization se conecta ao WebSocket Server
5. Visualizations se registram com nome e porta
6. Conexões são mantidas ativas com heartbeats
```

### 2. Recebimento de Webhook
```
1. Cliente externo envia POST para /webhook
2. Webhook Server recebe CPF
3. Webhook Server conecta ao WebSocket Server
4. Envia comando 'display_image' com CPF
5. WebSocket Server distribui para todos os clientes
6. Cada Visualization recebe comando instantaneamente
```

### 3. Exibição de Imagem
```
1. Visualization recebe comando via WebSocket
2. Busca imagem do CPF no PostgreSQL
3. Exibe imagem imediatamente
4. Envia confirmação de exibição
5. Remove imagem após tempo configurado
```

## Componentes Detalhados

### Servidor WebSocket Central
```
┌─────────────────────────────────────────────────────────┐
│                Servidor WebSocket Central               │
│                     (Porta 8765)                        │
├─────────────────────────────────────────────────────────┤
│ • Gerencia conexões de clientes                         │
│ • Distribui comandos via broadcast                      │
│ • Monitora heartbeats (30s)                             │
│ • Reconexão automática                                  │
│ • Logs detalhados de comunicação                        │
└─────────────────────────────────────────────────────────┘
```

### Cliente WebSocket (Visualization)
```
┌─────────────────────────────────────────────────────────┐
│                Cliente WebSocket                        │
│              (Cada Visualization)                       │
├─────────────────────────────────────────────────────────┤
│ • Conecta ao servidor central                           │
│ • Registra-se com nome e porta                          │
│ • Envia heartbeats periódicos                           │
│ • Recebe comandos de exibição                           │
│ • Envia confirmações                                    │
│ • Reconexão automática em caso de falha                 │
└─────────────────────────────────────────────────────────┘
```

### Webhook Server
```
┌─────────────────────────────────────────────────────────┐
│                  Webhook Server                         │
│                     (Porta 5002)                        │
├─────────────────────────────────────────────────────────┤
│ • Recebe webhooks HTTP                                  │
│ • Conecta ao WebSocket Server                           │
│ • Envia comandos de exibição                            │
│ • Retorna status da operação                            │
│ • Compatibilidade com sistema anterior                  │
└─────────────────────────────────────────────────────────┘
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

## Vantagens da Arquitetura WebSocket

### ✅ **Tempo Real**
- Comunicação instantânea
- Sem delays de agendamento
- Exibição imediata das imagens

### ✅ **Confiabilidade**
- Conexões persistentes
- Heartbeats para detectar falhas
- Reconexão automática

### ✅ **Simplicidade**
- Elimina complexidade de agendamento
- Menos pontos de falha
- Comunicação direta

### ✅ **Monitoramento**
- Status em tempo real
- Logs detalhados
- Fácil debug

### ✅ **Escalabilidade**
- Fácil adicionar novos visualizadores
- Broadcast eficiente
- Arquitetura distribuída

## Portas e Endpoints

| Serviço | Porta | Endpoint | Descrição |
|---------|-------|----------|-----------|
| PostgreSQL | 5432 | - | Banco de dados |
| Cadastro | 5001 | POST /upload | Upload de imagens |
| Webhook | 5002 | POST /webhook | Recebe webhooks |
| WebSocket Server | 8765 | ws:// | Servidor WebSocket |
| Visualization1 | 8083 | GET /view/ | Interface visual |
| Visualization2 | 8084 | GET /view/ | Interface visual |
| Visualization3 | 8085 | GET /view/ | Interface visual |
| Visualization4 | 8086 | GET /view/ | Interface visual |
| Visualization5 | 8087 | GET /view/ | Interface visual |
| Visualization6 | 8088 | GET /view/ | Interface visual |

## Comparação: Sistema Anterior vs WebSocket

| Aspecto | Sistema Anterior | Sistema WebSocket |
|---------|------------------|-------------------|
| Comunicação | HTTP + Agendamento | WebSocket em tempo real |
| Delay | 10-60 segundos | Instantâneo |
| Sincronização | Baseada em horário | Broadcast simultâneo |
| Confiabilidade | Depende de scheduler | Conexões persistentes |
| Monitoramento | Logs limitados | Status em tempo real |
| Complexidade | Alta (agendamento) | Baixa (comunicação direta) |
| Pontos de falha | Múltiplos | Centralizado |
| Performance | Lenta | Rápida | 