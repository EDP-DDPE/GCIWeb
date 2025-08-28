@echo off
SETLOCAL

REM Caminho do certificado usando o USERPROFILE
set CERT_PATH=%USERPROFILE%\EDP\O365_Planejamento da Expansao - Documents\Servidores\Servidor SP\GCIWeb\instalar_certificado\root.crt

REM Usuário e senha do administrador local
set ADMIN_USER=.\admin
set ADMIN_PASS=@dm1nl0c@u

REM Comando para instalar certificado
set CMD=certutil -addstore -f "ROOT" "%CERT_PATH%"

echo ==========================================
echo Instalando certificado usando admin local...
echo ==========================================

REM Executa com PsExec usando credenciais
psexec64.exe -accepteula -u %ADMIN_USER% -p %ADMIN_PASS% -h cmd /c "%CMD%"

echo.
echo Instalacao finalizada.
pause
