# Correção: Aplicação dos Parâmetros da Tabela

## Problema Identificado

O sistema não estava aplicando corretamente os parâmetros da tabela `parametros`:

- **Parâmetros configurados**:
  - `tempo_inicial_segundos`: 30
  - `incremento_segundos`: 10
  - `duracao_exibicao_seg`: 10

- **Comportamento incorreto**: Todos os eventos estavam sendo criados com delays de apenas 2 segundos, ignorando completamente os parâmetros da tabela.

### Exemplo do Problema (ANTES):
```
105	12345678901	visualization3	12:57:28	00:00:04.932279	12:57:33	12:57:43
106	12345678901	visualization4	12:57:28	00:00:14.932279	12:57:43	12:57:53
107	12345678901	visualization5	12:57:28	00:00:24.932279	12:57:53	12:58:03
108	12345678901	visualization6	12:57:28	00:00:34.932279	12:58:03	12:58:13
109	22673617876	visualization1	12:59:00	00:00:02	12:59:02	12:59:12  ❌
110	22673617876	visualization2	12:59:00	00:00:02	12:59:02	12:59:12  ❌
111	22673617876	visualization3	12:59:00	00:00:02	12:59:02	12:59:12  ❌
```

## Causa do Problema

No arquivo `app/views/webhook.py`, a lógica estava usando delays fixos de 2 segundos em vez de aplicar os parâmetros da tabela:

```python
# CÓDIGO INCORRETO (ANTES)
if hora_inicio_base <= hora_atual:
    # Último evento já terminou, começar imediatamente
    hora_inicio_dt = hora_atual_brasilia + timedelta(seconds=2)  # ❌ Fixo
else:
    # Último evento ainda está ativo, começar após ele terminar
    hora_inicio_dt += timedelta(seconds=2)  # ❌ Fixo
```

## Solução Implementada

### Correção no Webhook (`app/views/webhook.py`)

**Problema**: Delays fixos de 2 segundos em vez de usar parâmetros da tabela.

**Solução**: Aplicar corretamente os parâmetros da tabela em todos os cenários:

```python
# CÓDIGO CORRETO (DEPOIS)
if ultimo_evento_visualization:
    # Se existe evento anterior nesta visualização, começar após o último terminar
    hora_inicio_base = ultimo_evento_visualization.hora_fim
    
    # Verificar se o último evento já terminou
    if hora_inicio_base <= hora_atual:
        # Último evento já terminou, começar imediatamente
        # Aplicar delay baseado nos parâmetros da tabela
        delay_inicial = tempo_inicial + (i * incremento)
        hora_inicio_dt = hora_atual_brasilia + timedelta(seconds=delay_inicial)
    else:
        # Último evento ainda está ativo, começar após ele terminar
        # Converter para datetime com timezone de Brasília
        data_atual = hora_atual_brasilia.date()
        hora_inicio_dt = TIMEZONE_BRASILIA.localize(
            datetime.combine(data_atual, hora_inicio_base)
        )
        # Aplicar delay baseado nos parâmetros da tabela
        delay_inicial = tempo_inicial + (i * incremento)
        hora_inicio_dt += timedelta(seconds=delay_inicial)
else:
    # Primeiro evento desta visualização
    # Calcular delay baseado no índice da visualização
    delay_inicial = tempo_inicial + (i * incremento)
    hora_inicio_dt = hora_atual_brasilia + timedelta(seconds=delay_inicial)
```

## Resultados dos Testes

### Teste de Aplicação dos Parâmetros

Após a correção, o sistema agora aplica corretamente os parâmetros:

```
=== VERIFICAÇÃO DOS PARÂMETROS ===
📋 Parâmetros esperados:
   - Tempo inicial: 30s
   - Incremento: 10s
   - Duração: 10s

✅ visualization1: 0:00:30 (esperado: 30s)
✅ visualization2: 0:00:40 (esperado: 40s)
✅ visualization3: 0:00:50 (esperado: 50s)
✅ visualization4: 0:01:00 (esperado: 60s)
✅ visualization5: 0:01:10 (esperado: 70s)
✅ visualization6: 0:01:20 (esperado: 80s)
```

### Exemplo de Sequência Correta (DEPOIS):

```
 1 22673617876 visualization1 13:05:50.483429 → 13:06:00.483429 (delay: 0:00:30)
 2 22673617876 visualization2 13:06:00.483429 → 13:06:10.483429 (delay: 0:00:40)
 3 22673617876 visualization3 13:06:10.483429 → 13:06:20.483429 (delay: 0:00:50)
 4 22673617876 visualization4 13:06:20.483429 → 13:06:30.483429 (delay: 0:01:00)
 5 22673617876 visualization5 13:06:30.483429 → 13:06:40.483429 (delay: 0:01:10)
 6 22673617876 visualization6 13:06:40.483429 → 13:06:50.483429 (delay: 0:01:20)
```

## Benefícios da Correção

1. **Configurabilidade**: Sistema agora respeita os parâmetros da tabela
2. **Flexibilidade**: Parâmetros podem ser alterados sem modificar código
3. **Consistência**: Todos os eventos seguem a mesma lógica de timing
4. **Previsibilidade**: Comportamento esperado baseado na configuração

## Como Testar

1. **Limpar eventos**: `curl -X DELETE "http://localhost:8000/webhook/eventos"`
2. **Enviar webhook**: `curl -X POST "http://localhost:8000/webhook/" -H "Content-Type: application/json" -d '{"cpf":"CPF_VALIDO"}'`
3. **Verificar delays**: `curl "http://localhost:8000/webhook/eventos"`

### Verificação Esperada:
- **visualization1**: delay de 30 segundos
- **visualization2**: delay de 40 segundos
- **visualization3**: delay de 50 segundos
- **visualization4**: delay de 60 segundos
- **visualization5**: delay de 70 segundos
- **visualization6**: delay de 80 segundos

## Status Atual

✅ **Problema Resolvido**: Parâmetros da tabela sendo aplicados corretamente
✅ **Testes Passando**: Delays calculados conforme configuração
✅ **Sistema Funcionando**: Sequência cronológica mantida
✅ **Configurabilidade**: Parâmetros podem ser alterados via tabela

O sistema agora aplica corretamente os parâmetros da tabela `parametros`, garantindo que os delays sejam calculados conforme a configuração (30s inicial + 10s de incremento por visualização). 