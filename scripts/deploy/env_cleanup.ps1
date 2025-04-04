#!/usr/bin/env pwsh
# This script checks for and standardizes environment files
# Ensures .env files follow the structure defined in docs/setup/environment.md

# Usage: ./scripts/deploy/env_cleanup.ps1

Write-Host "========================================"
Write-Host "Environment Cleanup Check"
Write-Host "========================================"

# Check for .env.example files
$missingFiles = @()

$envExampleFiles = @(
    ".env.example",
    "backend/.env.example",
    "frontend/.env.example"
)

foreach ($file in $envExampleFiles) {
    if (-not (Test-Path $file)) {
        $missingFiles += $file
    }
}

if ($missingFiles.Count -gt 0) {
    Write-Host "`nWARNING: The following .env.example files are missing:" -ForegroundColor Yellow
    foreach ($file in $missingFiles) {
        Write-Host " - $file" -ForegroundColor Yellow
    }
    Write-Host "`nPlease create them based on the documentation in docs/setup/environment.md" -ForegroundColor Yellow
}

# Check for environment files that should not be committed
$shouldCheck = $false

$localEnvFiles = @(
    # Root level
    ".env",
    ".env.test",
    ".env.production",
    
    # Backend level
    "backend/.env",
    "backend/.env.test",
    "backend/.env.production",
    
    # Frontend level
    "frontend/.env",
    "frontend/.env.test",
    "frontend/.env.production"
)

$existingLocalFiles = @()

foreach ($file in $localEnvFiles) {
    if (Test-Path $file) {
        $existingLocalFiles += $file
        $shouldCheck = $true
    }
}

if ($shouldCheck) {
    Write-Host "`nNOTE: The following environment files exist locally:" -ForegroundColor Cyan
    foreach ($file in $existingLocalFiles) {
        Write-Host " - $file" -ForegroundColor Cyan
    }
    Write-Host "`nThese files should NOT be committed to Git." -ForegroundColor Cyan
    Write-Host "Run 'git check-ignore <file>' to confirm they are ignored." -ForegroundColor Cyan
}

# Validate environment files against examples (check for missing variables)
Write-Host "`n========================================"
Write-Host "Validating environment files"
Write-Host "========================================`n"

function Get-EnvVars {
    param (
        [string]$FilePath
    )
    
    if (-not (Test-Path $FilePath)) {
        return @()
    }
    
    $content = Get-Content $FilePath
    $vars = @()
    
    foreach ($line in $content) {
        # Skip comments and empty lines
        if ($line -match '^\s*#' -or $line -match '^\s*$') {
            continue
        }
        
        # Extract variable name
        if ($line -match '^\s*([A-Za-z0-9_]+)=') {
            $vars += $Matches[1]
        }
    }
    
    return $vars
}

$filePairs = @(
    @{Example = ".env.example"; Actual = ".env"},
    @{Example = ".env.example"; Actual = ".env.test"},
    @{Example = ".env.example"; Actual = ".env.production"},
    @{Example = "backend/.env.example"; Actual = "backend/.env"},
    @{Example = "backend/.env.example"; Actual = "backend/.env.test"},
    @{Example = "backend/.env.example"; Actual = "backend/.env.production"},
    @{Example = "frontend/.env.example"; Actual = "frontend/.env"},
    @{Example = "frontend/.env.example"; Actual = "frontend/.env.test"},
    @{Example = "frontend/.env.example"; Actual = "frontend/.env.production"}
)

$foundIssues = $false

foreach ($pair in $filePairs) {
    if ((Test-Path $pair.Example) -and (Test-Path $pair.Actual)) {
        $exampleVars = Get-EnvVars -FilePath $pair.Example
        $actualVars = Get-EnvVars -FilePath $pair.Actual
        
        $missingVars = $exampleVars | Where-Object { $_ -notin $actualVars }
        
        if ($missingVars.Count -gt 0) {
            $foundIssues = $true
            Write-Host "Variables missing in $($pair.Actual) (from $($pair.Example)):" -ForegroundColor Yellow
            foreach ($var in $missingVars) {
                Write-Host " - $var" -ForegroundColor Yellow
            }
            Write-Host ""
        }
    }
}

if (-not $foundIssues) {
    Write-Host "All environment files contain the required variables.`n" -ForegroundColor Green
}

Write-Host "Environment cleanup check complete."
Write-Host "========================================" 