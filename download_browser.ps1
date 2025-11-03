# Download Chromium for Playwright
$url = "https://cdn.playwright.dev/dbazure/download/playwright/builds/chromium/1187/chromium-win64.zip"
$zipPath = "$PSScriptRoot\chromium-win64.zip"
$extractPath = "$PSScriptRoot\browser_data"

Write-Host "Downloading Chromium browser..."

try {
    # Create directory if it doesn't exist
    if (!(Test-Path $extractPath)) {
        New-Item -ItemType Directory -Path $extractPath -Force
    }

    # Download the file
    Invoke-WebRequest -Uri $url -OutFile $zipPath -UseBasicParsing

    Write-Host "Download complete, extracting..."

    # Extract the zip
    Expand-Archive -Path $zipPath -DestinationPath $extractPath -Force

    Write-Host "Chromium extracted successfully!"
    Write-Host "Browser ready! Try running the bot now."

} catch {
    Write-Host "Download failed: $($_.Exception.Message)"
    Write-Host "Manual URL: $url"
}
