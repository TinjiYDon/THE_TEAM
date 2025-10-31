# PowerShell测试启动脚本
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "账单查询与管理系统 - 测试启动" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Write-Host "`n1. 检查后端服务..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/health" -TimeoutSec 3 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "[OK] 后端服务正在运行" -ForegroundColor Green
        $data = $response.Content | ConvertFrom-Json
        Write-Host "    状态: $($data.status)" -ForegroundColor Gray
    }
} catch {
    Write-Host "[X] 后端服务未运行" -ForegroundColor Red
    Write-Host "    请运行: python run_server.py" -ForegroundColor Yellow
}

Write-Host "`n2. 检查前端服务..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 2 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "[OK] 前端服务正在运行" -ForegroundColor Green
    }
} catch {
    Write-Host "[X] 前端服务未运行" -ForegroundColor Red
    Write-Host "    请运行: cd frontend; npm run dev" -ForegroundColor Yellow
}

Write-Host "`n3. 测试API端点..." -ForegroundColor Yellow
$endpoints = @(
    @{name='health_check'; url='/health'},
    @{name='bills_list'; url='/bills?limit=5&user_id=1'},
    @{name='spending_summary'; url='/analysis/summary?user_id=1'}
)

$successCount = 0
foreach ($endpoint in $endpoints) {
    try {
        $fullUrl = "http://localhost:8000/api/v1" + $endpoint.url
        $response = Invoke-WebRequest -Uri $fullUrl -TimeoutSec 3 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Host "[OK] $($endpoint.name)" -ForegroundColor Green
            $successCount++
        }
    } catch {
        Write-Host "[X] $($endpoint.name)" -ForegroundColor Red
    }
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "测试完成: $successCount/$($endpoints.Count) 通过" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Write-Host "`n访问地址:" -ForegroundColor Yellow
Write-Host "  前端: http://localhost:3000" -ForegroundColor White
Write-Host "  后端API文档: http://localhost:8000/docs" -ForegroundColor White
Write-Host "  健康消费: http://localhost:3000/health" -ForegroundColor White

Write-Host "`n测试账号:" -ForegroundColor Yellow
Write-Host "  用户名: user1, user2, user3" -ForegroundColor White
Write-Host "  密码: demo123" -ForegroundColor White

