@echo off
echo Starting chat application server...
echo.

:: 显示IP地址
echo Your IP addresses:
ipconfig | findstr /i "IPv4"
echo.
echo Access your application using one of these IP addresses on port 3888
echo Example: http://192.168.x.x:3888
echo.

:: 启动后端服务器
echo Starting backend server...
cd backend
python -m app.main

pause 