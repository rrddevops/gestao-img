# 🚀 Guia Rápido - Cadastro em Massa

## ✅ Sistema Testado e Funcionando!

O sistema está 100% operacional. Você tem **3 opções** para cadastro em massa:

## 📋 Pré-requisitos

1. **Sistema rodando**: `docker-compose up -d`
2. **Python instalado**: ✅ Já está instalado
3. **Dependências**: ✅ Já estão instaladas

## 🎯 Como Usar

### Opção 1: Script Simples (Recomendado)
```cmd
python cadastro_simples.py "C:\caminho\para\imagens"
```

### Opção 2: Script Direto no Banco
```cmd
python cadastro_direto.py "C:\caminho\para\imagens"
```

### Opção 3: Testar Sistema
```cmd
python teste_cadastro.py
```

## 📁 Preparação das Imagens

**Estrutura obrigatória:**
```
C:\minhas_imagens\
├── 11111111111.jpg
├── 22222222222.png
├── 33333333333.jpeg
└── 44444444444.gif
```

**Regras:**
- ✅ Nome do arquivo = CPF (11 dígitos)
- ✅ Extensões: .jpg, .jpeg, .png, .gif, .bmp
- ❌ Não use espaços ou caracteres especiais

## 🔧 Exemplo Prático

1. **Crie um diretório de teste:**
   ```
   C:\imagens_teste\
   ├── 12345678901.jpg
   ├── 98765432109.png
   └── 11122233344.jpeg
   ```

2. **Execute o cadastro:**
   ```cmd
   python cadastro_simples.py "C:\imagens_teste"
   ```

3. **Resultado esperado:**
   ```
   🎯 Cadastro em Massa - Versão Simples
   ==================================================
   📁 Diretório: C:\imagens_teste
   🌐 API: http://localhost:8000

   📄 Encontrados 3 arquivos de imagem

   📄 Processando: 12345678901.jpg
      ✅ CPF 12345678901 cadastrado com sucesso
   📄 Processando: 98765432109.png
      ✅ CPF 98765432109 cadastrado com sucesso
   📄 Processando: 11122233344.jpeg
      ✅ CPF 11122233344 cadastrado com sucesso

   ==================================================
   📊 RESUMO FINAL
   ==================================================
   ✅ Sucessos: 3
   ❌ Erros: 0
   📁 Total: 3

   🎉 Cadastro concluído!
      Acesse: http://localhost/cadastro
   ```

## 🌐 Verificar Resultados

Após o cadastro, acesse:
- **Interface web**: http://localhost/cadastro
- **API docs**: http://localhost:8000/docs
- **Imagem específica**: http://localhost:8000/cadastro/{CPF}/imagem

## ⚠️ Solução de Problemas

### Erro: "Diretório não encontrado"
- Verifique se o caminho está correto
- Use aspas: `"C:\caminho com espaços"`

### Erro: "CPF inválido"
- Nome do arquivo deve ter exatamente 11 dígitos
- Exemplo: `12345678901.jpg` ✅

### Erro: "API não está disponível"
- Execute: `docker-compose up -d`
- Aguarde alguns segundos

### Erro: "CPF já cadastrado"
- Normal, o script pula e continua
- Não é um erro, é uma proteção

## 🎉 Pronto!

Agora você pode cadastrar centenas de imagens de uma vez!

**Dica**: Use o modo de teste primeiro para verificar se tudo está correto. 