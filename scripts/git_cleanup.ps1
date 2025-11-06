# Git Cleanup Script for Finance Fraud Project
# Run this from the project root directory

Write-Host "=" * 70
Write-Host "GIT REPOSITORY CLEANUP"
Write-Host "=" * 70

# Check if we're in the right directory
$projectFiles = @("src", "scripts", "data", "models")
$isProjectDir = $true
foreach ($file in $projectFiles) {
    if (-not (Test-Path $file)) {
        $isProjectDir = $false
        break
    }
}

if (-not $isProjectDir) {
    Write-Host "[ERROR] Not in project directory!"
    Write-Host "Please run this from: C:\Users\CL502_05\Downloads\Finance Fraud"
    exit 1
}

Write-Host "[OK] In project directory"
Write-Host ""

# Step 1: Remove models from Git tracking
Write-Host "[1/5] Removing models from Git tracking..."
git rm -r --cached models/ 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  [OK] Models removed from Git tracking"
} else {
    Write-Host "  [INFO] Models not in Git (already excluded)"
}
Write-Host ""

# Step 2: Verify .gitignore
Write-Host "[2/5] Verifying .gitignore..."
$gitignoreContent = Get-Content .gitignore -Raw -ErrorAction SilentlyContinue

if (-not $gitignoreContent) {
    Write-Host "  [WARNING] .gitignore not found, creating..."
    New-Item .gitignore -ItemType File
    $gitignoreContent = ""
}

# Check if model exclusions exist
$needsUpdate = $false
if ($gitignoreContent -notmatch "safetensors") {
    Write-Host "  [FIX] Adding *.safetensors to .gitignore"
    Add-Content .gitignore "`n# Model files (large)`n*.safetensors`n"
    $needsUpdate = $true
}

if ($gitignoreContent -notmatch "models/fin-e5/") {
    Write-Host "  [FIX] Adding models/fin-e5/ to .gitignore"
    Add-Content .gitignore "`n# Fine-tuned models (too large for Git)`nmodels/fin-e5/`nmodels/deployed/`n"
    $needsUpdate = $true
}

if ($needsUpdate) {
    Write-Host "  [OK] .gitignore updated"
} else {
    Write-Host "  [OK] .gitignore already has model exclusions"
}
Write-Host ""

# Step 3: Check Git status
Write-Host "[3/5] Checking Git status..."
$status = git status --short 2>$null
$hasModels = $status | Select-String "models/"

if ($hasModels) {
    Write-Host "  [WARNING] Models still showing in Git status!"
    Write-Host "  Run: git rm -r --cached models/"
} else {
    Write-Host "  [OK] Models excluded from Git"
}
Write-Host ""

# Step 4: Stage changes
Write-Host "[4/5] Staging .gitignore changes..."
git add .gitignore 2>$null
Write-Host "  [OK] .gitignore staged"
Write-Host ""

# Step 5: Check remote
Write-Host "[5/5] Checking remote configuration..."
$remote = git remote -v 2>$null

if ($remote) {
    Write-Host "  [OK] Remote configured:"
    Write-Host $remote
} else {
    Write-Host "  [INFO] No remote configured"
    Write-Host "  To add remote: git remote add origin https://github.com/Ranveersingh1113/Finance-Fraud.git"
}
Write-Host ""

Write-Host "=" * 70
Write-Host "CLEANUP COMPLETE"
Write-Host "=" * 70
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Review changes: git status"
Write-Host "2. Commit: git commit -m 'Exclude model files from Git'"
Write-Host "3. Push: git push origin master (or main)"
Write-Host ""
Write-Host "To verify models are excluded:"
Write-Host "  git check-ignore models/fin-e5/model.safetensors"
Write-Host ""

