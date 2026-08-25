@echo off
echo Starting Redis with Docker...
echo.

REM Check if Docker is running
docker version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not running!
    echo Please start Docker Desktop first.
    pause
    exit /b 1
)

REM Pull Redis image
echo Pulling Redis image...
docker pull redis:latest

REM Stop existing Redis container if running
docker stop redis-server >nul 2>&1
docker rm redis-server >nul 2>&1

REM Start Redis container
echo Starting Redis container...
docker run -d -p 6379:6379 --name redis-server redis:latest

REM Test Redis connection
echo Testing Redis connection...
timeout /t 3 >nul
docker exec -it redis-server redis-cli ping

if errorlevel 1 (
    echo ERROR: Redis is not responding!
    pause
    exit /b 1
)

echo.
echo ✅ Redis is running successfully!
echo 📊 You can now test Celery with Redis:
echo    python test_celery_setup.py
echo    python -m celery -A crm_project worker -l info
echo.
pause
