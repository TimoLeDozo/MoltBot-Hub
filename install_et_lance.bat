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
set "ENV_FILE=.env"
set "ENV_EXAMPLE=.env.example"

echo ====================================================
echo   Outil Orthophonie - Installation et lancement
echo ====================================================
echo.

if not exist "%APP_FILE%" (
    echo [ERREUR] Fichier introuvable : %APP_FILE%
    goto :error
)

REM --- VERIFICATION DE L'ENVIRONNEMENT VIRTUEL ---
if exist "%VENV_PY%" goto :venv_exists

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

echo [INFO] Installation des dependances (Patientez quelques minutes)...
python -m pip install --upgrade pip
python -m pip install -r "%REQUIREMENTS%"
if errorlevel 1 (
    echo [ERREUR] Echec d'installation des dependances.
    goto :error
)

call :ensure_env
if errorlevel 1 goto :error

goto :launch

:venv_exists
echo [INFO] Environnement virtuel detecte. Installation ignoree.
call "%VENV_ACTIVATE%"
if errorlevel 1 (
    echo [ERREUR] Impossible d'activer l'environnement virtuel.
    goto :error
)

call :ensure_env
if errorlevel 1 goto :error

:launch
echo.
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

:ensure_env
if not exist "%ENV_FILE%" (
    if exist "%ENV_EXAMPLE%" (
        copy /Y "%ENV_EXAMPLE%" "%ENV_FILE%" >nul
        echo [INFO] Fichier .env cree depuis .env.example.
    ) else (
        > "%ENV_FILE%" (
            echo GOOGLE_API_KEY=
            echo GEMINI_MODEL=gemini-2.5-flash
            echo # Optional: set POPPLER_PATH if Poppler is not in PATH
            echo # POPPLER_PATH=C:\poppler\Library\bin
        )
        echo [INFO] Fichier .env cree.
    )
)

set "GOOGLE_API_KEY="
for /f "usebackq tokens=1,* delims==" %%A in ("%ENV_FILE%") do (
    if /I "%%A"=="GOOGLE_API_KEY" set "GOOGLE_API_KEY=%%B"
)

if defined GOOGLE_API_KEY exit /b 0

echo [CONFIG] Aucune GOOGLE_API_KEY detectee dans %ENV_FILE%.
set /p GOOGLE_API_KEY=Collez votre cle Google AI Studio puis appuyez sur Entree :
if not defined GOOGLE_API_KEY (
    echo [ERREUR] La cle API est obligatoire pour lancer l'application.
    exit /b 1
)

> "%ENV_FILE%" (
    echo GOOGLE_API_KEY=%GOOGLE_API_KEY%
    echo GEMINI_MODEL=gemini-2.5-flash
    echo # Optional: set POPPLER_PATH if Poppler is not in PATH
    echo # POPPLER_PATH=C:\poppler\Library\bin
)
echo [INFO] Fichier .env mis a jour.
exit /b 0

:error
echo.
echo Le script s'est arrete.
pause
exit /b 1
