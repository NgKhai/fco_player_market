@echo off
chcp 65001 >nul
title TẢI TOÀN BỘ MINIFACE FC ONLINE (88.246 THẺ)
color 0B
echo =======================================================================
echo          TẢI FULL KHO ẢNH MINIFACE FC ONLINE (HD)
echo =======================================================================
echo.
echo [1] Đang chuẩn bị môi trường tải đa luồng tốc độ cao (35 workers)...
echo [2] Quá trình tải có hỗ trợ Resume (nếu dừng giữa chừng, mở lại sẽ tiếp tục tải).
echo.
python download_full_minifaces.py
echo.
echo =======================================================================
echo [!] Hoàn tất! Nhấn phím bất kỳ để thoát.
pause >nul
