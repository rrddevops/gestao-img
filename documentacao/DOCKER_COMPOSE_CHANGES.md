# Mudanças no Docker Compose - Sistema de Agendamento Baseado em DateTime

## Resumo das Alterações

O arquivo `docker-compose.yml` foi ajustado para ser totalmente compatível com a nova estrutura de agendamento baseado em datetime.

## 🔄 Mudanças Realizadas

### Antes (Sistema Legado)
```yaml
visualization1:
  environment:
    - DELAY=15  # ❌ Incorreto

visualization2:
  environment:
    - DELAY=25  # ❌ Incorreto

visualization3:
  environment:
    - DELAY=35  # ❌ Incorreto

visualization4:
  environment:
    - DELAY=45  # ❌ Incorreto

visualization5:
  environment:
    - DELAY=55  # ❌ Incorreto

visualization6:
  environment:
    - DELAY=65  # ❌ Incorreto
```

### Depois (Sistema Novo)
```yaml
visualization1:
  environment:
    - DELAY=0   # ✅ Primeira exibição

visualization2:
  environment:
    - DELAY=10  # ✅ +10 segundos

visualization3:
  environment:
    - DELAY=20  # ✅ +20 segundos

visualization4:
  environment:
    - DELAY=30  # ✅ +30 segundos

visualization5:
  environment:
    - DELAY=40  # ✅ +40 segundos

visualization6:
  environment:
    - DELAY=50  # ✅ +50 segundos
```

## 📊 Configuração Correta

### Mapeamento de Delays
| Visualização | Porta Externa | Delay (segundos) | Descrição |
|--------------|---------------|------------------|-----------|
| visualization1 | 8083 | 0 | Primeira exibição |
| visualization2 | 8084 | 10 | +10 segundos |
| visualization3 | 8085 | 20 | +20 segundos |
| visualization4 | 8086 | 30 | +30 segundos |
| visualization5 | 8087 | 40 | +40 segundos |
| visualization6 | 8088 | 50 | +50 segundos |

### Como Funciona

1. **Identificação da Visualização**: Cada container usa a variável `DELAY` para se identificar
2. **Mapeamento no Código**: O app3-visualizacao mapeia o `DELAY` para o nome da visualização
3. **Agendamento Preciso**: O sistema agenda exibições com delays exatos baseados em datetime

## 🔧 Compatibilidade

### Sistema Legado
- ✅ **Mantido** para compatibilidade
- ✅ **Conversão automática** de milissegundos para datetime
- ✅ **APIs antigas** continuam funcionando

### Sistema Novo
- ✅ **Agendamento baseado em horário**
- ✅ **Controle preciso** de tempo
- ✅ **Ordenação cronológica** automática

## 🧪 Verificação

### Script de Verificação
```bash
python verify_docker_compose.py
```

Este script verifica:
- ✅ Todos os serviços existem
- ✅ Delays configurados corretamente
- ✅ Portas mapeadas corretamente
- ✅ Variáveis de ambiente configuradas
- ✅ Rede e volumes configurados

### Teste Manual
```bash
# Iniciar sistema
docker-compose up -d --build

# Verificar containers
docker-compose ps

# Verificar logs
docker-compose logs visualization1
```

## 🚀 Como Usar

### Inicialização Rápida
```bash
python start_system.py
```

### Inicialização Manual
```bash
# Parar containers existentes
docker-compose down

# Construir e iniciar
docker-compose up -d --build

# Verificar status
docker-compose ps
```

### Testes
```bash
# Teste rápido
python test_scheduler.py

# Teste completo
python test_complete_system.py

# Verificar configuração
python verify_docker_compose.py
```

## 📋 URLs de Acesso

Após a inicialização, as visualizações estarão disponíveis em:

- **Visualization1**: http://localhost:8083/view/
- **Visualization2**: http://localhost:8084/view/
- **Visualization3**: http://localhost:8085/view/
- **Visualization4**: http://localhost:8086/view/
- **Visualization5**: http://localhost:8087/view/
- **Visualization6**: http://localhost:8088/view/

## 🔍 Troubleshooting

### Problemas Comuns

1. **Container não inicia**
   ```bash
   docker-compose logs visualization1
   ```

2. **Delay incorreto**
   ```bash
   python verify_docker_compose.py
   ```

3. **Porta já em uso**
   ```bash
   # Verificar portas em uso
   netstat -tulpn | grep 8083
   
   # Parar containers
   docker-compose down
   ```

4. **Banco não conecta**
   ```bash
   # Verificar logs do postgres
   docker-compose logs postgres
   
   # Verificar rede
   docker network ls
   ```

### Comandos Úteis

```bash
# Verificar status de todos os containers
docker-compose ps

# Ver logs de um serviço específico
docker-compose logs app3-visualizacao

# Reiniciar um serviço
docker-compose restart visualization1

# Parar todos os serviços
docker-compose down

# Remover volumes (cuidado!)
docker-compose down -v
```

## ✅ Checklist de Verificação

- [ ] Todos os 6 containers de visualização estão rodando
- [ ] Delays configurados corretamente (0, 10, 20, 30, 40, 50)
- [ ] Portas mapeadas corretamente (8083-8088)
- [ ] Banco PostgreSQL conectando
- [ ] Apps conectando ao banco
- [ ] Rede interna funcionando
- [ ] Scripts de teste executando sem erro

## 📖 Documentação Relacionada

- [README.md](README.md) - Visão geral do sistema
- [README_SCHEDULER.md](README_SCHEDULER.md) - Documentação do agendamento
- [CHANGELOG.md](CHANGELOG.md) - Mudanças do sistema
- [verify_docker_compose.py](verify_docker_compose.py) - Script de verificação

---

**Status**: ✅ Configurado e testado
**Versão**: 2.0.0
**Compatibilidade**: Total com sistema anterior 