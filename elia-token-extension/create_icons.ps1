# PowerShell Script to Create Extension Icons
# Creates 3 PNG icons with Vidéotron branding

Write-Host "🎨 Creating Elia Token Manager Icons..." -ForegroundColor Cyan

# Check if icons directory exists
$iconsDir = Join-Path $PSScriptRoot "icons"
if (-not (Test-Path $iconsDir)) {
    New-Item -ItemType Directory -Path $iconsDir | Out-Null
    Write-Host "✅ Created icons directory" -ForegroundColor Green
}

# Function to create icon using .NET
function Create-Icon {
    param (
        [int]$Size,
        [string]$OutputPath
    )
    
    Add-Type -AssemblyName System.Drawing
    
    # Create bitmap
    $bitmap = New-Object System.Drawing.Bitmap($Size, $Size)
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    $graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $graphics.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAlias
    
    # Background - Vidéotron yellow
    $yellowBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(255, 255, 210, 0))
    $graphics.FillRectangle($yellowBrush, 0, 0, $Size, $Size)
    
    # Draw "E" letter
    $blackBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(255, 2, 4, 1))
    $fontSize = [int]($Size * 0.6)
    $font = New-Object System.Drawing.Font("Arial", $fontSize, [System.Drawing.FontStyle]::Bold)
    
    # Center text
    $format = New-Object System.Drawing.StringFormat
    $format.Alignment = [System.Drawing.StringAlignment]::Center
    $format.LineAlignment = [System.Drawing.StringAlignment]::Center
    
    $rect = New-Object System.Drawing.RectangleF(0, 0, $Size, $Size)
    $graphics.DrawString("E", $font, $blackBrush, $rect, $format)
    
    # Save
    $bitmap.Save($OutputPath, [System.Drawing.Imaging.ImageFormat]::Png)
    
    # Cleanup
    $graphics.Dispose()
    $bitmap.Dispose()
    $yellowBrush.Dispose()
    $blackBrush.Dispose()
    $font.Dispose()
    
    Write-Host "✅ Created $OutputPath" -ForegroundColor Green
}

# Create icons
try {
    Create-Icon -Size 16 -OutputPath (Join-Path $iconsDir "icon16.png")
    Create-Icon -Size 48 -OutputPath (Join-Path $iconsDir "icon48.png")
    Create-Icon -Size 128 -OutputPath (Join-Path $iconsDir "icon128.png")
    
    Write-Host ""
    Write-Host "🎉 All icons created successfully!" -ForegroundColor Green
    Write-Host "📁 Location: $iconsDir" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "✅ You can now proceed to Step 2: Load Extension" -ForegroundColor Yellow
    Write-Host "   1. Open Chrome: chrome://extensions/" -ForegroundColor White
    Write-Host "   2. Enable Developer mode" -ForegroundColor White
    Write-Host "   3. Click 'Load unpacked'" -ForegroundColor White
    Write-Host "   4. Select: elia-token-extension folder" -ForegroundColor White
    Write-Host ""
}
catch {
    Write-Host "❌ Error creating icons: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "📋 Alternative: Open create_icons.html in browser" -ForegroundColor Yellow
    Write-Host "   1. Open: elia-token-extension/create_icons.html" -ForegroundColor White
    Write-Host "   2. Click 'Download All Icons'" -ForegroundColor White
    Write-Host "   3. Move files to icons folder" -ForegroundColor White
}
