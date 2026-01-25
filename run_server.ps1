# PowerShell script to run Django development server
Write-Host "Starting Django Development Server..." -ForegroundColor Green
Set-Location $PSScriptRoot
& ".\myenv\Scripts\python.exe" manage.py runserver



