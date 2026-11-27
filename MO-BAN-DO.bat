@echo off
if not exist "%~dp0index.html" (
  echo Khong tim thay index.html. Hay giai nen hoac clone day du repo.
  pause
  exit /b 1
)
start "" "%~dp0index.html"
