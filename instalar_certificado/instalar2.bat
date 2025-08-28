@echo off
set ADMIN_USER=.\admin
set ADMIN_PASS=@dm1nl0c@u
set CERT_NAME=root.crt
set "CERT_DIR=C:\cert"
set "FULL_CERT_PATH=%CERT_DIR%\%CERT_NAME%"

if not exist "%FULL_CERT_PATH%" (
    echo ERRO: Certificado nao encontrado em: %FULL_CERT_PATH%
    pause
    exit /b 1
)

echo Instalando certificado: %CERT_NAME%
PsExec64.exe -accepteula -u %ADMIN_USER% -p %ADMIN_PASS% certutil -addstore Root "\"%FULL_CERT_PATH%\""

if %errorlevel%==0 (
    echo Certificado instalado com sucesso!
) else (
    echo Erro ao instalar certificado! Codigo: %errorlevel%
)

pause
