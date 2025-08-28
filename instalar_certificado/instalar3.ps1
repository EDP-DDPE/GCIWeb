# Nome do certificado
$CertName   = "root.crt"
$CertDir    = "C:\Users\7034\EDP\O365_Planejamento da Expansao - Documents\Servidores\Servidor SP\GCIWeb\instalar_certificado"
$FullCertPath = Join-Path $CertDir $CertName

# Verifica se o certificado existe
if (-not (Test-Path $FullCertPath)) {
    Write-Host "ERRO: Certificado não encontrado em: $FullCertPath" -ForegroundColor Red
    Pause
    exit 1
}

# Função: verificar se está rodando como admin
function Test-Admin {
    $currentUser = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    return $currentUser.IsInRole([Security.Principal.WindowsBuiltinRole]::Administrator)
}

# Se não for admin → relança como admin
if (-not (Test-Admin)) {
    Write-Host "[INFO] Elevando permissões (UAC)..."
    Start-Process powershell "-ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

# Agora já estamos como administrador
Write-Host "Instalando certificado: $FullCertPath" -ForegroundColor Cyan

try {
    certutil -addstore Root "$FullCertPath"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Certificado instalado com sucesso!" -ForegroundColor Green
    } else {
        Write-Host "ERRO ao instalar certificado! Codigo: $LASTEXITCODE" -ForegroundColor Red
    }
} catch {
    Write-Host "Falha: $($_.Exception.Message)" -ForegroundColor Red
}

Pause
