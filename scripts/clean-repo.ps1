# PowerShell script to remove large files from Git history
Write-Host "Starting repository cleaning process..." -ForegroundColor Green

# Create a fresh clone to work with
$repoUrl = git config --get remote.origin.url
$tempDir = "C:\Temp\manobal-temp"
Write-Host "Creating temporary clone in $tempDir..." -ForegroundColor Yellow

if (Test-Path $tempDir) {
    Remove-Item -Recurse -Force $tempDir
}
New-Item -ItemType Directory -Path $tempDir | Out-Null

# Clone the repository (shallow clone to speed things up)
cd $tempDir
git clone --depth 1 $repoUrl .

# Create a proper .gitignore file
$gitignoreContent = @"
# Dependencies
node_modules/
*/node_modules/
**/node_modules/
__pycache__/
*.py[cod]
*$py.class
venv/
env/
ENV/
.env
.venv
env.bak/
venv.bak/
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Next.js build outputs
.next/
out/
*.tsbuildinfo

# Logs and debugging
logs/
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.pnpm-debug.log*
.DS_Store
*.pem
*.swp

# Testing and coverage
coverage/
.coverage
htmlcov/
.pytest_cache/
.benchmarks/

# Local environment
.env.local
.env.development.local
.env.test.local
.env.production.local

# IDE specific files
.idea/
.vscode/
*.suo
*.ntvs*
*.njsproj
*.sln
*.sw?

# Flask specific
instance/
.webassets-cache
.env

# Certificates
*.key
*.crt
*.cert
*.pem

# Large files
*.node
*.msvc
*.so
*.dylib
*.dll
*.whl

# Build files
**/build/
build/

# MongoDB binaries
.cache/mongodb-binaries/
**/mongodb-memory-server/
"@

Set-Content -Path ".gitignore" -Value $gitignoreContent

# Add all current files but respect the new .gitignore
git add .
git commit -m "Fresh start with proper .gitignore"

# Push with force to update the repository
git push -f origin main

Write-Host "Repository cleaned and updated successfully!" -ForegroundColor Green
Write-Host "Please go back to your original repository folder and run 'git pull origin main' to update your local copy." -ForegroundColor Yellow 