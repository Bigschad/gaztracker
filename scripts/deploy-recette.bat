@echo off
REM =============================================================================
REM Script de déploiement pour l'environnement de recette (Windows)
REM =============================================================================

setlocal enabledelayedexpansion

REM Vérifier que Docker est installé
where docker >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Docker n'est pas installé. Veuillez l'installer d'abord.
    exit /b 1
)

REM Vérifier que Docker Compose est installé
where docker-compose >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Docker Compose n'est pas installé. Veuillez l'installer d'abord.
    exit /b 1
)

REM Vérifier que le fichier .env.recette existe
if not exist ".env.recette" (
    echo [WARNING] Le fichier .env.recette n'existe pas.
    echo [INFO] Création d'un fichier .env.recette depuis le template...
    
    if exist ".env.example" (
        copy .env.example .env.recette >nul
        echo [WARNING] IMPORTANT: Modifiez le fichier .env.recette avec vos configurations avant de continuer!
        echo [WARNING]    Notamment: POSTGRES_PASSWORD, REDIS_PASSWORD, SECRET_KEY
        exit /b 1
    ) else (
        echo [ERROR] Aucun fichier .env.example trouvé. Créez manuellement .env.recette
        exit /b 1
    )
)

REM Gestion des commandes
if "%1"=="" goto show_help
if "%1"=="help" goto show_help
if "%1"=="--help" goto show_help
if "%1"=="-h" goto show_help

if "%1"=="start" goto start_services
if "%1"=="stop" goto stop_services
if "%1"=="restart" goto restart_services
if "%1"=="logs" goto show_logs
if "%1"=="rebuild" goto rebuild_images
if "%1"=="migrate" goto run_migrations
if "%1"=="health" goto health_check
if "%1"=="status" goto show_status

echo [ERROR] Commande inconnue: %1
echo.
goto show_help

:start_services
echo [INFO] Démarrage des services de recette...
if "%2"=="--with-tools" (
    echo [INFO] Démarrage avec PgAdmin (outils de gestion)...
    docker-compose -f docker-compose.recette.yml --profile tools up -d
) else (
    docker-compose -f docker-compose.recette.yml up -d
)
echo [INFO] Attente du démarrage des services...
timeout /t 5 /nobreak >nul
echo [INFO] État des services:
docker-compose -f docker-compose.recette.yml ps
goto end

:stop_services
echo [INFO] Arrêt des services de recette...
docker-compose -f docker-compose.recette.yml down
goto end

:restart_services
call :stop_services
timeout /t 2 /nobreak >nul
call :start_services
goto end

:show_logs
if "%2"=="" (
    docker-compose -f docker-compose.recette.yml logs -f
) else (
    docker-compose -f docker-compose.recette.yml logs -f %2
)
goto end

:rebuild_images
echo [INFO] Reconstruction des images...
docker-compose -f docker-compose.recette.yml build --no-cache
if "%2"=="--restart" (
    echo [INFO] Redémarrage des services...
    docker-compose -f docker-compose.recette.yml up -d
)
goto end

:run_migrations
echo [INFO] Exécution des migrations de base de données...
docker-compose -f docker-compose.recette.yml exec app alembic upgrade head
goto end

:health_check
echo [INFO] Vérification de la santé des services...
echo.
echo [INFO] Backend API:
curl -s http://localhost:8001/health >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] Backend API est accessible
) else (
    echo [ERROR] Backend API n'est pas accessible
)
echo.
echo [INFO] PostgreSQL:
docker-compose -f docker-compose.recette.yml exec -T postgres pg_isready -U gaztracker_user >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] PostgreSQL est prêt
) else (
    echo [ERROR] PostgreSQL n'est pas prêt
)
echo.
echo [INFO] Redis:
docker-compose -f docker-compose.recette.yml exec -T redis redis-cli ping >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] Redis est prêt
) else (
    echo [ERROR] Redis n'est pas prêt
)
goto end

:show_status
docker-compose -f docker-compose.recette.yml ps
goto end

:show_help
echo Usage: %0 [COMMAND] [OPTIONS]
echo.
echo Commandes disponibles:
echo   start [--with-tools]    Démarrer les services (--with-tools pour inclure PgAdmin)
echo   stop                    Arrêter les services
echo   restart                 Redémarrer les services
echo   logs [service]          Afficher les logs (optionnel: nom du service)
echo   rebuild [--restart]     Reconstruire les images (--restart pour redémarrer après)
echo   migrate                 Exécuter les migrations de base de données
echo   health                  Vérifier la santé des services
echo   status                  Afficher l'état des services
echo   help                    Afficher cette aide
echo.
echo Exemples:
echo   %0 start                Démarrer les services
echo   %0 start --with-tools   Démarrer avec PgAdmin
echo   %0 logs app             Voir les logs du backend
echo   %0 rebuild --restart    Reconstruire et redémarrer
goto end

:end
endlocal

