@echo off
REM Intelligent RAG Assistant - Heroku Deployment
REM Author: Sreevallabh kakarala
REM Version: 2.0 (Cloud Edition)

echo ===============================================
echo  RAG Assistant - Heroku Cloud Deployment
echo  Author: Sreevallabh kakarala
echo ===============================================

echo.
echo [1/7] Checking prerequisites...

REM Check Git
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Git not found. Please install Git first.
    echo Download from: https://git-scm.com/
    pause
    exit /b 1
)

REM Check Heroku CLI
heroku --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Heroku CLI not found. Please install it first.
    echo Download from: https://devcenter.heroku.com/articles/heroku-cli
    pause
    exit /b 1
)

echo.
echo [2/7] Logging into Heroku...
heroku auth:whoami >nul 2>&1
if %errorlevel% neq 0 (
    echo Please login to Heroku:
    heroku login
)

echo.
echo [3/7] Setting up for cloud deployment...
REM Copy requirements for Heroku
copy requirements-heroku.txt requirements.txt

echo.
echo [4/7] Creating Heroku app...
set /p APP_NAME=Enter your app name (or press Enter for auto-generated): 
if "%APP_NAME%"=="" (
    heroku create
) else (
    heroku create %APP_NAME%
)

if %errorlevel% neq 0 (
    echo ERROR: Failed to create Heroku app.
    pause
    exit /b 1
)

echo.
echo [5/7] Setting up environment variables...
echo.
echo IMPORTANT: You need to set your OpenAI API key for the app to work.
echo You can do this in two ways:
echo 1. Set it now (recommended)
echo 2. Set it later in Heroku dashboard
echo.
set /p SET_API_KEY=Do you want to set your OpenAI API key now? (y/n): 
if /i "%SET_API_KEY%"=="y" (
    set /p OPENAI_KEY=Enter your OpenAI API key: 
    heroku config:set OPENAI_API_KEY=%OPENAI_KEY%
)

echo.
echo [6/7] Deploying to Heroku...
git add .
git commit -m "Deploy RAG Assistant Cloud Edition by Sreevallabh kakarala"
git push heroku main

if %errorlevel% neq 0 (
    echo ERROR: Deployment failed.
    pause
    exit /b 1
)

echo.
echo [7/7] Opening your deployed app...
for /f "tokens=*" %%i in ('heroku apps:info --shell ^| findstr web_url') do set %%i
echo.
echo ===============================================
echo  🚀 Deployment Complete!
echo  📊 App URL: %web_url%
echo  🌐 Status: Live on Heroku
echo  ⚡ Edition: Cloud (OpenAI-powered)
echo  👨‍💻 Developer: Sreevallabh kakarala
echo ===============================================
echo.
echo Opening your app...
start %web_url%

echo.
echo Useful commands:
echo - View logs: heroku logs --tail
echo - Open app: heroku open
echo - Set API key: heroku config:set OPENAI_API_KEY=your_key_here
echo.

pause 