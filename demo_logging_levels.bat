@echo off
echo.
echo 🔧 CorpLang Logging Levels Demo
echo =====================================
echo.

echo 📊 TESTANDO: Profissional (prod)
echo -------------------------------------
python switch_logging.py prod
echo.
echo Executando exemplo...
python module.py examples/first_project/main.mp | head -n 5
echo.

echo 🛠️ TESTANDO: Desenvolvimento (dev) 
echo -------------------------------------
python switch_logging.py dev
echo.
echo Executando exemplo...
python module.py examples/first_project/main.mp | head -n 8
echo.

echo 🤫 TESTANDO: Silencioso (quiet)
echo -------------------------------------
python switch_logging.py quiet
echo.
echo Executando exemplo...
python module.py examples/first_project/main.mp | head -n 3
echo.

echo 📋 Restaurando configuração profissional...
python switch_logging.py prod

echo.
echo  Demo completa! 
echo 💡 Use: python switch_logging.py [prod|dev|quiet|summary]