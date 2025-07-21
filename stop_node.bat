@echo off
echo Stopping TorrentNode Net...

docker-compose -f infra/docker-compose.yml down
 
echo.
echo SUCCESS! The node has been stopped.
echo.
pause 