# Setup Environment Variables
#
# This script copies the example environment files to their corresponding .env files
# for both the root directory, backend, and frontend, if they don't already exist.
#
# Usage: ./scripts/setup/setup_env.ps1 [environment]
# environment: development (default), test, or production

param (
    [string]$Environment = "development"
)

Write-Host "Setting up environment variables for $Environment environment..." -ForegroundColor Green

# Define the environment file suffix based on the environment
$EnvSuffix = ""
if ($Environment -eq "test") {
    $EnvSuffix = ".test"
} elseif ($Environment -eq "production") {
    $EnvSuffix = ".production"
}

# Function to copy example env file if target doesn't exist
function Copy-EnvFile {
    param (
        [string]$SourceFile,
        [string]$TargetFile
    )

    if (Test-Path $TargetFile) {
        Write-Host "File already exists: $TargetFile" -ForegroundColor Yellow
    } else {
        try {
            Copy-Item -Path $SourceFile -Destination $TargetFile -Force
            Write-Host "Created: $TargetFile" -ForegroundColor Green
        } catch {
            Write-Host "Error creating $TargetFile. Please check file permissions and try again." -ForegroundColor Red
        }
    }
}

# Root directory environment files
$RootEnvExample = ".env.example"
$RootEnvTarget = ".env$EnvSuffix"
Copy-EnvFile -SourceFile $RootEnvExample -TargetFile $RootEnvTarget

# Backend environment files
$BackendEnvExample = "backend/.env.example"
$BackendEnvTarget = "backend/.env$EnvSuffix"
Copy-EnvFile -SourceFile $BackendEnvExample -TargetFile $BackendEnvTarget

# Frontend environment files
$FrontendEnvExample = "frontend/.env.example"
$FrontendEnvTarget = "frontend/.env$EnvSuffix"
Copy-EnvFile -SourceFile $FrontendEnvExample -TargetFile $FrontendEnvTarget

Write-Host "Environment setup complete!" -ForegroundColor Green
Write-Host "IMPORTANT: Make sure to update the created .env files with your actual configuration values." -ForegroundColor Yellow 