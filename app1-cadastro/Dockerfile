FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Executa a migração e depois inicia a aplicação
CMD python migrate.py && python app.py

EXPOSE 5001 