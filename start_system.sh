#!/bin/bash
set -e

echo "[INFO] Iniciando PostgreSQL..."
docker-compose up -d postgres

echo "[INFO] Aguardando PostgreSQL estar pronto..."
until docker-compose exec -T postgres pg_isready -U postgres; do
    echo "[INFO] PostgreSQL ainda não está pronto, aguardando..."
    sleep 5
done
echo "[INFO] PostgreSQL está pronto!"

echo "[INFO] Iniciando app1-cadastro..."
docker-compose up -d app1-cadastro

echo "[INFO] Aguardando app1-cadastro estar pronto..."
until curl -s http://localhost:5001/ > /dev/null 2>&1; do
    echo "[INFO] app1-cadastro ainda não está pronto, aguardando..."
    sleep 3
done
echo "[INFO] app1-cadastro está pronto!"

echo "[INFO] Iniciando app2-webhook..."
docker-compose up -d app2-webhook

echo "[INFO] Aguardando app2-webhook estar pronto..."
until curl -s http://localhost:5002/ > /dev/null 2>&1; do
    echo "[INFO] app2-webhook ainda não está pronto, aguardando..."
    sleep 3
done
echo "[INFO] app2-webhook está pronto!"

echo "[INFO] Iniciando servidores de visualização..."
docker-compose up -d visualization1 visualization2 visualization3 visualization4 visualization5 visualization6

echo "[INFO] Aguardando servidores de visualização estarem prontos..."
for port in 8083 8084 8085 8086 8087 8088; do
    echo "[INFO] Aguardando servidor na porta $port..."
    until curl -s http://localhost:$port/ > /dev/null 2>&1; do
        echo "[INFO] Servidor na porta $port ainda não está pronto, aguardando..."
        sleep 3
    done
    echo "[INFO] Servidor na porta $port está pronto!"
done

echo "[INFO] Todos os serviços estão prontos!"
echo "[INFO] Status dos containers:"
docker-compose ps

echo "[INFO] Sistema iniciado com sucesso!"
echo "[INFO] URLs disponíveis:"
echo "  - Cadastro: http://localhost:5001"
echo "  - Webhook: http://localhost:5002"
echo "  - Visualization1: http://localhost:8083"
echo "  - Visualization2: http://localhost:8084"
echo "  - Visualization3: http://localhost:8085"
echo "  - Visualization4: http://localhost:8086"
echo "  - Visualization5: http://localhost:8087"
echo "  - Visualization6: http://localhost:8088"
echo ""
echo "[INFO] Rotas disponíveis:"
echo "  - Detalhes dos agendamentos: http://localhost:8083/schedule-details"
echo "  - Status dos agendamentos: http://localhost:8083/schedule-status"
echo "  - Status da fila: http://localhost:8083/queue-status" 