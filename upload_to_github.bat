@echo off
setlocal enabledelayedexpansion
title Upload Project to GitHub
echo ================================================================
echo  GIS-Based Highway Network & Accessibility Analysis
echo  GitHub Upload Helper
echo ================================================================
echo.

:: Ensure MinGit and gh are in PATH for this session
set "PATH=C:\Users\laksh\AppData\Local\Programs\MinGit\cmd;C:\Users\laksh\AppData\Local\Programs\gh\bin;%PATH%"

where git >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Git was not found. Please verify MinGit installation.
    pause
    exit /b 1
)

echo [INFO] Git status:
git status
echo.

:: Check if remote origin already exists
git remote get-url origin >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%u in ('git remote get-url origin') do set "EXISTING_REMOTE=%%u"
    echo [INFO] Current remote origin: !EXISTING_REMOTE!
    set /p "CONFIRM=Push to this remote? (Y/N): "
    if /i "!CONFIRM!"=="Y" (
        echo [INFO] Pushing to !EXISTING_REMOTE!...
        git push -u origin main
        echo.
        echo [SUCCESS] Pushed to GitHub successfully!
        pause
        exit /b 0
    )
)

echo.
echo ================================================================
echo  OPTION 1: Using GitHub CLI (gh auth login)
echo  OPTION 2: Provide your GitHub Repository URL directly
echo ================================================================
echo.
echo 1. Enter your GitHub repository URL (e.g. https://github.com/USERNAME/REPO.git)
echo 2. Type 'login' to authenticate via GitHub CLI in your browser
echo.

set /p "USER_INPUT=Enter GitHub Repo URL or 'login': "

if /i "%USER_INPUT%"=="login" (
    echo.
    echo [INFO] Launching GitHub CLI authentication...
    gh auth login -w
    echo.
    set /p "REPO_NAME=Enter repository name to create (default: gis-highway-accessibility-patna): "
    if "!REPO_NAME!"=="" set "REPO_NAME=gis-highway-accessibility-patna"
    echo [INFO] Creating and pushing to GitHub repo: !REPO_NAME!...
    gh repo create !REPO_NAME! --public --source=. --remote=origin --push
    echo.
    echo [SUCCESS] Repository created and pushed to GitHub!
    pause
    exit /b 0
)

if not "%USER_INPUT%"=="" (
    echo.
    echo [INFO] Adding remote origin: %USER_INPUT%
    git remote remove origin >nul 2>&1
    git remote add origin %USER_INPUT%
    echo [INFO] Pushing branch main to GitHub...
    git push -u origin main
    if %errorlevel% equ 0 (
        echo.
        echo [SUCCESS] Project successfully uploaded to GitHub!
    ) else (
        echo.
        echo [NOTE] If authentication failed, create a Personal Access Token (PAT)
        echo on GitHub (Settings -> Developer Settings -> Personal Access Tokens)
        echo and use it as your password, or use Option 2: 'login'.
    )
)

pause
