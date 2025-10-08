# Project Organization Script for Financial Intelligence Platform
# This script organizes the project structure by moving files to appropriate directories

Write-Host "=== Financial Intelligence Platform - Project Organization ===" -ForegroundColor Cyan
Write-Host ""

# Get project root
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

Write-Host "Project Root: $ProjectRoot" -ForegroundColor Yellow
Write-Host ""

# Create necessary directories
Write-Host "[1/5] Creating directory structure..." -ForegroundColor Green
$directories = @("scripts", "tests_archive", "setup", "logs")
foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  ✓ Created $dir/" -ForegroundColor Gray
    } else {
        Write-Host "  ✓ $dir/ already exists" -ForegroundColor Gray
    }
}
Write-Host ""

# Move setup executables
Write-Host "[2/5] Moving setup files..." -ForegroundColor Green
if (Test-Path "OllamaSetup.exe") {
    Move-Item "OllamaSetup.exe" "setup/OllamaSetup.exe" -Force
    Write-Host "  ✓ Moved OllamaSetup.exe to setup/" -ForegroundColor Gray
}
Write-Host ""

# Move startup scripts
Write-Host "[3/5] Organizing startup scripts..." -ForegroundColor Green
$startupScripts = @(
    "start_advanced_api.py",
    "start_advanced_streamlit.py",
    "start_system.py",
    "run_demo.py",
    "setup_sebi_directory.py"
)

foreach ($script in $startupScripts) {
    if (Test-Path $script) {
        Copy-Item $script "scripts/$script" -Force
        Write-Host "  ✓ Copied $script to scripts/" -ForegroundColor Gray
    }
}
Write-Host ""

# Archive redundant test files
Write-Host "[4/5] Archiving redundant test files..." -ForegroundColor Green
$redundantTests = @(
    "test_api_connection.py",
    "test_minimal_api.py",
    "test_model_loading.py",
    "test_data_pipeline.py",
    "test_sebi_file_processing.py"
)

foreach ($test in $redundantTests) {
    if (Test-Path $test) {
        Move-Item $test "tests_archive/$test" -Force
        Write-Host "  ✓ Archived $test" -ForegroundColor Gray
    }
}
Write-Host ""

# Keep essential test files
Write-Host "[5/5] Essential test files (kept in root):" -ForegroundColor Green
$essentialTests = @(
    "test_advanced_rag.py",
    "test_advanced_api.py",
    "test_complete_sebi_pipeline.py",
    "test_ollama_integration.py"
)

foreach ($test in $essentialTests) {
    if (Test-Path $test) {
        Write-Host "  ✓ Keeping $test" -ForegroundColor Gray
    }
}
Write-Host ""

Write-Host "=== Project Organization Complete! ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Review the organized structure"
Write-Host "  2. Delete test files from root if archiving is confirmed"
Write-Host "  3. Use scripts/start_system.ps1 for launching the platform"
Write-Host ""

