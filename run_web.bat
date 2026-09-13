@echo off
title FC Online Laravel Web App - Database & TTCN Tool
chcp 65001 >nul
cd /d %~dp0
echo ======================================================================
echo           ⚽ DANG KHOI CHAY LARAVEL FC ONLINE DATABASE & TTCN ⚽
echo ======================================================================
echo.
echo [+] Dang mo trinh duyet tai: http://127.0.0.1:8000
echo.
start http://127.0.0.1:8000
cd /d %~dp0backend
php artisan serve --host=127.0.0.1 --port=8000
exit /b
