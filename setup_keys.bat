@echo off
REM Quick Setup Script for Multiple API Keys
REM 
REM Cách dùng:
REM 1. Tạo 2-3 API keys từ: https://console.cloud.google.com/apis/credentials
REM 2. Chạy: python setup_keys.py
REM 3. Paste 3 keys khi được hỏi
REM 4. Restart app

echo.
echo ========================================
echo  GEMINI API KEY SETUP
echo ========================================
echo.
echo 📖 Hướng dẫn:
echo 1. Vào: https://console.cloud.google.com/apis/credentials
echo 2. Click: + Create Credentials ^> API Key (Tạo 3 lần)
echo 3. Copy 3 keys
echo 4. Paste vào Terminal khi được hỏi
echo.
echo Chạy script setup...
echo.

python setup_keys.py
pause
