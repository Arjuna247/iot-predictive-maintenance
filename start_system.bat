@echo off
chcp 65001 >nul
echo ============================================================
echo   IoT Predictive Maintenance System -- Startup
echo ============================================================
echo.

REM -- PYTHONUTF8=1 prevents emoji UnicodeEncodeError on Windows consoles
set PYTHONUTF8=1

REM -- PREREQUISITE: MongoDB must be running before starting the backend.
REM    If MongoDB is not installed as a service, start it manually first:
REM      mongod --dbpath C:\data\db
REM    Default connection: mongodb://localhost:27017/iot_maintenance

REM -- 1. Backend ----------------------------------------------------------
echo [1/4] Starting Backend API (Flask + MongoDB) on port 5000 ...
start "IoT Backend" cmd /k "set PYTHONUTF8=1 && cd /d %~dp0backend && pip install -r requirements.txt -q && python app.py"
timeout /t 3 /nobreak >nul

REM -- 2. Physical Node (simulation fallback) ------------------------------
echo [2/4] Starting Physical Node (simulation mode) ...
start "Physical Node"  cmd /k "set PYTHONUTF8=1 && cd /d %~dp0edge_nodes && pip install -r requirements.txt -q && python physical_node.py --simulate"

REM    To use live ESP32 data over Wi-Fi instead, replace the line above with:
REM    start "Physical Node" cmd /k "set PYTHONUTF8=1 && cd /d %~dp0edge_nodes && python physical_node.py --esp32-wifi"
REM    Then POST sensor JSON from the ESP32 to  http://<THIS_PC_IP>:5005/esp32/data

REM -- 3. Simulated Node ---------------------------------------------------
echo [3/4] Starting Simulated Node ...
start "Simulated Node" cmd /k "set PYTHONUTF8=1 && cd /d %~dp0edge_nodes && pip install -r requirements.txt -q && python simulated_node.py"
timeout /t 3 /nobreak >nul

REM -- 4. Frontend ---------------------------------------------------------
echo [4/4] Starting React Frontend on port 3000 ...
start "IoT Frontend" cmd /k "cd /d %~dp0frontend && npm install && npm start"

echo.
echo ============================================================
echo   All services launched in separate windows.
echo   Dashboard  -^> http://localhost:3000
echo   Backend    -^> http://localhost:5000/api/health
echo   MongoDB    -^> mongodb://localhost:27017/iot_maintenance
echo   ESP32 WiFi -^> POST to http://^<THIS_PC_IP^>:5005/esp32/data
echo   FL interval: 30 seconds (peer-to-peer FedAvg)
echo   Press any key to exit this launcher.
echo ============================================================
pause >nul
