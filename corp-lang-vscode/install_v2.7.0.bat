@echo off
cls
echo.
echo   ╔══════════════════════════════════════════════════╗
echo   ║                                                  ║
echo   ║          🟣 CorpLang Advanced v2.7.0 🟣          ║
echo   ║                                                  ║
echo   ║     Instalador Automático - VS Code Extension    ║
echo   ║                                                  ║
echo   ╚══════════════════════════════════════════════════╝
echo.

echo 🔍 Verificando pré-requisitos...

:: Verificar se VS Code está instalado
where code >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ VS Code não encontrado no PATH!
    echo 💡 Instale VS Code e adicione ao PATH do sistema.
    pause
    exit /b 1
)
echo  VS Code encontrado

:: Verificar se arquivo .vsix existe
if not exist "corp-lang-2.7.0.vsix" (
    echo ❌ Arquivo corp-lang-2.7.0.vsix não encontrado!
    echo 💡 Execute este script no diretório da extensão.
    pause
    exit /b 1
)
echo  Arquivo corp-lang-2.7.0.vsix encontrado

echo.
echo 🚀 Iniciando instalação...
echo.

:: Tentar desinstalar versão anterior (pode falhar se não estiver instalada)
echo 🔄 Removendo versões anteriores...
code --uninstall-extension mf07.corp-lang >nul 2>&1
echo  Limpeza concluída

:: Instalar nova versão
echo 📦 Instalando CorpLang Advanced v2.7.0...
code --install-extension corp-lang-2.7.0.vsix

if %errorlevel% equ 0 (
    echo.
    echo   ╔════════════════════════════════════════════╗
    echo   ║                                            ║
    echo   ║      INSTALAÇÃO CONCLUÍDA COM SUCESSO!    ║
    echo   ║                                            ║
    echo   ║  🟣 CorpLang Advanced v2.7.0 Instalado     ║
    echo   ║                                            ║
    echo   ║  🎨 87+ Syntax Patterns                    ║
    echo   ║  🌈 Tema Roxo/Azul Exclusivo               ║
    echo   ║  💡 25+ Snippets Corporativos              ║
    echo   ║  🔍 IntelliSense Completo                  ║
    echo   ║  📁 Ícones de Arquivo .mp                  ║
    echo   ║  📊 Logs Profissionais Otimizadas         ║
    echo   ║                                            ║
    echo   ║     REINICIE O VS CODE PARA ATIVAR!        ║
    echo   ║                                            ║
    echo   ╚════════════════════════════════════════════╝
) else (
    echo.
    echo ❌ Erro durante a instalação!
    echo 💡 Verifique se VS Code está fechado e tente novamente.
)

echo.
pause
