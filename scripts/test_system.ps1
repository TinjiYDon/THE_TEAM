# System Test Script
Write-Host "=== System Test ===" -ForegroundColor Cyan

# Check ports
$port8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
$port3000 = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue

Write-Host "[1] Backend (8000): " -NoNewline
if ($port8000) { Write-Host "RUNNING" -ForegroundColor Green } else { Write-Host "NOT RUNNING" -ForegroundColor Red }

Write-Host "[2] Frontend (3000): " -NoNewline
if ($port3000) { Write-Host "RUNNING" -ForegroundColor Green } else { Write-Host "NOT RUNNING" -ForegroundColor Red }

Write-Host ""
Write-Host "[3] Testing Backend API..." -ForegroundColor Yellow
try {
    $r = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/health" -Method GET -TimeoutSec 3 -UseBasicParsing
    Write-Host "  Backend health check: OK" -ForegroundColor Green
} catch {
    Write-Host "  Backend not responding" -ForegroundColor Red
}

Write-Host ""
Write-Host "[4] Demo Account Links:" -ForegroundColor Yellow
Write-Host "  A(101): http://localhost:3000/assistant?user=101&city=beijing"
Write-Host "  B(102): http://localhost:3000/assistant?user=102&city=shanghai"
Write-Host "  C(103): http://localhost:3000/assistant?user=103&city=suzhou"
Write-Host "  D(104): http://localhost:3000/assistant?user=104&city=shanghai"
Write-Host ""
Write-Host "  Community: http://localhost:3000/community?user=104&city=shanghai"
Write-Host "  Groups: http://localhost:3000/groups?user=104&city=shanghai"
Write-Host ""
Write-Host "=== Test Complete ===" -ForegroundColor Cyan

