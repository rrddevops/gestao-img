@echo off
echo 🚀 Iniciando Sistema de Gerenciamento de Imagens
echo ================================================

REM Verificar se Docker está instalado
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker não está instalado. Por favor, instale o Docker primeiro.
    pause
    exit /b 1
)

REM Verificar se Docker Compose está instalado
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose não está instalado. Por favor, instale o Docker Compose primeiro.
    pause
    exit /b 1
)

echo ✅ Docker e Docker Compose encontrados

REM Parar containers existentes
echo 🛑 Parando containers existentes...
docker-compose down

REM Construir e iniciar containers
echo 🔨 Construindo e iniciando containers...
docker-compose up -d --build

REM Aguardar inicialização
echo ⏳ Aguardando inicialização dos serviços...
timeout /t 10 /nobreak >nul

REM Verificar status dos containers
echo 📊 Verificando status dos containers...
docker-compose ps

REM Verificar se o backend está respondendo
echo 🔍 Verificando se o backend está respondendo...
for /l %%i in (1,1,30) do (
    curl -s http://localhost:8000/health >nul 2>&1
    if not errorlevel 1 (
        echo ✅ Backend está respondendo!
        goto :backend_ok
    )
    echo ⏳ Aguardando backend... (%%i/30)
    timeout /t 2 /nobreak >nul
)

:backend_ok
echo.
echo 🎉 Sistema iniciado com sucesso!
echo.
echo 📋 URLs do sistema:
echo    🌐 Página inicial: http://localhost:8000
echo    📝 Cadastro: http://localhost:8000/cadastro
echo    📚 API Docs: http://localhost:8000/docs
echo.
echo 📺 Visualizações:
echo    🖥️  Visualization 1: http://localhost:8000/visualization1
echo    🖥️  Visualization 2: http://localhost:8000/visualization2
echo    🖥️  Visualization 3: http://localhost:8000/visualization3
echo    🖥️  Visualization 4: http://localhost:8000/visualization4
echo    🖥️  Visualization 5: http://localhost:8000/visualization5
echo    🖥️  Visualization 6: http://localhost:8000/visualization6
echo.
echo 🧪 Para testar o sistema:
echo    python test_system.py
echo.
echo 📊 Para ver logs:
echo    docker-compose logs -f backend
echo.
echo 🛑 Para parar o sistema:
echo    docker-compose down
echo.
pause 