# Create Startup Shortcut for Gmail Automation
# Run this script to add Gmail Automation to Windows Startup

$batchPath = Join-Path $PSScriptRoot "start_gmail_automation.bat"
$startupFolder = [Environment]::GetFolderPath("Startup")
$shortcutPath = Join-Path $startupFolder "Gmail Automation.lnk"

$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($shortcutPath)
$Shortcut.TargetPath = $batchPath
$Shortcut.WorkingDirectory = $PSScriptRoot
$Shortcut.Description = "Start Gmail Automation on Windows Login"
$Shortcut.Save()

Write-Host "✅ Gmail Automation shortcut created in Startup folder!" -ForegroundColor Green
Write-Host "📍 Location: $shortcutPath" -ForegroundColor Cyan
Write-Host "🚀 Automation will start automatically on Windows login!" -ForegroundColor Green
