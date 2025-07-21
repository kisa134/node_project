@echo off
echo Starting TorrentNode Net in Docker...

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not running. Please start Docker Desktop and try again.
    pause
    exit /b 1
)

echo Building and starting the node container in the background...
docker-compose -f infra/docker-compose.yml up --build -d

if %errorlevel% neq 0 (
    echo [ERROR] Failed to start the node. Please check the output above.
    pause
    exit /b 1
)

echo.
echo SUCCESS! TorrentNode is running in the background.
echo.
echo To see the logs, run this command in your terminal:
echo docker-compose -f infra/docker-compose.yml logs -f
echo.
echo To stop the node, run the stop_node.bat script.
echo.
pause 