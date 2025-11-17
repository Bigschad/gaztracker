@echo off
REM Script de démarrage du backend FastAPI avec --host 0.0.0.0
REM Ce script garantit que le serveur est accessible depuis le réseau local

echo ========================================
echo   Demarrage du backend GazTracker
echo ========================================
echo.

REM Vérifier si l'environnement virtuel existe
if not exist "venv\Scripts\activate.bat" (
    echo [ERREUR] Environnement virtuel non trouve!
    echo Veuillez creer un environnement virtuel avec: python -m venv venv
    pause
    exit /b 1
)

REM Activer l'environnement virtuel
echo [1/3] Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

REM Vérifier si uvicorn est installé
python -c "import uvicorn" 2>nul
if errorlevel 1 (
    echo [ERREUR] uvicorn n'est pas installe!
    echo Installation en cours...
    pip install uvicorn[standard]
)

echo [2/3] Verification de la configuration...
echo Host: 0.0.0.0 (accessible depuis le reseau local)
echo Port: 8000
echo.

echo [3/3] Demarrage du serveur...
echo.
echo ========================================
echo   Serveur accessible sur:
echo   - Local: http://localhost:8000
echo   - Reseau: http://192.168.1.4:8000
echo   - Docs: http://192.168.1.4:8000/docs
echo ========================================
echo.
echo Appuyez sur Ctrl+C pour arreter le serveur
echo.

REM Démarrer uvicorn avec --host 0.0.0.0
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause

