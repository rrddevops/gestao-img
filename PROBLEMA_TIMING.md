# Problema de Timing no Sistema de Agendamento

## Problema Identificado

Durante os testes em massa do webhook, foi identificado que o sistema não estava respeitando os tempos de espera configurados. As imagens estavam sendo substituídas muito rapidamente, ignorando os parâmetros de timing.

### Análise do Problema

1. **Configuração Atual**:
   - `display_seconds`: 10 segundos (tempo que cada imagem fica visível)
   - `delay_seconds`: 30-80 segundos (tempo entre visualizações)
   - `wait_time`: 10 segundos (tempo entre agendamento e primeira exibição)

2. **Comportamento Problemático**:
   - O webhook estava usando `wait_time = 10 segundos` fixo
   - Quando múltiplos CPFs eram agendados rapidamente, todos apareciam quase simultaneamente
   - Os `delay_seconds` entre visualizações não eram respeitados

3. **Causa Raiz**:
   - O `wait_time` deveria ser baseado no `delay_seconds` da primeira visualização
   - O sistema estava ignorando a configuração de timing das visualizações

## Soluções Implementadas

### 1. Correção do Webhook

**Arquivo**: `app2-webhook/app.py`

**Antes**:
```python
wait_time = "00:00:10"  # 10 segundos de espera padrão
```

**Depois**:
```python
# Calcula wait_time baseado no delay da primeira visualização (visualization1)
first_delay_seconds = 30  # delay_seconds da visualization1
wait_time_seconds = first_delay_seconds
wait_time = f"00:00:{wait_time_seconds:02d}"
```

### 2. Correção do Docker Compose

**Arquivo**: `docker-compose.yml`

**Problema**: Incompatibilidade entre DELAY do docker-compose e delay_seconds do config
- Docker-compose: DELAY=0,10,20,30,40,50
- Config: delay_seconds=30,40,50,60,70,80

**Correção**: Alinhamento dos DELAY com o config
- visualization1: DELAY=30 (era 0)
- visualization2: DELAY=40 (era 10)
- visualization3: DELAY=50 (era 20)
- visualization4: DELAY=60 (era 30)
- visualization5: DELAY=70 (era 40)
- visualization6: DELAY=80 (era 50)

### 3. Novo Script de Teste com Timing

**Arquivo**: `test_webhook_timing.py`

- Respeita os tempos de exibição configurados
- Adiciona delay entre agendamentos para evitar sobreposição
- Calcula tempo total estimado do teste
- Mostra sequência de exibição nas visualizações

### 4. Configuração de Timing

**Arquivo**: `app3-visualizacao/visualization_config.json`

```json
{
  "visualizations": [
    {
      "name": "visualization1",
      "port": 8083,
      "delay_seconds": 30,
      "display_seconds": 10
    },
    {
      "name": "visualization2", 
      "port": 8084,
      "delay_seconds": 40,
      "display_seconds": 10
    }
    // ... outras visualizações
  ]
}
```

### 5. Correção do Cálculo de Timing

**Arquivo**: `app3-visualizacao/app.py`

**Problema**: O código estava adicionando o `delay_seconds` completo ao `first_display_datetime`, causando atraso duplo.

**Antes**:
```python
display_datetime = first_display_datetime + timedelta(seconds=config['delay_seconds'])
```

**Depois**:
```python
# O first_display_datetime já inclui o wait_time (30s), então só adiciona o delta
delta_seconds = config['delay_seconds'] - 30  # Remove o delay da primeira visualização
display_datetime = first_display_datetime + timedelta(seconds=delta_seconds)
```

## Como Funciona Agora

### Sequência de Exibição

1. **Agendamento**: CPF é agendado com `wait_time = 30s`
2. **Primeira exibição**: visualization1 mostra a imagem após 30s
3. **Sequência**: Cada visualização mostra a imagem com delay progressivo:
   - visualization1: 30s
   - visualization2: 40s  
   - visualization3: 50s
   - visualization4: 60s
   - visualization5: 70s
   - visualization6: 80s

### Teste Recomendado

Use o novo script `test_webhook_timing.py`:

```bash
python test_webhook_timing.py
```

**Opção 1**: Teste com timing correto (recomendado)
- Respeita os tempos de exibição
- Evita sobreposição de imagens
- Tempo total estimado: ~6 minutos para 24 CPFs

**Opção 2**: Teste rápido (para comparação)
- Sem delay entre agendamentos
- Mostra o comportamento problemático anterior

## Verificação

### 1. Banco de Dados

Verifique se os agendamentos estão corretos:

```sql
SELECT sequence_id, cpf, visualization_name, entry_time, wait_time, display_time 
FROM schedule_entries 
ORDER BY sequence_id DESC 
LIMIT 10;
```

### 2. Status dos Agendamentos

Acesse: `http://localhost:5002/schedule-status`

### 3. Visualizações

Acesse as telas de visualização:
- http://localhost:8083 (visualization1)
- http://localhost:8084 (visualization2)
- http://localhost:8085 (visualization3)
- etc.

## Resultado Esperado

- ✅ Imagens aparecem na sequência correta
- ✅ Tempos de exibição são respeitados
- ✅ Não há sobreposição entre CPFs diferentes
- ✅ Cada visualização mostra a imagem no momento correto

## Próximos Passos

1. Teste o novo script `test_webhook_timing.py`
2. Verifique se os tempos estão sendo respeitados
3. Ajuste os `delay_seconds` no `visualization_config.json` se necessário
4. Monitore o comportamento durante testes em massa 