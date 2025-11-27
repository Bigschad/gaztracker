@echo off
REM Script pour démarrer le backend dans Docker pour les tests mobile (Windows)

echo 🐳 Démarrage du backend dans Docker pour les tests mobile...

REM Aller dans le dossier parent
cd ..\..

REM Vérifier que docker-compose.yml existe
if not exist "docker-compose.yml" (
    echo ❌ docker-compose.yml non trouvé dans le dossier parent
    exit /b 1
)

REM Démarrer les services
echo 🚀 Démarrage des services...
docker-compose up -d app postgres redis

REM Attendre que les services soient prêts
echo ⏳ Attente que les services soient prêts...
timeout /t 10 /nobreak >nul

REM Vérifier que l'API répond
echo 🧪 Vérification de l'API...
set MAX_RETRIES=30
set RETRY_COUNT=0

:retry
curl -f http://localhost:8000/health >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo ✅ API est prête!
    goto :ready
)

set /a RETRY_COUNT+=1
if %RETRY_COUNT% GEQ %MAX_RETRIES% (
    echo ❌ L'API n'est pas prête
    echo 📋 Vérifiez les logs: docker-compose logs app
    exit /b 1
)

echo    Tentative %RETRY_COUNT%/%MAX_RETRIES%...
timeout /t 2 /nobreak >nul
goto :retry

:ready
REM Trouver l'IP locale
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    set IP=%%a
    set IP=!IP:~1!
    goto :found
)
:found

echo.
echo ✅ Backend démarré avec succès!
echo.
echo 📋 Informations:
echo    - API: http://localhost:8000
echo    - API (depuis téléphone): http://%IP%:8000
echo.
echo ⚠️  Configuration requise dans mobile-app/src/config/apiConfig.ts:
echo    baseUrl: 'http://%IP%:8000'
echo.
echo 📱 Pour lancer l'app mobile:
echo    cd mobile-app ^&^& npm start
echo.

pause

