@echo off
REM Script de configuration et test pour GazTracker Mobile (Windows)

echo 🚀 Configuration de l'environnement de test...

REM Vérifier Node.js
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Node.js n'est pas installé
    exit /b 1
)

echo ✅ Node.js installé
node --version

REM Vérifier npm
where npm >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ npm n'est pas installé
    exit /b 1
)

echo ✅ npm installé
npm --version

REM Installer les dépendances
echo 📦 Installation des dépendances...
call npm install

REM Trouver l'IP locale
echo 🔍 Recherche de l'IP locale...
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    set IP=%%a
    set IP=!IP:~1!
    goto :found
)
:found

echo 📍 IP locale trouvée: %IP%
echo.
echo ⚠️  IMPORTANT: Mettez à jour src/config/apiConfig.ts avec cette IP:
echo    baseUrl: 'http://%IP%:8000'
echo.
echo ✅ Configuration terminée!
echo.
echo 📱 Pour démarrer l'application:
echo    npm start
echo.
echo 🔧 Pour tester sur Android:
echo    npm run android
echo.

pause

