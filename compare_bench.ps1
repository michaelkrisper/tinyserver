Write-Host "==========================================" -ForegroundColor Cyan
Write-Host " COMPARING TINY C SERVER vs PYTHON SERVER " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

$cwd = (Get-Location).Path

# 1. Start Python Server on port 8080
Write-Host "`n[1] Starting Python http.server on port 8080..." -ForegroundColor Yellow
$pythonProc = Start-Process -PassThru -WindowStyle Hidden -FilePath "python.exe" -ArgumentList "-m http.server 8080" -WorkingDirectory $cwd
Start-Sleep -Seconds 2

Write-Host "Running Benchmark against Python Server..."
node.exe bench.js http://localhost:8080/

Write-Host "Stopping Python server..."
Stop-Process -Id $pythonProc.Id -Force

Start-Sleep -Seconds 2

# 2. Start C Server on port 80
Write-Host "`n[2] Starting Tiny C Server on port 80..." -ForegroundColor Yellow
$cProc = Start-Process -PassThru -WindowStyle Hidden -FilePath "$cwd\server.exe" -WorkingDirectory $cwd
Start-Sleep -Seconds 2

Write-Host "Running Benchmark against Tiny C Server..."
node.exe bench.js http://localhost:80/

Write-Host "Stopping Tiny C Server..."
Stop-Process -Id $cProc.Id -Force

Write-Host "`nDone! Look at the 'Requests Per Second' comparison." -ForegroundColor Green
