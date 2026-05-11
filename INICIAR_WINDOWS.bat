@echo off
echo ================================================
echo   Editor de Contrato - Saude GI
echo ================================================
echo.

:: Tenta python, depois python3
python --version >nul 2>&1
IF %ERRORLEVEL% EQU 0 (
    echo Python encontrado! Iniciando...
    echo Acesse: http://localhost:8080
    echo Para encerrar: feche esta janela
    echo.
    python servidor.py
    goto fim
)

python3 --version >nul 2>&1
IF %ERRORLEVEL% EQU 0 (
    echo Python3 encontrado! Iniciando...
    echo Acesse: http://localhost:8080
    echo Para encerrar: feche esta janela
    echo.
    python3 servidor.py
    goto fim
)

:: Python nao encontrado
echo ================================================
echo   ERRO: Python nao encontrado!
echo ================================================
echo.
echo Para usar este app voce precisa instalar o Python.
echo.
echo 1. Acesse: https://www.python.org/downloads/
echo 2. Clique em "Download Python" (versao mais recente)
echo 3. Na instalacao, MARQUE a opcao "Add Python to PATH"
echo 4. Conclua a instalacao
echo 5. Reinicie o computador
echo 6. Clique novamente neste arquivo
echo.
:fim
pause
