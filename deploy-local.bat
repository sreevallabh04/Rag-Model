@echo off
REM Intelligent RAG Assistant - Local Production Deployment
REM Author: Sreevallabh kakarala
REM Version: 2.0

echo ===============================================
echo  Intelligent RAG Assistant - Production Setup
echo  Author: Sreevallabh kakarala
echo ===============================================

echo.
echo [1/6] Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Please install Python 3.8+ first.
    pause
    exit /b 1
)

echo.
echo [2/6] Installing production requirements...
pip install -r requirements-prod.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install requirements.
    pause
    exit /b 1
)

echo.
echo [3/6] Checking Ollama installation...
where ollama >nul 2>nul
if %errorlevel% neq 0 (
    echo WARNING: Ollama not found. Installing...
    winget install Ollama.Ollama
)

echo.
echo [4/6] Starting Ollama service...
start /B ollama serve
timeout /t 5 /nobreak >nul

echo.
echo [5/6] Pulling Mistral model...
ollama pull mistral:latest
if %errorlevel% neq 0 (
    echo ERROR: Failed to pull Mistral model.
    pause
    exit /b 1
)

echo.
echo [6/6] Starting RAG Assistant in production mode...
echo.
echo ===============================================
echo  🚀 RAG Assistant is starting...
echo  📊 Access at: http://localhost:8501
echo  🤖 AI Model: Mistral (Local)
echo  🔒 Mode: Production
echo ===============================================
echo.

set ENVIRONMENT=production
streamlit run main.py --server.port 8501 --server.headless true

pause 