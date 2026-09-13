@echo off
title FC Online Web App - Database & TTCN Tool
chcp 65001 >nul
cd /d %~dp0
echo ======================================================================
echo           ⚽ DANG KHOI CHAY WEBSITE FC ONLINE DATABASE & TTCN ⚽
echo ======================================================================
echo.
echo [+] Dang mo trinh duyet tai: http://localhost:8080
echo.
start http://localhost:8080
python web/server.py 8080
exit /b
