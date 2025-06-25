@echo off
REM Intelligent RAG Assistant - Docker Deployment
REM Author: Sreevallabh kakarala
REM Version: 2.0

echo ===============================================
echo  RAG Assistant - Docker Deployment
echo  Author: Sreevallabh kakarala
echo ===============================================

echo.
echo [1/4] Checking Docker installation...
docker --version
if %errorlevel% neq 0 (
    echo ERROR: Docker not found. Please install Docker Desktop first.
    echo Download from: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

echo.
echo [2/4] Building Docker image...
docker build -t rag-assistant:latest .
if %errorlevel% neq 0 (
    echo ERROR: Failed to build Docker image.
    pause
    exit /b 1
)

echo.
echo [3/4] Stopping any existing containers...
docker stop rag-assistant-container 2>nul
docker rm rag-assistant-container 2>nul

echo.
echo [4/4] Starting RAG Assistant container...
echo.
echo ===============================================
echo  🚀 RAG Assistant is starting in Docker...
echo  📊 Access at: http://localhost:8501
echo  🐳 Mode: Containerized
echo  🔒 Security: Enhanced (non-root user)
echo ===============================================
echo.

docker run -d ^
  --name rag-assistant-container ^
  -p 8501:8501 ^
  --restart unless-stopped ^
  rag-assistant:latest

echo.
echo Container started successfully!
echo View logs: docker logs -f rag-assistant-container
echo Stop container: docker stop rag-assistant-container
echo.

pause 