@echo off

REM Levantar los contenedores
docker-compose up -d --build

REM Esperar un momento para asegurarse de que los servicios estén en funcionamiento
timeout /t 5

REM Abrir el navegador
@REM start http://localhost:8000
start http://localhost:8080
