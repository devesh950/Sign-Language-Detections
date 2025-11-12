# Start Perfect App with Improved Accuracy
# Keep running in background

Write-Host ""
Write-Host ("="*80) -ForegroundColor Cyan
Write-Host "🚀 STARTING IMPROVED SIGN LANGUAGE APP..." -ForegroundColor Green
Write-Host ("="*80) -ForegroundColor Cyan
Write-Host ""

# Start in background
Start-Process -FilePath "C:/Users/deves/AppData/Local/Microsoft/WindowsApps/python3.12.exe" `
    -ArgumentList "perfect_app.py" `
    -WorkingDirectory "C:\Users\deves\OneDrive\Desktop\sign_language_project_empty" `
    -WindowStyle Hidden

Start-Sleep -Seconds 8

Write-Host ""
Write-Host ("="*80) -ForegroundColor Cyan
Write-Host "✅ APP IS NOW RUNNING WITH IMPROVED ACCURACY!" -ForegroundColor Green
Write-Host ("="*80) -ForegroundColor Cyan
Write-Host ""
Write-Host "🎯 ACCURACY IMPROVEMENTS:" -ForegroundColor Yellow
Write-Host "   ✅ Confidence threshold: 80% (was 70%)" -ForegroundColor White
Write-Host "   ✅ Better hand tracking: 70% minimum" -ForegroundColor White
Write-Host "   ✅ Faster processing: Every 2nd frame" -ForegroundColor White
Write-Host "   ✅ Shows 'uncertain' for 60-79% confidence" -ForegroundColor White
Write-Host ""
Write-Host "📱 OPEN IN YOUR BROWSER:" -ForegroundColor Yellow
Write-Host ""
Write-Host "   From computer: " -NoNewline
Write-Host "http://localhost:5000" -ForegroundColor Cyan -BackgroundColor Black
Write-Host ""
Write-Host "   From phone:    " -NoNewline
Write-Host "http://192.168.88.119:5000" -ForegroundColor Cyan -BackgroundColor Black
Write-Host ""
Write-Host ""
Write-Host "💡 TIPS FOR ACCURATE DETECTION:" -ForegroundColor Yellow
Write-Host "   1. ☀️  Good lighting (face a light source)" -ForegroundColor White
Write-Host "   2. 📏 Keep hand 30-60cm from camera" -ForegroundColor White
Write-Host "   3. ✋ Show FULL hand clearly" -ForegroundColor White
Write-Host "   4. ⏸️  Hold gesture STEADY 1-2 seconds" -ForegroundColor White
Write-Host "   5. 🎯 Make CLEAR, DISTINCT gestures" -ForegroundColor White
Write-Host "   6. 🏞️  Use plain background" -ForegroundColor White
Write-Host ""
Write-Host "📊 CONFIDENCE LEVELS:" -ForegroundColor Yellow
Write-Host "   • 80-100% = ✅ ACCURATE (voice speaks)" -ForegroundColor Green
Write-Host "   • 60-79%  = ⚠️  UNCERTAIN (shown only)" -ForegroundColor Yellow
Write-Host "   • 0-59%   = ❌ TOO LOW (not shown)" -ForegroundColor Red
Write-Host ""
Write-Host ("="*80) -ForegroundColor Cyan
Write-Host ""
Write-Host "📖 Read ACCURACY_GUIDE.txt for more tips!" -ForegroundColor Gray
Write-Host ""
Write-Host "Press Ctrl+C to exit this window (app keeps running)" -ForegroundColor Gray
Write-Host ""

# Keep window open
Read-Host "Press Enter to close this window"
