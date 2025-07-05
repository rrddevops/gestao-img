@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   Sistema de Cadastro em Massa
echo ========================================
echo.

if "%~1"=="" (
    echo Uso: cadastro_massa.bat [diretorio] [opcoes]
    echo.
    echo Exemplos:
    echo   cadastro_massa.bat C:\imagens
    echo   cadastro_massa.bat C:\imagens --dry-run
    echo   cadastro_massa.bat C:\imagens --api-url http://localhost:8000
    echo.
    echo Opções:
    echo   --dry-run     Simular cadastro sem realmente cadastrar
    echo   --api-url     URL da API (padrão: http://localhost:8000)
    echo.
    pause
    exit /b 1
)

echo Verificando se o Python está instalado...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado! Instale o Python primeiro.
    pause
    exit /b 1
)

echo Verificando se as dependências estão instaladas...
python -c "import requests" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Instalando dependências...
    pip install requests
)

echo.
echo 🚀 Iniciando cadastro em massa...
echo.

python cadastro_massa.py %*

echo.
echo ✅ Processo concluído!
pause 