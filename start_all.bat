@echo off
echo Lanzando backend con Docker Desktop...

cd %~dp0
docker-compose up -d

timeout /t 3 > nul
echo Lanzando GUI...
python gui\test.py
