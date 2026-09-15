@echo off
chcp 65001 >nul
title my-ai-chat 一键启动
echo ==========================================
echo    my-ai-chat 一键启动（Docker Compose）
echo ==========================================
echo.

echo [1/3] 检查 Docker 环境...
docker info >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Docker，请先安装并启动 Docker Desktop
    pause
    exit /b 1
)
echo        OK

echo [2/3] 检查 aliyun 环境变量...
if "%aliyun%"=="" (
    echo [错误] 未检测到 aliyun 环境变量
    echo.
    echo 请先执行下面的命令设置 API Key，然后重新打开终端再运行本脚本：
    echo     setx aliyun "sk-你的APIKey"
    pause
    exit /b 1
)
echo        OK

echo [3/3] 构建并启动全部服务（首次构建需几分钟，请耐心等待）...
docker compose up -d --build
if errorlevel 1 (
    echo [错误] 启动失败，请查看上方日志
    pause
    exit /b 1
)

echo.
echo ==========================================
echo    启动完成！
echo      前端页面:  http://localhost:8080
echo      后端接口:  http://localhost:8000
echo      停止服务:  docker compose down
echo ==========================================
echo.
timeout /t 3 >nul
start http://localhost:8080
