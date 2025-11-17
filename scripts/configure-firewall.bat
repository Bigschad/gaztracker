@echo off
REM Script pour configurer le pare-feu Windows pour le port 8000
REM Doit être exécuté en tant qu'administrateur

echo ========================================
echo   Configuration du pare-feu Windows
echo   pour le port 8000
echo ========================================
echo.

REM Vérifier les privilèges administrateur
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERREUR] Ce script doit etre execute en tant qu'administrateur!
    echo Clic droit sur le fichier -^> Executer en tant qu'administrateur
    pause
    exit /b 1
)

echo [1/2] Suppression des anciennes regles (si elles existent)...
netsh advfirewall firewall delete rule name="GazTracker Backend Port 8000" >nul 2>&1

echo [2/2] Creation de la regle de pare-feu...
netsh advfirewall firewall add rule name="GazTracker Backend Port 8000" dir=in action=allow protocol=TCP localport=8000

if %errorLevel% equ 0 (
    echo.
    echo ========================================
    echo   Regle creee avec succes!
    echo ========================================
    echo.
    echo Le port 8000 est maintenant accessible depuis le reseau local.
    echo.
) else (
    echo.
    echo [ERREUR] Impossible de creer la regle de pare-feu.
    echo.
)

pause

