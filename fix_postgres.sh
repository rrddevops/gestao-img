#!/bin/bash

echo "🔧 Resolvendo problema de compatibilidade do PostgreSQL"
echo "======================================================"

echo "📋 Opções disponíveis:"
echo "1. Limpar dados e usar PostgreSQL 15 (recomendado)"
echo "2. Manter dados e usar PostgreSQL 14"
echo "3. Sair"

read -p "Escolha uma opção (1-3): " choice

case $choice in
    1)
        echo "🗑️  Limpando dados existentes..."
        docker-compose down -v
        echo "✅ Dados limpos. Agora usando PostgreSQL 15..."
        
        # Alterar para PostgreSQL 15
        sed -i 's/image: postgres:14/image: postgres:15/' docker-compose.yml
        
        echo "🚀 Iniciando sistema com PostgreSQL 15..."
        docker-compose up -d --build
        ;;
    2)
        echo "🔄 Mantendo dados existentes com PostgreSQL 14..."
        docker-compose down
        
        # Garantir que está usando PostgreSQL 14
        sed -i 's/image: postgres:15/image: postgres:14/' docker-compose.yml
        
        echo "🚀 Iniciando sistema com PostgreSQL 14..."
        docker-compose up -d --build
        ;;
    3)
        echo "👋 Saindo..."
        exit 0
        ;;
    *)
        echo "❌ Opção inválida"
        exit 1
        ;;
esac

echo ""
echo "⏳ Aguardando inicialização..."
sleep 10

echo "📊 Verificando status..."
docker-compose ps

echo ""
echo "✅ Problema resolvido!"
echo "🌐 Acesse: http://localhost:8000" 