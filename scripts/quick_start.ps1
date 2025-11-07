# 一键启动并打开演示页面
Write-Host "=== 账单管理系统 - 快速启动 ===" -ForegroundColor Cyan
Write-Host ""

# 检查服务状态
$backend = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
$frontend = Get-NetTCPConnection -LocalPort 3000 -State Listen -ErrorAction SilentlyContinue

if (-not $backend) {
    Write-Host "[1] 启动后端..." -ForegroundColor Yellow
    Start-Process powershell -ArgumentList "-NoProfile", "-Command", "python start_backend.py"
    Start-Sleep 8
} else {
    Write-Host "[1] 后端已运行" -ForegroundColor Green
}

if (-not $frontend) {
    Write-Host "[2] 启动前端..." -ForegroundColor Yellow
    Start-Process powershell -ArgumentList "-NoProfile", "-Command", "cd frontend; npm run dev"
    Start-Sleep 10
} else {
    Write-Host "[2] 前端已运行" -ForegroundColor Green
}

Write-Host ""
Write-Host "[3] 打开演示页面..." -ForegroundColor Yellow
Start-Process "http://localhost:3000/assistant?user=104&city=shanghai"
Start-Sleep 1
Start-Process "http://localhost:3000/bills?user=104&city=shanghai"
Start-Sleep 1
Start-Process "http://localhost:3000/community?user=104&city=shanghai"

Write-Host ""
Write-Host "=== 启动完成！ ===" -ForegroundColor Green
Write-Host "已打开3个演示页面（用户104）" -ForegroundColor Cyan

