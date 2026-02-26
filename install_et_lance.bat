@echo off
setlocal EnableExtensions

title Installation et lancement - Orthophonie

REM Se placer dans le dossier du script, meme si lance par double-clic
cd /d "%~dp0"

set "VENV_DIR=.venv"
set "VENV_PY=%VENV_DIR%\Scripts\python.exe"
set "VENV_ACTIVATE=%VENV_DIR%\Scripts\activate.bat"
set "REQUIREMENTS=requirements.txt"
set "APP_FILE=interface_web.py"

echo ====================================================
echo   Outil Orthophonie - Installation et lancement
echo ====================================================
echo.

if not exist "%APP_FILE%" (
    echo [ERREUR] Fichier introuvable : %APP_FILE%
    goto :error
)

if not exist "%VENV_PY%" (
    echo [INFO] Environnement virtuel non trouve. Creation en cours...
    call :find_python
    if errorlevel 1 goto :error

    %PYTHON_BOOTSTRAP% -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo [ERREUR] Impossible de creer l'environnement virtuel.
        goto :error
    )

    call "%VENV_ACTIVATE%"
    if errorlevel 1 (
        echo [ERREUR] Impossible d'activer l'environnement virtuel.
        goto :error
    )

    if not exist "%REQUIREMENTS%" (
        echo [ERREUR] Fichier introuvable : %REQUIREMENTS%
        goto :error
    )

    echo [INFO] Installation des dependances...
    python -m pip install --upgrade pip
    if errorlevel 1 (
        echo [ERREUR] Echec de mise a jour de pip.
        goto :error
    )

    python -m pip install -r "%REQUIREMENTS%"
    if errorlevel 1 (
        echo [ERREUR] Echec d'installation des dependances.
        goto :error
    )
) else (
    echo [INFO] Environnement virtuel detecte. Installation ignoree.
    call "%VENV_ACTIVATE%"
    if errorlevel 1 (
        echo [ERREUR] Impossible d'activer l'environnement virtuel.
        goto :error
    )
)

echo [INFO] Lancement de l'interface Streamlit...
python -m streamlit run "%APP_FILE%"
if errorlevel 1 (
    echo [ERREUR] L'application s'est arretee avec une erreur.
    goto :error
)

exit /b 0

:find_python
where py >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_BOOTSTRAP=py -3"
    exit /b 0
)

where python >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_BOOTSTRAP=python"
    exit /b 0
)

echo [ERREUR] Python est introuvable.
echo         Installe Python 3 puis relance ce script.
exit /b 1

:error
echo.
echo Le script s'est arrete.
pause
exit /b 1
