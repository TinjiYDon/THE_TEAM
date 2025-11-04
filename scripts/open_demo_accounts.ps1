# Open Demo Accounts Script
$baseUrl = "http://localhost:3000"
$chromePath = "C:\Program Files\Google\Chrome\Application\chrome.exe"
$edgePath = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

# Detect browser
$browser = $null
if (Test-Path $chromePath) {
    $browser = $chromePath
} elseif (Test-Path $edgePath) {
    $browser = $edgePath
} else {
    Write-Host "Browser not found. Please open manually:"
    Write-Host "A(101): $baseUrl/assistant?user=101&city=beijing"
    Write-Host "B(102): $baseUrl/assistant?user=102&city=shanghai"
    Write-Host "C(103): $baseUrl/assistant?user=103&city=suzhou"
    Write-Host "D(104): $baseUrl/assistant?user=104&city=shanghai"
    exit
}

# Account config
$accounts = @(
    @{ id = 101; name = "A"; city = "beijing"; desc = "Normal-Beijing-Food/Transport" },
    @{ id = 102; name = "B"; city = "shanghai"; desc = "Premium-Shanghai-Shopping/Travel-In Group" },
    @{ id = 103; name = "C"; city = "suzhou"; desc = "Normal-Suzhou-Education/Medical" },
    @{ id = 104; name = "D"; city = "shanghai"; desc = "Shanghai-Food Top1-In Food Group" }
)

Write-Host "Opening 4 demo accounts..."
Write-Host ""

foreach ($acc in $accounts) {
    $userDataDir = "$env:TEMP\demo-account-$($acc.id)"
    $url = "$baseUrl/assistant?user=$($acc.id)" + "&city=$($acc.city)"
    
    Write-Host "[$($acc.name)] $($acc.desc)"
    Write-Host "  URL: $url"
    
    Start-Process $browser -ArgumentList "--user-data-dir=$userDataDir", $url
    Start-Sleep -Milliseconds 500
}

Write-Host ""
Write-Host "All 4 accounts opened. Each uses independent user data directory."
Write-Host ""
Write-Host "Quick links:"
Write-Host '  Assistant: /assistant?user=XXX&city=XXX'
Write-Host '  Community: /community?user=XXX&city=XXX'
Write-Host '  Groups: /groups?user=XXX&city=XXX'
Write-Host '  Bills: /bills?user=XXX&city=XXX'
