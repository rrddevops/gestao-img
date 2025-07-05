# 📁 Cadastro em Massa - Sistema de Gestão de Imagens

Este script permite cadastrar múltiplas imagens no sistema de forma automatizada, sem precisar fazer upload uma a uma.

## 📋 Pré-requisitos

1. **Sistema rodando**: Certifique-se de que o sistema está funcionando (`docker-compose up -d`)
2. **Imagens preparadas**: As imagens devem estar em uma pasta com o nome do CPF como nome do arquivo
3. **Python 3.6+** com biblioteca `requests`

## 📁 Preparação das Imagens

### Estrutura de Arquivos
```
pasta_imagens/
├── 22222222222.jpg
├── 33333333333.png
├── 44444444444.jpeg
└── 55555555555.gif
```

### Formatos Suportados
- `.jpg` / `.jpeg`
- `.png`
- `.gif`
- `.bmp`

### Nomenclatura
- **O nome do arquivo deve ser o CPF** (sem extensão)
- Exemplo: `12345678901.jpg` → CPF: `12345678901`

## 🚀 Como Usar

### Script Python Simples

```bash
python upload_simples.py
```

**Características:**
- Interface amigável com perguntas interativas
- Mostra progresso em tempo real
- Confirmação antes de executar
- Resumo final detalhado
- Cadastro + agendamento automático

## 📊 Funcionalidades

### ✅ Cadastro Automático
- Processa todas as imagens da pasta
- Extrai CPF do nome do arquivo
- Faz upload via API do sistema
- Trata erros individualmente

### 📅 Agendamento Automático
- Após cada cadastro, agenda a exibição
- Usa o webhook do sistema
- Delay de 1 segundo entre agendamentos
- Evita sobrecarga do sistema

### 📈 Relatório Detalhado
- Total de imagens processadas
- Sucessos e erros
- Progresso em tempo real
- Resumo final

## ⚙️ Configurações

### URLs do Sistema
O script está configurado para:
- **Cadastro**: `http://localhost:5001/upload`
- **Webhook**: `http://localhost:5002/webhook`

### Delays Padrão
- **Entre cadastros**: 1 segundo
- **Entre agendamentos**: 1 segundo

## 🔧 Personalização

### Alterar URLs
Edite as variáveis no script:
```python
response = requests.post("http://localhost:5001/upload", files=files, data=data)
webhook_response = requests.post("http://localhost:5002/webhook", json={'cpf': cpf})
```

### Alterar Delays
Edite a linha no script:
```python
time.sleep(1)  # Altere o número para mais ou menos segundos
```

## 🚨 Tratamento de Erros

### Erros Comuns
1. **Pasta não encontrada**: Verifique o caminho
2. **Sistema não respondendo**: Verifique se está rodando
3. **CPF já cadastrado**: O sistema sobrescreve automaticamente
4. **Formato de imagem inválido**: Use apenas formatos suportados

### Logs
- O script mostra progresso detalhado
- Erros são exibidos individualmente
- Processo continua mesmo com erros pontuais

## 📝 Exemplos de Uso

### Exemplo 1: Cadastro Simples
```bash
# 1. Prepare as imagens
mkdir imagens_teste
# Copie as imagens para a pasta

# 2. Execute o script
python upload_simples.py

# 3. Siga as instruções na tela
```

### Exemplo 2: Teste com Poucas Imagens
```bash
# Teste primeiro com 2-3 imagens
# Depois processe o lote completo
```

## 🎯 Dicas

1. **Teste com poucas imagens primeiro**
2. **Mantenha backup das imagens originais**
3. **Verifique se o sistema está funcionando antes**
4. **Use delays maiores se processar muitas imagens**

## 📞 Suporte

Se encontrar problemas:
1. Verifique se o sistema está rodando
2. Confirme o formato dos nomes dos arquivos
3. Teste com uma imagem por vez
4. Verifique os logs do sistema 