# Atualização da Documentação - Formato Simplificado do Webhook

## Resumo das Mudanças

A documentação foi completamente atualizada para refletir o novo formato simplificado do webhook que aceita apenas CPF, com gerenciamento automático de horários pelo servidor.

## Arquivos Atualizados

### 1. README.md
**Principais mudanças:**
- ✅ Adicionada seção sobre "Sistema de Agendamento Simplificado"
- ✅ Destaque para interface simplificada - apenas CPF necessário
- ✅ Exemplos atualizados com formato simplificado
- ✅ Nova seção "Exemplos de Uso" com Python, JavaScript e cURL
- ✅ Reorganização das APIs disponíveis
- ✅ Atualização das vantagens do sistema

### 2. README_SCHEDULER.md
**Principais mudanças:**
- ✅ Nova seção "Interface Simplificada" no topo
- ✅ Exemplos de formato simplificado e manual
- ✅ Atualização das APIs disponíveis
- ✅ Novos exemplos de uso em Python
- ✅ Seção de monitoramento expandida
- ✅ Comandos de troubleshooting atualizados

### 3. CHANGELOG.md
**Principais mudanças:**
- ✅ Nova versão 2.1.0 documentada
- ✅ Seção completa sobre interface simplificada
- ✅ Exemplos de formato simplificado
- ✅ Vantagens da nova interface
- ✅ Compatibilidade documentada

### 4. EXAMPLES.md (NOVO)
**Conteúdo criado:**
- ✅ Exemplos práticos de uso
- ✅ Formato simplificado e avançado
- ✅ Scripts de teste
- ✅ Fluxo completo de uso
- ✅ Comandos de manutenção
- ✅ Tratamento de erros
- ✅ Testes de performance

## Novos Recursos Documentados

### Formato Simplificado (Recomendado)
```json
{
    "cpf": "12345678900"
}
```

### Resposta Detalhada
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

## Exemplos de Uso Documentados

### cURL
```bash
curl -X POST http://localhost:5002/schedule \
  -H "Content-Type: application/json" \
  -d '{"cpf": "12345678900"}'
```

### Python
```python
import requests

response = requests.post('http://localhost:5002/schedule', 
                        json={'cpf': '12345678900'})
print(response.json())
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

## Scripts de Teste Documentados

### test_webhook.py
- ✅ Teste rápido do formato simplificado
- ✅ Verificação de filas em todos os visualizadores
- ✅ Monitoramento de sincronização

### test_scheduler.py
- ✅ Teste completo do sistema
- ✅ Formato manual e simplificado
- ✅ Validação de funcionalidades

## Vantagens Documentadas

### 1. Simplicidade
- Menos parâmetros para enviar
- Menos erros de configuração
- Implementação mais rápida
- Menor curva de aprendizado

### 2. Automatização
- Horários gerenciados automaticamente
- Sincronização precisa garantida
- Menos configuração manual
- Menos pontos de falha

### 3. Flexibilidade
- Dois formatos disponíveis
- Escolha do usuário baseada na necessidade
- Migração gradual possível
- Compatibilidade total

## URLs de Acesso Documentadas

### Visualizações
- **Visualization1**: http://localhost:8083/view/
- **Visualization2**: http://localhost:8084/view/
- **Visualization3**: http://localhost:8085/view/
- **Visualization4**: http://localhost:8086/view/
- **Visualization5**: http://localhost:8087/view/
- **Visualization6**: http://localhost:8088/view/

### APIs
- **Upload**: http://localhost:5001/upload
- **Webhook**: http://localhost:5002/schedule
- **Status**: http://localhost:5002/schedule-status

## Comandos de Manutenção Documentados

### Limpeza
```bash
# Limpar agendamentos
docker-compose exec postgres psql -U postgres -d gestao_img -c "DELETE FROM schedule_entries;"

# Reiniciar visualizadores
docker-compose restart visualization1 visualization2 visualization3 visualization4 visualization5 visualization6
```

### Monitoramento
```bash
# Verificar filas
curl http://localhost:8083/queue-status

# Ver logs
docker-compose logs visualization1 | grep -i "88888888888\|error\|exibindo"
```

## Configuração dos Delays Documentada

| Visualização | Porta | Delay | Primeira Exibição |
|--------------|-------|-------|-------------------|
| visualization1 | 8083 | 0s | entry_time + wait_time |
| visualization2 | 8084 | 10s | +10s |
| visualization3 | 8085 | 20s | +20s |
| visualization4 | 8086 | 30s | +30s |
| visualization5 | 8087 | 40s | +40s |
| visualization6 | 8088 | 50s | +50s |

## Tratamento de Erros Documentado

### Erros Comuns
1. **CPF não encontrado** - Fazer upload da imagem primeiro
2. **Formato de horário inválido** - Usar formato correto ou simplificado
3. **Servidor não disponível** - Verificar se containers estão rodando

## Compatibilidade Documentada

### Formato Anterior Mantido
- Formato manual ainda suportado
- Controle de horários personalizado
- Transição gradual possível
- Sem quebra de funcionalidades

## Próximos Passos Documentados

### Melhorias Futuras
- Interface web para agendamento
- Dashboard de monitoramento
- Notificações em tempo real
- API REST completa
- Autenticação e autorização

---

## Status da Atualização

✅ **README.md** - Atualizado com formato simplificado
✅ **README_SCHEDULER.md** - Atualizado com interface simplificada
✅ **CHANGELOG.md** - Nova versão 2.1.0 documentada
✅ **EXAMPLES.md** - Criado com exemplos práticos
✅ **test_webhook.py** - Script de teste documentado

**Data da Atualização:** $(date)
**Versão da Documentação:** 2.1.0
**Status:** Completo ✅ 