@echo off
REM Script de test avec Docker pour GazTracker Mobile (Windows)

echo 🐳 Configuration de l'environnement de test Docker...

REM Vérifier Docker
where docker >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Docker n'est pas installé
    exit /b 1
)

echo ✅ Docker installé
docker --version

REM Vérifier Docker Compose
where docker-compose >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Docker Compose n'est pas installé
    exit /b 1
)

echo ✅ Docker Compose installé
docker-compose --version

REM Trouver l'IP locale
echo 🔍 Recherche de l'IP locale...
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    set IP=%%a
    set IP=!IP:~1!
    goto :found
)
:found

echo 📍 IP locale: %IP%

REM Démarrer les services
echo 🚀 Démarrage des services Docker...
docker-compose -f docker-compose.mobile.yml up -d

REM Attendre que l'API soit prête
echo ⏳ Attente que l'API soit prête...
timeout /t 10 /nobreak >nul

REM Test de santé
echo 🧪 Test de l'API...
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
    echo ❌ L'API n'est pas prête après %MAX_RETRIES% tentatives
    echo 📋 Vérifiez les logs: docker-compose -f docker-compose.mobile.yml logs api
    exit /b 1
)

echo    Tentative %RETRY_COUNT%/%MAX_RETRIES%...
timeout /t 2 /nobreak >nul
goto :retry

:ready
echo.
echo ✅ Environnement Docker prêt!
echo.
echo 📋 Informations importantes:
echo    - API: http://localhost:8000
echo    - API (depuis téléphone): http://%IP%:8000
echo    - Health check: http://localhost:8000/health
echo.
echo ⚠️  Configuration requise:
echo    1. Mettre à jour src/config/apiConfig.ts:
echo       baseUrl: 'http://%IP%:8000'
echo.
echo    2. Vérifier que votre téléphone est sur le même WiFi
echo.
echo 📱 Commandes utiles:
echo    - Voir les logs: docker-compose -f docker-compose.mobile.yml logs -f
echo    - Arrêter: docker-compose -f docker-compose.mobile.yml down
echo    - Redémarrer: docker-compose -f docker-compose.mobile.yml restart api
echo.

pause

