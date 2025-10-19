@echo off
cls
echo ==================================================
echo    INSTALADOR CORPLANG EXTENSION v2.6.0
echo ==================================================
echo.
echo Este instalador vai:
echo [1] Desinstalar versao anterior (se existir)
echo [2] Instalar CorpLang Advanced v2.5.0
echo [3] Configurar tema automaticamente
echo.
pause

cd /d "%~dp0"

echo.
echo [ETAPA 1/3] Verificando VS Code...
where code >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERRO: VS Code nao encontrado no PATH
    echo    Instale o VS Code primeiro: https://code.visualstudio.com/
    pause
    exit /b 1
)
echo  VS Code encontrado!

echo.
echo [ETAPA 2/3] Removendo versoes antigas...
code --uninstall-extension your-name.corp-lang >nul 2>&1
code --uninstall-extension mf07.corp-lang >nul 2>&1
echo  Limpeza concluida!

echo.
echo [ETAPA 3/3] Instalando CorpLang Advanced v2.3.0...
if exist "corp-lang-2.6.0.vsix" (
    code --install-extension corp-lang-2.6.0.vsix
    if %errorlevel% equ 0 (
        echo  CorpLang Extension instalada com sucesso!
    ) else (
        echo ❌ Erro na instalacao
        pause
        exit /b 1
    )
) else (
    echo ❌ ERRO: Arquivo corp-lang-2.5.0.vsix nao encontrado
    echo    Execute este instalador na pasta da extensao
    pause
    exit /b 1
)

echo.
echo ==================================================
echo             INSTALACAO CONCLUIDA! 
echo ==================================================
echo.
echo  CorpLang Advanced v2.6.0 instalada
echo  Syntax highlighting roxo/azul configurado
echo  25+ snippets corporativos disponiveis
echo.
echo PROXIMOS PASSOS:
echo 1. Abra um arquivo .mp no VS Code
echo 2. Pressione Ctrl+Shift+P
echo 3. Digite "Color Theme" 
echo 4. Selecione "CorpLang Dark Theme"
echo.
echo Teste os snippets:
echo - Digite 'fn' + Tab para funcao
echo - Digite 'class' + Tab para classe
echo - Digite 'asyncfn' + Tab para async function
echo.
pause