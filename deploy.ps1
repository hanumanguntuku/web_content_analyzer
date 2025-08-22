# Deployment Scripts - M1-DEPLOY-02
# Automated deployment and management scripts

# Windows PowerShell deployment script
echo "🚀 Web Content Analyzer - Deployment Script"
echo "============================================="

# Function to check prerequisites
function Check-Prerequisites {
    Write-Host "📋 Checking prerequisites..." -ForegroundColor Cyan
    
    # Check Docker
    try {
        $dockerVersion = docker --version
        Write-Host "✅ Docker: $dockerVersion" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Docker not found. Please install Docker Desktop." -ForegroundColor Red
        exit 1
    }
    
    # Check Docker Compose
    try {
        $composeVersion = docker-compose --version
        Write-Host "✅ Docker Compose: $composeVersion" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Docker Compose not found." -ForegroundColor Red
        exit 1
    }
    
    # Check if ports are available
    $ports = @(8000, 8501, 80)
    foreach ($port in $ports) {
        $connection = Test-NetConnection -ComputerName localhost -Port $port -InformationLevel Quiet
        if ($connection) {
            Write-Host "⚠️ Port $port is already in use" -ForegroundColor Yellow
        } else {
            Write-Host "✅ Port $port is available" -ForegroundColor Green
        }
    }
}

# Function to build and start services
function Start-Services {
    param(
        [string]$Environment = "development"
    )
    
    Write-Host "🏗️ Building and starting services..." -ForegroundColor Cyan
    
    if ($Environment -eq "production") {
        $composeFile = "docker-compose.prod.yml"
    } else {
        $composeFile = "docker-compose.yml"
    }
    
    try {
        # Build services
        Write-Host "Building Docker images..." -ForegroundColor Yellow
        docker-compose -f $composeFile build --no-cache
        
        # Start services
        Write-Host "Starting services..." -ForegroundColor Yellow
        docker-compose -f $composeFile up -d
        
        Write-Host "✅ Services started successfully!" -ForegroundColor Green
        
        # Wait for services to be ready
        Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Yellow
        Start-Sleep -Seconds 30
        
        # Check service health
        Check-ServiceHealth
        
    }
    catch {
        Write-Host "❌ Failed to start services: $_" -ForegroundColor Red
        exit 1
    }
}

# Function to check service health
function Check-ServiceHealth {
    Write-Host "🏥 Checking service health..." -ForegroundColor Cyan
    
    # Check backend health
    try {
        $backendHealth = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 10
        Write-Host "✅ Backend service is healthy" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Backend service is not responding" -ForegroundColor Red
    }
    
    # Check frontend health
    try {
        $frontendResponse = Invoke-WebRequest -Uri "http://localhost:8501" -Method Get -TimeoutSec 10
        if ($frontendResponse.StatusCode -eq 200) {
            Write-Host "✅ Frontend service is healthy" -ForegroundColor Green
        }
    }
    catch {
        Write-Host "❌ Frontend service is not responding" -ForegroundColor Red
    }
}

# Function to stop services
function Stop-Services {
    Write-Host "🛑 Stopping services..." -ForegroundColor Cyan
    
    try {
        docker-compose down
        Write-Host "✅ Services stopped successfully!" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Failed to stop services: $_" -ForegroundColor Red
    }
}

# Function to view logs
function Show-Logs {
    param(
        [string]$Service = ""
    )
    
    if ($Service) {
        docker-compose logs -f $Service
    } else {
        docker-compose logs -f
    }
}

# Function to run tests
function Run-Tests {
    Write-Host "🧪 Running tests..." -ForegroundColor Cyan
    
    # Run backend tests
    Write-Host "Running backend tests..." -ForegroundColor Yellow
    docker-compose exec backend python -m pytest tests/ -v
    
    # Run integration tests
    Write-Host "Running integration tests..." -ForegroundColor Yellow
    python test_milestone1_integration.py
    
    Write-Host "✅ Tests completed!" -ForegroundColor Green
}

# Function to backup data
function Backup-Data {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupDir = "backup_$timestamp"
    
    Write-Host "💾 Creating backup..." -ForegroundColor Cyan
    
    New-Item -ItemType Directory -Path $backupDir -Force
    
    # Backup configuration files
    Copy-Item "docker-compose*.yml" $backupDir -Force
    Copy-Item "nginx" $backupDir -Recurse -Force
    Copy-Item "config" $backupDir -Recurse -Force -ErrorAction SilentlyContinue
    
    # Backup logs
    if (Test-Path "logs") {
        Copy-Item "logs" $backupDir -Recurse -Force
    }
    
    Write-Host "✅ Backup created: $backupDir" -ForegroundColor Green
}

# Function to update application
function Update-Application {
    Write-Host "🔄 Updating application..." -ForegroundColor Cyan
    
    # Create backup first
    Backup-Data
    
    # Pull latest code
    git pull origin main
    
    # Rebuild and restart services
    docker-compose down
    docker-compose build --no-cache
    docker-compose up -d
    
    # Check health
    Start-Sleep -Seconds 30
    Check-ServiceHealth
    
    Write-Host "✅ Application updated successfully!" -ForegroundColor Green
}

# Function to show status
function Show-Status {
    Write-Host "📊 Service Status" -ForegroundColor Cyan
    Write-Host "=================" -ForegroundColor Cyan
    
    # Docker containers status
    docker-compose ps
    
    Write-Host "`n🌐 Service URLs:" -ForegroundColor Cyan
    Write-Host "Frontend: http://localhost:8501" -ForegroundColor Green
    Write-Host "Backend API: http://localhost:8000" -ForegroundColor Green
    Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Green
    Write-Host "Health Check: http://localhost:8000/health" -ForegroundColor Green
}

# Main menu
function Show-Menu {
    Write-Host "`n🔍 Web Content Analyzer - Deployment Menu" -ForegroundColor Cyan
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "1. Check Prerequisites" -ForegroundColor White
    Write-Host "2. Start Services (Development)" -ForegroundColor White
    Write-Host "3. Start Services (Production)" -ForegroundColor White
    Write-Host "4. Stop Services" -ForegroundColor White
    Write-Host "5. Check Service Health" -ForegroundColor White
    Write-Host "6. Show Logs" -ForegroundColor White
    Write-Host "7. Run Tests" -ForegroundColor White
    Write-Host "8. Show Status" -ForegroundColor White
    Write-Host "9. Backup Data" -ForegroundColor White
    Write-Host "10. Update Application" -ForegroundColor White
    Write-Host "0. Exit" -ForegroundColor White
    Write-Host ""
}

# Main execution
if ($args.Count -eq 0) {
    # Interactive mode
    do {
        Show-Menu
        $choice = Read-Host "Select an option (0-10)"
        
        switch ($choice) {
            "1" { Check-Prerequisites }
            "2" { Start-Services -Environment "development" }
            "3" { Start-Services -Environment "production" }
            "4" { Stop-Services }
            "5" { Check-ServiceHealth }
            "6" { 
                $service = Read-Host "Enter service name (or press Enter for all)"
                Show-Logs -Service $service 
            }
            "7" { Run-Tests }
            "8" { Show-Status }
            "9" { Backup-Data }
            "10" { Update-Application }
            "0" { 
                Write-Host "👋 Goodbye!" -ForegroundColor Green
                exit 0 
            }
            default { 
                Write-Host "❌ Invalid option. Please try again." -ForegroundColor Red 
            }
        }
        
        if ($choice -ne "0") {
            Write-Host "`nPress Enter to continue..." -ForegroundColor Yellow
            Read-Host
        }
        
    } while ($choice -ne "0")
} else {
    # Command line mode
    $action = $args[0]
    
    switch ($action) {
        "check" { Check-Prerequisites }
        "start" { Start-Services }
        "start-prod" { Start-Services -Environment "production" }
        "stop" { Stop-Services }
        "health" { Check-ServiceHealth }
        "logs" { Show-Logs }
        "test" { Run-Tests }
        "status" { Show-Status }
        "backup" { Backup-Data }
        "update" { Update-Application }
        default {
            Write-Host "❌ Unknown action: $action" -ForegroundColor Red
            Write-Host "Available actions: check, start, start-prod, stop, health, logs, test, status, backup, update" -ForegroundColor Yellow
            exit 1
        }
    }
}
