@echo off
cls
echo.
echo   ╔═════════════════════════════════════════════════════════╗
echo   ║                                                         ║
echo   ║     🟣 CorpLang Advanced v2.7.0 - ATUALIZAÇÃO 🟣        ║
echo   ║                                                         ║
echo   ║          Logs Profissionais + Extensão VS Code          ║
echo   ║                                                         ║
echo   ╚═════════════════════════════════════════════════════════╝
echo.

echo 🚀 Processo de Atualização Completa:
echo.

echo ▶️ PASSO 1: Configurando logs profissionais...
python switch_logging.py prod
if %errorlevel% neq 0 (
    echo ❌ Erro ao configurar logging
    pause
    exit /b 1
)
echo  Logs profissionais ativadas
echo.

echo ▶️ PASSO 2: Testando linguagem com logs otimizadas...
echo Executando exemplo...
python module.py examples/first_project/main.mp > temp_output.txt 2>&1
findstr /C:"CorpLang Core:" temp_output.txt >nul
if %errorlevel% equ 0 (
    echo  Logs otimizadas funcionando corretamente
) else (
    echo ❌ Problema com logs otimizadas
    type temp_output.txt
    del temp_output.txt
    pause
    exit /b 1
)
del temp_output.txt
echo.

echo ▶️ PASSO 3: Atualizando extensão VS Code...
cd corp-lang-vscode

:: Verificar se VS Code está disponível
where code >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ VS Code não encontrado no PATH!
    echo 💡 Instale VS Code e adicione ao PATH do sistema.
    cd ..
    pause
    exit /b 1
)

:: Verificar se arquivo vsix existe
if not exist "corp-lang-2.7.0.vsix" (
    echo ❌ Arquivo corp-lang-2.7.0.vsix não encontrado!
    echo 💡 Gerando pacote...
    vsce package --allow-missing-repository --allow-star-activation
    if %errorlevel% neq 0 (
        echo ❌ Erro ao gerar pacote
        cd ..
        pause
        exit /b 1
    )
)

:: Desinstalar versão anterior e instalar nova
echo 📦 Atualizando extensão VS Code...
code --uninstall-extension mf07.corp-lang >nul 2>&1
code --install-extension corp-lang-2.7.0.vsix

if %errorlevel% equ 0 (
    echo  Extensão VS Code atualizada para v2.7.0
) else (
    echo ❌ Erro ao instalar extensão
    cd ..
    pause
    exit /b 1
)

cd ..
echo.

echo   ╔═══════════════════════════════════════════════════════════╗
echo   ║                                                           ║
echo   ║         ATUALIZAÇÃO COMPLETA REALIZADA COM SUCESSO!     ║
echo   ║                                                           ║
echo   ║  🟣 CorpLang v2.7.0 - Logs Profissionais Ativadas        ║
echo   ║                                                           ║
echo   ║  📊 Sistema de Logs:                                      ║
echo   ║     • Logs internas reduzidas em 95%%                     ║
echo   ║     • Saída limpa e profissional                         ║
echo   ║     • 4 níveis configuráveis (prod/dev/quiet/summary)    ║
echo   ║                                                           ║
echo   ║  🎨 Extensão VS Code v2.7.0:                             ║
echo   ║     • 87+ padrões de sintaxe                             ║
echo   ║     • Tema roxo/azul corporativo                         ║
echo   ║     • 25+ snippets prontos                               ║
echo   ║     • Ícones para arquivos .mp                           ║
echo   ║                                                           ║
echo   ║           REINICIE O VS CODE PARA ATIVAR!                 ║
echo   ║                                                           ║
echo   ╚═══════════════════════════════════════════════════════════╝
echo.

echo 💡 Comandos úteis:
echo    python switch_logging.py prod      # Logs profissionais (ativo)
echo    python switch_logging.py dev       # Logs para desenvolvimento
echo    python switch_logging.py quiet     # Logs silenciosas
echo    demo_logging_levels.bat            # Demo dos níveis de log
echo.

pause