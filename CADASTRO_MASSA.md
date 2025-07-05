# Sistema de Cadastro em Massa

Este sistema permite cadastrar múltiplas imagens de uma vez no sistema de gestão de imagens.

## 📋 Pré-requisitos

1. **Sistema rodando**: Certifique-se de que o sistema está rodando com `docker-compose up`
2. **Python**: Python 3.7+ instalado
3. **Dependências**: Biblioteca `requests` (será instalada automaticamente)

## 📁 Preparação das Imagens

As imagens devem estar organizadas da seguinte forma:

```
diretorio_imagens/
├── 11111111111.jpg
├── 22222222222.png
├── 33333333333.jpeg
└── 44444444444.gif
```

**Regras importantes:**
- O nome do arquivo deve ser exatamente o CPF (11 dígitos)
- Extensões suportadas: `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`
- Não use espaços ou caracteres especiais no nome do arquivo

## 🚀 Como Usar

### Opção 1: Script Python (Recomendado)

```bash
# Cadastro normal
python cadastro_massa.py C:\caminho\para\imagens

# Simular cadastro (sem realmente cadastrar)
python cadastro_massa.py C:\caminho\para\imagens --dry-run

# Usar API em outro endereço
python cadastro_massa.py C:\caminho\para\imagens --api-url http://192.168.1.100:8000
```

### Opção 2: Script Batch (Windows)

```cmd
# Cadastro normal
cadastro_massa.bat C:\caminho\para\imagens

# Simular cadastro
cadastro_massa.bat C:\caminho\para\imagens --dry-run

# Usar API em outro endereço
cadastro_massa.bat C:\caminho\para\imagens --api-url http://192.168.1.100:8000
```

### Opção 3: Interface Web

1. Acesse `http://localhost/cadastro`
2. Role até a seção "Cadastro em Massa"
3. Digite o caminho do diretório
4. Clique em "Cadastrar em Massa"

## 📊 Exemplo de Saída

```
🎯 Sistema de Cadastro em Massa de Imagens
==================================================
📁 Encontrados 5 arquivos de imagem
🌐 API URL: http://localhost:8000
🔍 Modo: Cadastro real
--------------------------------------------------
📄 Processando: 11111111111.jpg
   ✅ Cadastrado com sucesso
📄 Processando: 22222222222.png
   ✅ Cadastrado com sucesso
📄 Processando: 33333333333.jpeg
   ❌ CPF já cadastrado ou inválido: CPF já cadastrado
📄 Processando: 44444444444.gif
   ✅ Cadastrado com sucesso
📄 Processando: 55555555555.jpg
   ❌ CPF inválido: 55555555555
--------------------------------------------------
📊 Resumo:
   ✅ Sucessos: 3
   ❌ Erros: 2
   📁 Total processado: 5
```

## ⚠️ Tratamento de Erros

O sistema trata automaticamente os seguintes casos:

- **CPF já cadastrado**: Pula o arquivo e continua
- **CPF inválido**: Pula o arquivo e continua
- **Arquivo corrompido**: Pula o arquivo e continua
- **Erro de rede**: Para o processo e mostra o erro

## 🔧 Configuração Avançada

### Variáveis de Ambiente

```bash
# URL da API (padrão: http://localhost:8000)
export API_URL=http://192.168.1.100:8000

# Timeout da requisição (padrão: 30s)
export REQUEST_TIMEOUT=60
```

### Logs Detalhados

Para ver logs mais detalhados, execute:

```bash
python cadastro_massa.py --verbose C:\caminho\para\imagens
```

## 🆘 Solução de Problemas

### Erro: "API não está disponível"
- Verifique se o sistema está rodando: `docker-compose ps`
- Inicie o sistema: `docker-compose up -d`

### Erro: "CPF inválido"
- Verifique se o nome do arquivo tem exatamente 11 dígitos
- Não use espaços ou caracteres especiais

### Erro: "Arquivo não encontrado"
- Verifique se o caminho está correto
- Use caminhos absolutos: `C:\caminho\completo\para\imagens`

### Erro: "Permissão negada"
- Execute como administrador (Windows)
- Verifique as permissões do diretório

## 📞 Suporte

Para problemas ou dúvidas:
1. Verifique os logs do sistema: `docker-compose logs backend`
2. Teste a API: `http://localhost:8000/docs`
3. Use o modo `--dry-run` para simular primeiro 