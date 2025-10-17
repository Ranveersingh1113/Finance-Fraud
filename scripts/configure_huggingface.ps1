# Configure HuggingFace to use local model cache
# This script sets up environment variables for HuggingFace models

Write-Host "🔧 HuggingFace Local Cache Configuration" -ForegroundColor Cyan
Write-Host "=" * 60

$CachePath = "D:\huggingface_cache"

# Check if cache directory exists
if (Test-Path $CachePath) {
    Write-Host "✅ Found HuggingFace cache at: $CachePath" -ForegroundColor Green
    
    # List models in cache
    $modelsPath = Join-Path $CachePath "models--BAAI--bge-reranker-large"
    if (Test-Path $modelsPath) {
        Write-Host "✅ Found BGE Reranker Large model" -ForegroundColor Green
        
        # Check snapshots
        $snapshotsPath = Join-Path $modelsPath "snapshots"
        if (Test-Path $snapshotsPath) {
            $snapshots = Get-ChildItem $snapshotsPath -Directory
            if ($snapshots.Count -gt 0) {
                Write-Host "✅ Model snapshots found: $($snapshots.Count)" -ForegroundColor Green
            } else {
                Write-Host "⚠️  No model snapshots found - model may be incomplete" -ForegroundColor Yellow
            }
        }
    } else {
        Write-Host "⚠️  BGE Reranker model not found in cache" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ Cache directory not found: $CachePath" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Setting environment variables..." -ForegroundColor Yellow

# Set environment variables for current session
$env:HF_HOME = $CachePath
$env:TRANSFORMERS_CACHE = $CachePath
$env:HF_DATASETS_CACHE = $CachePath

Write-Host "✅ Environment variables set for current session:" -ForegroundColor Green
Write-Host "   HF_HOME = $env:HF_HOME" -ForegroundColor Gray
Write-Host "   TRANSFORMERS_CACHE = $env:TRANSFORMERS_CACHE" -ForegroundColor Gray

Write-Host ""
Write-Host "To make this permanent, add to your system environment variables:" -ForegroundColor Yellow
Write-Host "   1. Open System Properties > Environment Variables" -ForegroundColor Gray
Write-Host "   2. Add User Variable:" -ForegroundColor Gray
Write-Host "      Name: HF_HOME" -ForegroundColor Gray
Write-Host "      Value: $CachePath" -ForegroundColor Gray
Write-Host "   3. Add User Variable:" -ForegroundColor Gray
Write-Host "      Name: TRANSFORMERS_CACHE" -ForegroundColor Gray
Write-Host "      Value: $CachePath" -ForegroundColor Gray

Write-Host ""
Write-Host "Or add to your PowerShell profile for persistence:" -ForegroundColor Yellow
Write-Host @"
   # Add these lines to: $PROFILE
   `$env:HF_HOME = '$CachePath'
   `$env:TRANSFORMERS_CACHE = '$CachePath'
"@ -ForegroundColor Gray

Write-Host ""
Write-Host "=" * 60
Write-Host "✅ Configuration complete!" -ForegroundColor Green
Write-Host "   Restart your API server for changes to take effect" -ForegroundColor Yellow

