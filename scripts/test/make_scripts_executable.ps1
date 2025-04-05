# Set scripts to executable on Windows

$scripts = @(
    "scripts/test/run_backend_tests.py",
    "scripts/test/run_frontend_tests.py",
    "scripts/test/run_integration_tests.py",
    "scripts/test/run_all_tests.py"
)

foreach ($script in $scripts) {
    Write-Host "Setting $script as executable..."
    
    # Add Python shebang line if not present
    $content = Get-Content $script -Raw
    if (-not $content.StartsWith("#!/usr/bin/env python")) {
        $content = "#!/usr/bin/env python`n" + $content
        Set-Content $script $content -NoNewline
    }
    
    # Create a .bat wrapper for each Python script
    $batFile = $script.Replace(".py", ".bat")
    @"
@echo off
python "%~dp0\$(Split-Path $script -Leaf)" %*
"@ | Set-Content $batFile -NoNewline
    
    Write-Host "Created batch wrapper at $batFile"
}

Write-Host "All scripts are now executable. Use the .bat files to run them on Windows." 