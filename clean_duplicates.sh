#!/bin/bash
set -e

echo "[INFO] Limpando registros duplicados do banco de dados..."

# Verifica se o PostgreSQL está rodando
if ! docker-compose ps postgres | grep -q "Up"; then
    echo "[ERROR] PostgreSQL não está rodando. Execute 'docker-compose up -d postgres' primeiro."
    exit 1
fi

# Copia o script SQL para o container
docker cp clean_duplicates.sql gestao-img-postgres-1:/tmp/clean_duplicates.sql

# Executa a limpeza
echo "[INFO] Executando limpeza..."
docker-compose exec -T postgres psql -U postgres -d gestao_img -f /tmp/clean_duplicates.sql

echo "[INFO] Limpeza concluída!"
echo "[INFO] Para verificar os resultados, acesse: http://localhost:8083/schedule-details" 