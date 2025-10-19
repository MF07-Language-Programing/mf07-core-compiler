# CorpLang Advanced v2.7.0 - Instalador PowerShell
# Instalação automática da extensão VS Code CorpLang

Write-Host ""
Write-Host "  ╔══════════════════════════════════════════════════╗" -ForegroundColor Magenta
Write-Host "  ║                                                  ║" -ForegroundColor Magenta
Write-Host "  ║          🟣 CorpLang Advanced v2.7.0 🟣          ║" -ForegroundColor Magenta
Write-Host "  ║                                                  ║" -ForegroundColor Magenta  
Write-Host "  ║     Instalador Automático - VS Code Extension    ║" -ForegroundColor Magenta
Write-Host "  ║                                                  ║" -ForegroundColor Magenta
Write-Host "  ╚══════════════════════════════════════════════════╝" -ForegroundColor Magenta
Write-Host ""

Write-Host "🔍 Verificando pré-requisitos..." -ForegroundColor Cyan

# Verificar se VS Code está instalado
$codeCommand = Get-Command code -ErrorAction SilentlyContinue
if (-not $codeCommand) {
    Write-Host "❌ VS Code não encontrado no PATH!" -ForegroundColor Red
    Write-Host "💡 Instale VS Code e adicione ao PATH do sistema." -ForegroundColor Yellow
    Read-Host "Pressione Enter para sair"
    exit 1
}
Write-Host " VS Code encontrado" -ForegroundColor Green

# Verificar se arquivo .vsix existe
if (-not (Test-Path "corp-lang-2.7.0.vsix")) {
    Write-Host "❌ Arquivo corp-lang-2.7.0.vsix não encontrado!" -ForegroundColor Red
    Write-Host "💡 Execute este script no diretório da extensão." -ForegroundColor Yellow
    Read-Host "Pressione Enter para sair"
    exit 1
}
Write-Host " Arquivo corp-lang-2.7.0.vsix encontrado" -ForegroundColor Green

Write-Host ""
Write-Host "🚀 Iniciando instalação..." -ForegroundColor Cyan
Write-Host ""

# Tentar desinstalar versão anterior
Write-Host "🔄 Removendo versões anteriores..." -ForegroundColor Yellow
try {
    & code --uninstall-extension mf07.corp-lang 2>$null
} catch {
    # Ignorar erro se extensão não estiver instalada
}
Write-Host " Limpeza concluída" -ForegroundColor Green

# Instalar nova versão
Write-Host "📦 Instalando CorpLang Advanced v2.7.0..." -ForegroundColor Yellow
$result = & code --install-extension corp-lang-2.7.0.vsix

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "  ╔════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "  ║                                            ║" -ForegroundColor Green
    Write-Host "  ║      INSTALAÇÃO CONCLUÍDA COM SUCESSO!    ║" -ForegroundColor Green
    Write-Host "  ║                                            ║" -ForegroundColor Green
    Write-Host "  ║  🟣 CorpLang Advanced v2.7.0 Instalado     ║" -ForegroundColor Green
    Write-Host "  ║                                            ║" -ForegroundColor Green
    Write-Host "  ║  🎨 87+ Syntax Patterns                    ║" -ForegroundColor Green
    Write-Host "  ║  🌈 Tema Roxo/Azul Exclusivo               ║" -ForegroundColor Green
    Write-Host "  ║  💡 25+ Snippets Corporativos              ║" -ForegroundColor Green
    Write-Host "  ║  🔍 IntelliSense Completo                  ║" -ForegroundColor Green
    Write-Host "  ║  📁 Ícones de Arquivo .mp                  ║" -ForegroundColor Green
    Write-Host "  ║  📊 Logs Profissionais Otimizadas         ║" -ForegroundColor Green
    Write-Host "  ║                                            ║" -ForegroundColor Green
    Write-Host "  ║     REINICIE O VS CODE PARA ATIVAR!        ║" -ForegroundColor Green
    Write-Host "  ║                                            ║" -ForegroundColor Green
    Write-Host "  ╚════════════════════════════════════════════╝" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "❌ Erro durante a instalação!" -ForegroundColor Red
    Write-Host "💡 Verifique se VS Code está fechado e tente novamente." -ForegroundColor Yellow
}

Write-Host ""
Read-Host "Pressione Enter para sair"