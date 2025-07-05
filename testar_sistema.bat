@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   Teste do Sistema de Cadastro
echo ========================================
echo.

echo Executando teste do sistema...
python teste_cadastro.py

echo.
echo ========================================
echo   Scripts Disponíveis
echo ========================================
echo.
echo 1. cadastro_simples.py - Via API
echo    python cadastro_simples.py "C:\caminho\para\imagens"
echo.
echo 2. cadastro_direto.py - Direto no banco
echo    python cadastro_direto.py "C:\caminho\para\imagens"
echo.
echo 3. teste_cadastro.py - Testar sistema
echo    python teste_cadastro.py
echo.
pause 