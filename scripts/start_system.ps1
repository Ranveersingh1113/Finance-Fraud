# Financial Intelligence Platform - Unified System Launcher
# Starts both the Advanced API Server and Streamlit Frontend

param(
    [switch]$ApiOnly,
    [switch]$FrontendOnly,
    [switch]$Help
)

if ($Help) {
    Write-Host @"
Financial Intelligence Platform - System Launcher

Usage:
  .\start_system.ps1           Start both API and Frontend
  .\start_system.ps1 -ApiOnly  Start only the API server
  .\start_system.ps1 -FrontendOnly  Start only the Frontend (requires API to be running)

Options:
  -ApiOnly        Start only the Advanced API server on port 8001
  -FrontendOnly   Start only the Streamlit frontend on port 8501  
  -Help           Show this help message

Requirements:
  - Python virtual environment activated (financevenv)
  - Ollama running locally (http://localhost:11434)
  - All dependencies installed (pip install -r requirements.txt)

"@
    exit 0
}

# Get project root (parent of scripts directory)
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  Financial Intelligence Platform" -ForegroundColor Cyan
Write-Host "  Advanced RAG System for Fraud Detection" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment is activated
if (-not $env:VIRTUAL_ENV) {
    Write-Host "⚠️  Warning: Virtual environment not detected" -ForegroundColor Yellow
    Write-Host "   Attempting to activate financevenv..." -ForegroundColor Yellow
    
    if (Test-Path ".\financevenv\Scripts\Activate.ps1") {
        & ".\financevenv\Scripts\Activate.ps1"
        Write-Host "✓ Virtual environment activated" -ForegroundColor Green
    } else {
        Write-Host "❌ Error: Virtual environment not found" -ForegroundColor Red
        Write-Host "   Please run: python -m venv financevenv" -ForegroundColor Red
        exit 1
    }
}
Write-Host ""

# Check Python
$pythonVersion = python --version 2>&1
Write-Host "🐍 Python: $pythonVersion" -ForegroundColor Gray

# Check Ollama
Write-Host "🦙 Checking Ollama..." -ForegroundColor Gray
try {
    $ollamaCheck = curl -s http://localhost:11434/api/tags 2>&1
    Write-Host "✓ Ollama is running" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Warning: Ollama may not be running" -ForegroundColor Yellow
    Write-Host "   Start Ollama before running queries" -ForegroundColor Yellow
}
Write-Host ""

# Start API Server
if (-not $FrontendOnly) {
    Write-Host "🚀 Starting Advanced API Server..." -ForegroundColor Green
    Write-Host "   Port: 8001" -ForegroundColor Gray
    Write-Host "   Docs: http://localhost:8001/docs" -ForegroundColor Gray
    
    $apiJob = Start-Job -ScriptBlock {
        param($root)
        Set-Location $root
        python start_advanced_api.py
    } -ArgumentList $ProjectRoot
    
    Write-Host "✓ API Server started (Job ID: $($apiJob.Id))" -ForegroundColor Green
    Start-Sleep -Seconds 5
}
Write-Host ""

# Start Streamlit Frontend
if (-not $ApiOnly) {
    Write-Host "🎨 Starting Streamlit Frontend..." -ForegroundColor Green
    Write-Host "   Port: 8501" -ForegroundColor Gray
    Write-Host "   URL: http://localhost:8501" -ForegroundColor Gray
    
    $frontendJob = Start-Job -ScriptBlock {
        param($root)
        Set-Location $root
        python start_advanced_streamlit.py
    } -ArgumentList $ProjectRoot
    
    Write-Host "✓ Frontend started (Job ID: $($frontendJob.Id))" -ForegroundColor Green
    Start-Sleep -Seconds 3
}
Write-Host ""

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "✅ System Started Successfully!" -ForegroundColor Green
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

if (-not $FrontendOnly) {
    Write-Host "📊 API Server:    http://localhost:8001" -ForegroundColor White
    Write-Host "📚 API Docs:      http://localhost:8001/docs" -ForegroundColor White
}
if (-not $ApiOnly) {
    Write-Host "🕵️  Analyst UI:    http://localhost:8501" -ForegroundColor White
}
Write-Host ""
Write-Host "Press Ctrl+C to stop all services" -ForegroundColor Yellow
Write-Host ""

# Monitor jobs
try {
    while ($true) {
        Start-Sleep -Seconds 1
        
        # Check if jobs are still running
        if ($apiJob -and (Get-Job -Id $apiJob.Id).State -ne "Running") {
            Write-Host "❌ API Server stopped unexpectedly" -ForegroundColor Red
            break
        }
        if ($frontendJob -and (Get-Job -Id $frontendJob.Id).State -ne "Running") {
            Write-Host "❌ Frontend stopped unexpectedly" -ForegroundColor Red
            break
        }
    }
} finally {
    Write-Host ""
    Write-Host "🛑 Shutting down services..." -ForegroundColor Yellow
    
    # Stop all jobs
    if ($apiJob) {
        Stop-Job -Id $apiJob.Id -ErrorAction SilentlyContinue
        Remove-Job -Id $apiJob.Id -Force -ErrorAction SilentlyContinue
    }
    if ($frontendJob) {
        Stop-Job -Id $frontendJob.Id -ErrorAction SilentlyContinue
        Remove-Job -Id $frontendJob.Id -Force -ErrorAction SilentlyContinue
    }
    
    Write-Host "✅ All services stopped" -ForegroundColor Green
}

