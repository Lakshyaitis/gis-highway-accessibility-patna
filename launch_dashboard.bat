@echo off
title Patna GIS Dashboard Launcher
echo ================================================================
echo Launching Patna Highway Network & Accessibility GIS Dashboard...
echo ================================================================
powershell -ExecutionPolicy Bypass -File "%~dp0scripts\serve_dashboard.ps1"
pause
