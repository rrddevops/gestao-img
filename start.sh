#!/bin/bash

echo "🚀 Iniciando Sistema de Gerenciamento de Imagens"
echo "================================================"

# Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não está instalado. Por favor, instale o Docker primeiro."
    exit 1
fi

# Verificar se Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose não está instalado. Por favor, instale o Docker Compose primeiro."
    exit 1
fi

echo "✅ Docker e Docker Compose encontrados"

# Parar containers existentes
echo "🛑 Parando containers existentes..."
docker-compose down

# Construir e iniciar containers
echo "🔨 Construindo e iniciando containers..."
docker-compose up -d --build

# Aguardar inicialização
echo "⏳ Aguardando inicialização dos serviços..."
sleep 10

# Verificar status dos containers
echo "📊 Verificando status dos containers..."
docker-compose ps

# Verificar se o backend está respondendo
echo "🔍 Verificando se o backend está respondendo..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend está respondendo!"
        break
    fi
    echo "⏳ Aguardando backend... ($i/30)"
    sleep 2
done

# Verificar se o banco está funcionando
echo "🔍 Verificando conexão com banco de dados..."
if docker-compose exec -T db pg_isready -U postgres -d gestao_img > /dev/null 2>&1; then
    echo "✅ Banco de dados está funcionando!"
else
    echo "⚠️  Banco de dados pode não estar totalmente inicializado ainda"
fi

echo ""
echo "🎉 Sistema iniciado com sucesso!"
echo ""
echo "📋 URLs do sistema:"
echo "   🌐 Página inicial: http://localhost:8000"
echo "   📝 Cadastro: http://localhost:8000/cadastro"
echo "   📚 API Docs: http://localhost:8000/docs"
echo ""
echo "📺 Visualizações:"
echo "   🖥️  Visualization 1: http://localhost:8000/visualization1"
echo "   🖥️  Visualization 2: http://localhost:8000/visualization2"
echo "   🖥️  Visualization 3: http://localhost:8000/visualization3"
echo "   🖥️  Visualization 4: http://localhost:8000/visualization4"
echo "   🖥️  Visualization 5: http://localhost:8000/visualization5"
echo "   🖥️  Visualization 6: http://localhost:8000/visualization6"
echo ""
echo "🧪 Para testar o sistema:"
echo "   python test_system.py"
echo ""
echo "📊 Para ver logs:"
echo "   docker-compose logs -f backend"
echo ""
echo "🛑 Para parar o sistema:"
echo "   docker-compose down" 