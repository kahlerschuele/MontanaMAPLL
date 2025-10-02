@echo off
echo Stopping old backend servers...
FOR /F "tokens=5" %%P IN ('netstat -ano ^| findstr :8001') DO (
    echo Killing process %%P on port 8001
    taskkill /F /PID %%P 2>nul
)

FOR /F "tokens=5" %%P IN ('netstat -ano ^| findstr :8000') DO (
    echo Killing process %%P on port 8000
    taskkill /F /PID %%P 2>nul
)

timeout /t 2 /nobreak >nul

echo Starting backend server on port 8001...
cd backend
start "Montana Map Backend" python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload

echo.
echo Backend starting on http://localhost:8001
echo Check the new window for server logs
echo.
pause
