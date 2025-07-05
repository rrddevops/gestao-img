@echo off
echo 🔧 Resolvendo problema de compatibilidade do PostgreSQL
echo ======================================================

echo 📋 Opções disponíveis:
echo 1. Limpar dados e usar PostgreSQL 15 (recomendado)
echo 2. Manter dados e usar PostgreSQL 14
echo 3. Sair

set /p choice="Escolha uma opção (1-3): "

if "%choice%"=="1" (
    echo 🗑️  Limpando dados existentes...
    docker-compose down -v
    echo ✅ Dados limpos. Agora usando PostgreSQL 15...
    
    REM Alterar para PostgreSQL 15
    powershell -Command "(Get-Content docker-compose.yml) -replace 'image: postgres:14', 'image: postgres:15' | Set-Content docker-compose.yml"
    
    echo 🚀 Iniciando sistema com PostgreSQL 15...
    docker-compose up -d --build
) else if "%choice%"=="2" (
    echo 🔄 Mantendo dados existentes com PostgreSQL 14...
    docker-compose down
    
    REM Garantir que está usando PostgreSQL 14
    powershell -Command "(Get-Content docker-compose.yml) -replace 'image: postgres:15', 'image: postgres:14' | Set-Content docker-compose.yml"
    
    echo 🚀 Iniciando sistema com PostgreSQL 14...
    docker-compose up -d --build
) else if "%choice%"=="3" (
    echo 👋 Saindo...
    exit /b 0
) else (
    echo ❌ Opção inválida
    exit /b 1
)

echo.
echo ⏳ Aguardando inicialização...
timeout /t 10 /nobreak >nul

echo 📊 Verificando status...
docker-compose ps

echo.
echo ✅ Problema resolvido!
echo 🌐 Acesse: http://localhost:8000
pause 