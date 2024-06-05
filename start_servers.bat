@echo off
REM Set the Python path
set PYTHONPATH=C:\WebServer\HollyWood

REM Change to the directory of the Nginx server
cd /d C:\WebServer\nginx

REM Start Nginx server
start nginx.exe

REM Change to the HollyWood directory
cd /d C:\WebServer\HollyWood

REM Start HollyWood FastAPI server
start cmd /k "set PYTHONPATH=C:\WebServer\HollyWood && uvicorn main:app --host 0.0.0.0 --port 8001 --workers 2 --backlog 2048"

REM End of script
@echo on
