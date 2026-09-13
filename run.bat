@echo off
title FC Online Data Extractor & Market Tool
chcp 65001 >nul
cd /d %~dp0
python main.py
pause
