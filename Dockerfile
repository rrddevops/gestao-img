FROM python:3.9-slim

WORKDIR /app

# Copiar os arquivos de requisitos primeiro para aproveitar o cache do Docker
COPY requirements.txt .

# Instalar as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o resto dos arquivos da aplicação
COPY . .

# Criar diretório de uploads
RUN mkdir -p uploads

# Expor a porta 5000
EXPOSE 5000

# Comando para executar a aplicação
CMD ["python", "app.py"] 