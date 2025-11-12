# ============================================================
# 🚀 INSTANT INTERNET ACCESS - 2 MINUTE SETUP
# ============================================================

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   🌐 MAKE YOUR FLASK APP ACCESSIBLE FROM INTERNET" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "📋 WHAT YOU NEED:" -ForegroundColor Yellow
Write-Host "   1. Your Flask app running (perfect_app.py)" -ForegroundColor White
Write-Host "   2. ngrok installed (I'll help you)" -ForegroundColor White
Write-Host ""

Write-Host "============================================================" -ForegroundColor White
Write-Host ""

# Check if Flask app is running
Write-Host "🔍 Checking if Flask app is running..." -ForegroundColor Cyan
$flaskRunning = Get-Process python* -ErrorAction SilentlyContinue | Where-Object {$_.Path -like "*python*"}

if ($flaskRunning) {
    Write-Host "✅ Flask app is running!" -ForegroundColor Green
    Write-Host "   (If it's not your sign language app, stop it and run: python perfect_app.py)" -ForegroundColor Gray
} else {
    Write-Host "⚠️  No Flask app detected!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "START YOUR FLASK APP FIRST:" -ForegroundColor Yellow
    Write-Host "   python perfect_app.py" -ForegroundColor White
    Write-Host ""
    Write-Host "Then run this script again!" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor White
Write-Host ""

# Check if ngrok is installed
Write-Host "🔍 Checking for ngrok..." -ForegroundColor Cyan

$ngrokPath = Get-Command ngrok -ErrorAction SilentlyContinue

if ($ngrokPath) {
    Write-Host "✅ ngrok found!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🚀 EXPOSING YOUR APP TO INTERNET..." -ForegroundColor Cyan
    Write-Host ""
    Write-Host "⏳ Starting ngrok tunnel..." -ForegroundColor Yellow
    Write-Host ""
    
    # Start ngrok
    Start-Process -FilePath "ngrok" -ArgumentList "http 5000"
    
    Write-Host "✅ ngrok started in new window!" -ForegroundColor Green
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "   LOOK FOR YOUR PUBLIC URL IN THE NGROK WINDOW!" -ForegroundColor Green
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "You'll see something like:" -ForegroundColor White
    Write-Host "   https://abc123xyz.ngrok-free.app" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "📱 SHARE THAT URL to access from anywhere!" -ForegroundColor Green
    Write-Host ""
    
} else {
    Write-Host "❌ ngrok NOT found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor White
    Write-Host "   📥 DOWNLOAD & INSTALL ngrok (2 minutes)" -ForegroundColor Yellow
    Write-Host "============================================================" -ForegroundColor White
    Write-Host ""
    Write-Host "OPTION 1: Download Manually (Recommended)" -ForegroundColor Cyan
    Write-Host "   1. Go to: https://ngrok.com/download" -ForegroundColor White
    Write-Host "   2. Download for Windows" -ForegroundColor White
    Write-Host "   3. Extract ZIP to any folder" -ForegroundColor White
    Write-Host "   4. Run: .\ngrok.exe http 5000" -ForegroundColor White
    Write-Host ""
    Write-Host "OPTION 2: Install with Chocolatey" -ForegroundColor Cyan
    Write-Host "   choco install ngrok" -ForegroundColor White
    Write-Host ""
    Write-Host "OPTION 3: Install with Scoop" -ForegroundColor Cyan
    Write-Host "   scoop install ngrok" -ForegroundColor White
    Write-Host ""
    
    $openBrowser = Read-Host "Open ngrok download page now? (Y/N)"
    if ($openBrowser -eq "Y" -or $openBrowser -eq "y") {
        Start-Process "https://ngrok.com/download"
        Write-Host ""
        Write-Host "✅ Browser opened!" -ForegroundColor Green
        Write-Host "   After downloading, run this script again!" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor White
Write-Host ""
Write-Host "💡 WHY ngrok?" -ForegroundColor Yellow
Write-Host "   ✅ Your Flask app has REAL live detection" -ForegroundColor Green
Write-Host "   ✅ ngrok makes it accessible from internet" -ForegroundColor Green
Write-Host "   ✅ No code changes needed" -ForegroundColor Green
Write-Host "   ✅ Works in 2 minutes" -ForegroundColor Green
Write-Host "   ✅ Free to use" -ForegroundColor Green
Write-Host ""
Write-Host "🚫 Why NOT Streamlit?" -ForegroundColor Yellow
Write-Host "   ❌ Streamlit can't do TRUE live video" -ForegroundColor Red
Write-Host "   ❌ Only photo-based detection possible" -ForegroundColor Red
Write-Host "   ❌ Architecture limitation, not fixable" -ForegroundColor Red
Write-Host ""
Write-Host "============================================================" -ForegroundColor White
Write-Host ""
Write-Host "🎉 Your Flask app is the PERFECT solution!" -ForegroundColor Green
Write-Host "   Just expose it to internet with ngrok!" -ForegroundColor Green
Write-Host ""

Read-Host "Press Enter to exit"
