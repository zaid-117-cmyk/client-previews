# Load .env file into current process environment if present
if (Test-Path "$PSScriptRoot\.env") {
    Get-Content "$PSScriptRoot\.env" | ForEach-Object {
        $line = $_.Trim()
        if ($line -and -not $line.StartsWith("#") -and $line.Contains("=")) {
            $parts = $line.Split("=", 2)
            [System.Environment]::SetEnvironmentVariable($parts[0].Trim(), $parts[1].Trim().Trim('"').Trim("'"), "Process")
        }
    }
}

Write-Host "AI Auto-Responder Daemon Started!"
Write-Host "Monitoring inbox for $env:EMAIL_USER..."

while ($true) {
    Write-Host "----------------------------------------"
    Write-Host "[$(Get-Date)] Checking for new positive replies..."
    python scripts/auto_responder.py
    Write-Host "Sleeping for 5 minutes..."
    Start-Sleep -Seconds 300
}
