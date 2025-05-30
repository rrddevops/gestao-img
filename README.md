# Sistema de Gerenciamento de Imagens

Este sistema é composto por três aplicações que trabalham em conjunto para gerenciar o upload, processamento e visualização de imagens associadas a CPFs.

## Estrutura do Sistema

### App 1 - Cadastro de Imagens (Porta 5001)
- Responsável pelo upload e armazenamento de imagens
- Armazena as imagens no banco de dados SQLite
- Endpoint: POST /upload

### App 2 - Webhook (Porta 5002)
- Recebe notificações via webhook
- Encaminha solicitações para a aplicação de visualização
- Endpoint: POST /webhook

### App 3 - Visualização (Porta 5003)
- Gerencia a exibição temporizada das imagens
- Exibe as imagens por 30 segundos
- Endpoints:
  - POST /display
  - GET /view/<cpf>
  - GET /image/<cpf>

## Configuração e Execução

### Usando Docker Compose (Recomendado)

1. Construa e inicie todos os serviços:
```bash
docker-compose up -d --build
```

2. Para parar todos os serviços:
```bash
docker-compose down
```

### Usando Python local (Desenvolvimento)

1. Instale as dependências de cada aplicação:
```bash
cd app1-cadastro && pip install -r requirements.txt
cd ../app2-webhook && pip install -r requirements.txt
cd ../app3-visualizacao && pip install -r requirements.txt
```

2. Inicie cada aplicação em um terminal separado:
```bash
# Terminal 1
cd app1-cadastro && python app.py

# Terminal 2
cd app2-webhook && python app.py

# Terminal 3
cd app3-visualizacao && python app.py
```

## Como Usar

### 1. Cadastrar uma Imagem

```bash
curl -X POST -F "image=@caminho/para/imagem.jpg" -F "cpf=12345678900" http://localhost:5001/upload
```

### 2. Solicitar Visualização via Webhook

```bash
curl -X POST -H "Content-Type: application/json" -d '{"cpf":"12345678900"}' http://localhost:5002/webhook
```

### 3. Visualizar a Imagem

Após o webhook, acesse no navegador:
```
http://localhost:5003/view/12345678900
```

A imagem ficará disponível por exatamente 30 segundos, com um contador regressivo na página. Após esse tempo, a imagem não poderá mais ser visualizada até que um novo webhook seja recebido.

## Notas

- O banco de dados SQLite é compartilhado entre as aplicações 1 e 3 através do volume Docker
- As imagens são armazenadas diretamente no banco como dados binários
- O tempo de exibição é fixo em 30 segundos (30000 milissegundos)
- A aplicação de visualização mantém um registro em memória dos tempos de exibição
- As aplicações se comunicam através de uma rede Docker interna
- Os dados persistem mesmo após reiniciar os containers devido ao uso de volumes Docker 