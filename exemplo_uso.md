# Exemplo Prático de Uso

## 🎯 Cenário
Você tem um diretório com imagens nomeadas por CPF e quer cadastrar todas no sistema.

## 📁 Estrutura de Arquivos
```
C:\imagens_exemplo\
├── 11111111111.jpg
├── 22222222222.png
├── 33333333333.jpeg
├── 44444444444.gif
└── 55555555555.bmp
```

## 🚀 Passos para Cadastro

### 1. Verificar se o sistema está rodando
```cmd
docker-compose ps
```

### 2. Testar com simulação primeiro
```cmd
python cadastro_massa.py C:\imagens_exemplo --dry-run
```

**Saída esperada:**
```
🎯 Sistema de Cadastro em Massa de Imagens
==================================================
📁 Encontrados 5 arquivos de imagem
🌐 API URL: http://localhost:8000
🔍 Modo: Simulação
--------------------------------------------------
📄 Processando: 11111111111.jpg
   ✅ Simulação: CPF 11111111111 seria cadastrado
📄 Processando: 22222222222.png
   ✅ Simulação: CPF 22222222222 seria cadastrado
📄 Processando: 33333333333.jpeg
   ✅ Simulação: CPF 33333333333 seria cadastrado
📄 Processando: 44444444444.gif
   ✅ Simulação: CPF 44444444444 seria cadastrado
📄 Processando: 55555555555.bmp
   ✅ Simulação: CPF 55555555555 seria cadastrado
--------------------------------------------------
📊 Resumo:
   ✅ Sucessos: 5
   ❌ Erros: 0
   📁 Total processado: 5
```

### 3. Executar o cadastro real
```cmd
python cadastro_massa.py C:\imagens_exemplo
```

### 4. Verificar os resultados
Acesse `http://localhost/cadastro` para ver as imagens cadastradas.

## 🔧 Comandos Úteis

### Usando o script batch (Windows)
```cmd
# Simulação
cadastro_massa.bat C:\imagens_exemplo --dry-run

# Cadastro real
cadastro_massa.bat C:\imagens_exemplo
```

### Usando a interface web
1. Acesse `http://localhost/cadastro`
2. Role até "Cadastro em Massa"
3. Digite: `C:\imagens_exemplo`
4. Clique em "Cadastrar em Massa"

## ⚠️ Casos Especiais

### CPF já cadastrado
Se um CPF já estiver cadastrado, o sistema irá pular e continuar:
```
📄 Processando: 11111111111.jpg
   ❌ CPF já cadastrado ou inválido: CPF já cadastrado
```

### CPF inválido
Se o nome do arquivo não for um CPF válido:
```
📄 Processando: teste.jpg
   ❌ CPF inválido: teste
```

### Erro de rede
Se a API não estiver disponível:
```
⚠️  Aviso: Não foi possível conectar à API em http://localhost:8000
   Certifique-se de que o sistema está rodando com: docker-compose up
```

## 📊 Monitoramento

### Ver logs do sistema
```cmd
docker-compose logs backend --tail=50
```

### Verificar status da API
```cmd
curl http://localhost:8000/docs
```

### Listar cadastros via API
```cmd
curl http://localhost:8000/cadastro/list
```

## 🎉 Resultado Final

Após o cadastro bem-sucedido, você poderá:
- Ver as imagens na interface web: `http://localhost/cadastro`
- Usar as imagens no sistema de visualização
- Acessar as imagens via API: `http://localhost:8000/cadastro/{CPF}/imagem` 