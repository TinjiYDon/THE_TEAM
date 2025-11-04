# 启动服务并测试
Write-Host "=== 账单管理系统 - 启动与测试脚本 ===" -ForegroundColor Cyan
Write-Host ""

# 检查端口
$port8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
$port3000 = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue

Write-Host "[1/4] 检查服务状态..." -ForegroundColor Yellow

if ($port8000) {
    Write-Host "  ✓ 后端服务 (8000) 已运行" -ForegroundColor Green
} else {
    Write-Host "  ✗ 后端服务 (8000) 未运行，需要启动" -ForegroundColor Red
    Write-Host "    启动命令: python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000" -ForegroundColor Gray
}

if ($port3000) {
    Write-Host "  ✓ 前端服务 (3000) 已运行" -ForegroundColor Green
} else {
    Write-Host "  ✗ 前端服务 (3000) 未运行，需要启动" -ForegroundColor Red
    Write-Host "    启动命令: cd frontend; npm run dev" -ForegroundColor Gray
}

Write-Host ""
Write-Host "[2/4] 测试后端 API..." -ForegroundColor Yellow

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/health" -Method GET -TimeoutSec 3 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "  ✓ 后端健康检查通过" -ForegroundColor Green
    }
} catch {
    Write-Host "  ✗ 后端未响应: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "[3/4] 测试数据检查..." -ForegroundColor Yellow

try {
    $users = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/groups?limit=5" -Method GET -TimeoutSec 3 -UseBasicParsing | ConvertFrom-Json
    if ($users.success -and $users.data.Count -gt 0) {
        Write-Host "  ✓ 群组数据已加载 (找到 $($users.data.Count) 个群组)" -ForegroundColor Green
    }
} catch {
    Write-Host "  ✗ 群组数据检查失败: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "[4/4] 演示账号快速链接" -ForegroundColor Yellow
Write-Host ""
Write-Host "  A(101) 北京普通用户:" -ForegroundColor Cyan
Write-Host '    http://localhost:3000/assistant?user=101&city=beijing' -ForegroundColor White
Write-Host ""
Write-Host "  B(102) 上海订购用户 (已入综合理财群):" -ForegroundColor Cyan
Write-Host '    http://localhost:3000/assistant?user=102&city=shanghai' -ForegroundColor White
Write-Host ""
Write-Host "  C(103) 苏州普通用户 (教育/医疗):" -ForegroundColor Cyan
Write-Host '    http://localhost:3000/assistant?user=103&city=suzhou' -ForegroundColor White
Write-Host ""
Write-Host "  D(104) 上海餐饮Top1 (已入上海餐饮群) [重点测试]:" -ForegroundColor Cyan
Write-Host '    http://localhost:3000/assistant?user=104&city=shanghai' -ForegroundColor White
Write-Host "    → 应自动弹出'加入上海餐饮群'提示" -ForegroundColor Yellow
Write-Host ""
Write-Host "  社群广场:" -ForegroundColor Cyan
Write-Host '    http://localhost:3000/community?user=104&city=shanghai' -ForegroundColor White
Write-Host ""
Write-Host "  群组列表:" -ForegroundColor Cyan
Write-Host '    http://localhost:3000/groups?user=104&city=shanghai' -ForegroundColor White
Write-Host ""
Write-Host "=== 测试完成 ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "提示: 如果服务未运行，请在新终端执行以下命令：" -ForegroundColor Yellow
Write-Host '  后端: python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000' -ForegroundColor Gray
Write-Host '  前端: cd frontend; npm run dev' -ForegroundColor Gray
Write-Host ""

