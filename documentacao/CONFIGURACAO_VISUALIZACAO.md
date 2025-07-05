# Configuração de Visualizações - Sistema de Gestão de Imagens

## Visão Geral

O sistema permite configurar de forma flexível:
- **Delay de exibição**: Quanto tempo após o agendamento a imagem aparece em cada visualização
- **Tempo de exibição**: Por quanto tempo a imagem fica visível em cada visualização

## Arquivo de Configuração

### Localização
```
app3-visualizacao/visualization_config.json
```

### Estrutura
```json
{
  "visualizations": [
    {
      "name": "visualization1",
      "port": 8083,
      "delay_seconds": 0,
      "display_seconds": 10
    },
    {
      "name": "visualization2",
      "port": 8084,
      "delay_seconds": 10,
      "display_seconds": 10
    }
  ]
}
```

### Parâmetros

| Parâmetro | Descrição | Exemplo |
|-----------|-----------|---------|
| `name` | Nome da visualização (NÃO ALTERAR) | `"visualization1"` |
| `port` | Porta externa (NÃO ALTERAR) | `8083` |
| `delay_seconds` | Segundos após agendamento para exibir | `0` (imediato) |
| `display_seconds` | Segundos que a imagem fica visível | `10` (10 segundos) |

## Exemplos de Configuração

### 1. Configuração Padrão (Atual)
```json
{
  "visualizations": [
    {"name": "visualization1", "port": 8083, "delay_seconds": 0, "display_seconds": 10},
    {"name": "visualization2", "port": 8084, "delay_seconds": 10, "display_seconds": 10},
    {"name": "visualization3", "port": 8085, "delay_seconds": 20, "display_seconds": 10},
    {"name": "visualization4", "port": 8086, "delay_seconds": 30, "display_seconds": 10},
    {"name": "visualization5", "port": 8087, "delay_seconds": 40, "display_seconds": 10},
    {"name": "visualization6", "port": 8088, "delay_seconds": 50, "display_seconds": 10}
  ]
}
```

### 2. Configuração Personalizada
```json
{
  "visualizations": [
    {"name": "visualization1", "port": 8083, "delay_seconds": 0, "display_seconds": 15},
    {"name": "visualization2", "port": 8084, "delay_seconds": 5, "display_seconds": 20},
    {"name": "visualization3", "port": 8085, "delay_seconds": 12, "display_seconds": 10},
    {"name": "visualization4", "port": 8086, "delay_seconds": 20, "display_seconds": 8},
    {"name": "visualization5", "port": 8087, "delay_seconds": 30, "display_seconds": 12},
    {"name": "visualization6", "port": 8088, "delay_seconds": 45, "display_seconds": 10}
  ]
}
```

### 3. Configuração com Exibição Contínua
```json
{
  "visualizations": [
    {"name": "visualization1", "port": 8083, "delay_seconds": 0, "display_seconds": 0},
    {"name": "visualization2", "port": 8084, "delay_seconds": 10, "display_seconds": 0},
    {"name": "visualization3", "port": 8085, "delay_seconds": 20, "display_seconds": 0},
    {"name": "visualization4", "port": 8086, "delay_seconds": 30, "display_seconds": 0},
    {"name": "visualization5", "port": 8087, "delay_seconds": 40, "display_seconds": 0},
    {"name": "visualization6", "port": 8088, "delay_seconds": 50, "display_seconds": 0}
  ]
}
```

**Nota**: `display_seconds: 0` = imagem fica até ser substituída (comportamento original)

## Como Aplicar Mudanças

### 1. Editar o Arquivo
```bash
# Edite o arquivo de configuração
nano app3-visualizacao/visualization_config.json
```

### 2. Reiniciar o Sistema
```bash
# Parar containers
docker-compose down

# Reconstruir e iniciar
docker-compose up --build -d
```

### 3. Verificar Logs
```bash
# Verificar se a configuração foi carregada
docker-compose logs visualization1
```

## Casos de Uso

### Cenário 1: Exibição Sequencial Rápida
```json
{
  "visualizations": [
    {"name": "visualization1", "port": 8083, "delay_seconds": 0, "display_seconds": 5},
    {"name": "visualization2", "port": 8084, "delay_seconds": 2, "display_seconds": 5},
    {"name": "visualization3", "port": 8085, "delay_seconds": 4, "display_seconds": 5},
    {"name": "visualization4", "port": 8086, "delay_seconds": 6, "display_seconds": 5},
    {"name": "visualization5", "port": 8087, "delay_seconds": 8, "display_seconds": 5},
    {"name": "visualization6", "port": 8088, "delay_seconds": 10, "display_seconds": 5}
  ]
}
```

### Cenário 2: Exibição Prolongada
```json
{
  "visualizations": [
    {"name": "visualization1", "port": 8083, "delay_seconds": 0, "display_seconds": 30},
    {"name": "visualization2", "port": 8084, "delay_seconds": 15, "display_seconds": 30},
    {"name": "visualization3", "port": 8085, "delay_seconds": 30, "display_seconds": 30},
    {"name": "visualization4", "port": 8086, "delay_seconds": 45, "display_seconds": 30},
    {"name": "visualization5", "port": 8087, "delay_seconds": 60, "display_seconds": 30},
    {"name": "visualization6", "port": 8088, "delay_seconds": 75, "display_seconds": 30}
  ]
}
```

### Cenário 3: Exibição Simultânea
```json
{
  "visualizations": [
    {"name": "visualization1", "port": 8083, "delay_seconds": 0, "display_seconds": 20},
    {"name": "visualization2", "port": 8084, "delay_seconds": 0, "display_seconds": 20},
    {"name": "visualization3", "port": 8085, "delay_seconds": 0, "display_seconds": 20},
    {"name": "visualization4", "port": 8086, "delay_seconds": 0, "display_seconds": 20},
    {"name": "visualization5", "port": 8087, "delay_seconds": 0, "display_seconds": 20},
    {"name": "visualization6", "port": 8088, "delay_seconds": 0, "display_seconds": 20}
  ]
}
```

## Validação

### 1. Verificar Configuração Carregada
```bash
docker-compose logs visualization1 | grep "Configuração carregada"
```

### 2. Testar Agendamento
```bash
# Fazer um agendamento de teste
curl -X POST http://localhost:5002/schedule \
  -H "Content-Type: application/json" \
  -d '{"cpf": "12345678901"}'
```

### 3. Verificar Logs de Agendamento
```bash
docker-compose logs visualization1 | grep "Agendado:"
```

## Troubleshooting

### Problema: Arquivo não encontrado
**Sintoma**: Log mostra "Arquivo visualization_config.json não encontrado"
**Solução**: Verificar se o arquivo existe em `app3-visualizacao/visualization_config.json`

### Problema: JSON inválido
**Sintoma**: Erro ao carregar configuração
**Solução**: Validar JSON em https://jsonlint.com/

### Problema: Configuração não aplicada
**Sintoma**: Delays continuam os mesmos
**Solução**: Reiniciar containers com `docker-compose down && docker-compose up --build -d`

## Compatibilidade

- ✅ Mantém toda estrutura atual do banco de dados
- ✅ Mantém APScheduler e filas
- ✅ Mantém todas as APIs existentes
- ✅ Mantém queue-status e schedule-status
- ✅ Funciona com configuração padrão se arquivo não existir

## Notas Importantes

1. **NÃO altere** os campos `name` e `port` - são usados pelo sistema
2. **Reinicie sempre** após alterar a configuração
3. **Valide o JSON** antes de aplicar
4. **Monitore os logs** para verificar se a configuração foi carregada
5. **Teste** com um agendamento simples antes de usar em produção 