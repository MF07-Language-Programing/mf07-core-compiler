@echo off
set "PY_EXEC=%~dp0env\Scripts\python.exe"
if exist "%PY_EXEC%" (
	"%PY_EXEC%" "%~dp0mf.py" %*
) else (
	python "%~dp0mf.py" %*
)
