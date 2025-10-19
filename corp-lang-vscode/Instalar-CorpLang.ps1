# 🚀 INSTALADOR CORPLANG EXTENSION v2.3.0
# Instalador inteligente com verificações automáticas

param(
    [switch]$Force,
    [switch]$Quiet
)

function Write-ColorText {
    param([string]$Text, [string]$Color = "White")
    Write-Host $Text -ForegroundColor $Color
}

function Show-Header {
    Clear-Host
    Write-ColorText "============================================" "Cyan"
    Write-ColorText "  🚀 INSTALADOR CORPLANG EXTENSION v2.3.0" "Yellow"
    Write-ColorText "============================================" "Cyan"
    Write-Host ""
}

function Test-VSCode {
    try {
        $null = Get-Command "code" -ErrorAction Stop
        return $true
    }
    catch {
        return $false
    }
}

function Get-InstalledExtensions {
    try {
        $output = & code --list-extensions 2>$null
        return $output
    }
    catch {
        return @()
    }
}

function Uninstall-OldVersions {
    Write-ColorText "🧹 Removendo versões antigas..." "Yellow"
    
    $oldExtensions = @(
        "your-name.corp-lang",
        "mf07.corp-lang"
    )
    
    $installed = Get-InstalledExtensions
    
    foreach ($ext in $oldExtensions) {
        if ($installed -contains $ext) {
            Write-ColorText "  Removendo: $ext" "Gray"
            & code --uninstall-extension $ext | Out-Null
        }
    }
    
    Write-ColorText " Limpeza concluída!" "Green"
}

function Install-CorpLangExtension {
    Write-ColorText "📦 Instalando CorpLang Advanced v2.3.0..." "Yellow"
    
    $vsixFile = "corp-lang-2.3.0.vsix"
    
    if (!(Test-Path $vsixFile)) {
        Write-ColorText "❌ ERRO: Arquivo $vsixFile não encontrado" "Red"
        Write-ColorText "   Execute este script na pasta da extensão" "Red"
        return $false
    }
    
    try {
        & code --install-extension $vsixFile
        if ($LASTEXITCODE -eq 0) {
            Write-ColorText " Extensão instalada com sucesso!" "Green"
            return $true
        }
        else {
            Write-ColorText "❌ Erro na instalação (Código: $LASTEXITCODE)" "Red"
            return $false
        }
    }
    catch {
        Write-ColorText "❌ Erro na instalação: $($_.Exception.Message)" "Red"
        return $false
    }
}

function Show-CompletionMessage {
    Write-Host ""
    Write-ColorText "============================================" "Green"
    Write-ColorText "        🎉 INSTALAÇÃO CONCLUÍDA!" "Green"  
    Write-ColorText "============================================" "Green"
    Write-Host ""
    
    Write-ColorText " CorpLang Advanced v2.3.0 instalada" "Green"
    Write-ColorText " Syntax highlighting roxo/azul configurado" "Green"
    Write-ColorText " 25+ snippets corporativos disponíveis" "Green"
    Write-ColorText " Tema exclusivo CorpLang incluído" "Green"
    Write-Host ""
    
    Write-ColorText "PROXIMOS PASSOS:" "Cyan"
    Write-ColorText "1. Abra um arquivo .mp no VS Code" "White"
    Write-ColorText "2. Pressione Ctrl+Shift+P" "White"  
    Write-ColorText "3. Digite 'Color Theme'" "White"
    Write-ColorText "4. Selecione 'CorpLang Dark Theme'" "White"
    Write-Host ""
    
    Write-ColorText "TESTE OS SNIPPETS:" "Cyan"
    Write-ColorText "- fn + Tab      -> Funcao basica" "Gray"
    Write-ColorText "- asyncfn + Tab -> Funcao async" "Gray"
    Write-ColorText "- class + Tab   -> Classe completa" "Gray"
    Write-ColorText "- list + Tab    -> Lista tipada" "Gray"
    Write-ColorText "- map + Tab     -> Mapa tipado" "Gray"
    Write-Host ""
}

function Show-ErrorMessage {
    param([string]$Message)
    
    Write-Host ""
    Write-ColorText "============================================" "Red"
    Write-ColorText "              ❌ ERRO" "Red"
    Write-ColorText "============================================" "Red"
    Write-ColorText $Message "Red"
    Write-Host ""
}

# INÍCIO DO SCRIPT PRINCIPAL
Show-Header

# Verificar VS Code
if (!(Test-VSCode)) {
    Show-ErrorMessage "VS Code não encontrado no PATH`nInstale o VS Code primeiro: https://code.visualstudio.com/"
    if (!$Quiet) { pause }
    exit 1
}

Write-ColorText " VS Code encontrado!" "Green"
Write-Host ""

# Confirmar instalação
if (!$Force -and !$Quiet) {
    $confirm = Read-Host "Deseja continuar com a instalação? (s/N)"
    if ($confirm -notmatch "^[sS]") {
        Write-ColorText "Instalação cancelada pelo usuário." "Yellow"
        exit 0
    }
}

# Remover versões antigas
Uninstall-OldVersions
Write-Host ""

# Instalar nova versão  
$success = Install-CorpLangExtension

if ($success) {
    Show-CompletionMessage
    
    # Oferecer para abrir arquivo de teste
    if (!$Quiet) {
        Write-Host ""
        $openTest = Read-Host "Deseja abrir o arquivo de teste agora? (s/N)"
        if ($openTest -match "^[sS]") {
            if (Test-Path "TESTE_CORES_v2.2.0.mp") {
                & code "TESTE_CORES_v2.2.0.mp"
            }
        }
    }
}
else {
    Show-ErrorMessage "Falha na instalação da extensão"
    if (!$Quiet) { pause }
    exit 1
}

if (!$Quiet) { 
    Write-Host ""
    Write-ColorText "Pressione qualquer tecla para sair..." "Gray"
    pause 
}