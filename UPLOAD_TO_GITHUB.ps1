# GitHub Upload Helper Script
# This script will guide you through uploading your project to GitHub

Write-Host ""
Write-Host ("="*80) -ForegroundColor Cyan
Write-Host "🚀 GITHUB UPLOAD HELPER" -ForegroundColor Yellow
Write-Host ("="*80) -ForegroundColor Cyan
Write-Host ""

# Check if Git is installed
$gitInstalled = $null -ne (Get-Command git -ErrorAction SilentlyContinue)

if (-not $gitInstalled) {
    Write-Host "❌ Git is not installed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "📥 Please install Git first:" -ForegroundColor Yellow
    Write-Host "   1. Visit: https://git-scm.com/downloads" -ForegroundColor White
    Write-Host "   2. Download and install Git" -ForegroundColor White
    Write-Host "   3. Restart PowerShell" -ForegroundColor White
    Write-Host "   4. Run this script again" -ForegroundColor White
    Write-Host ""
    Write-Host "OR use GitHub Desktop (easier):" -ForegroundColor Yellow
    Write-Host "   1. Visit: https://desktop.github.com/" -ForegroundColor White
    Write-Host "   2. Download and install" -ForegroundColor White
    Write-Host "   3. Follow GUI instructions" -ForegroundColor White
    Write-Host ""
    Write-Host "OR upload via website (simplest):" -ForegroundColor Yellow
    Write-Host "   See: GITHUB_UPLOAD_GUIDE.md" -ForegroundColor White
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit
}

Write-Host "✅ Git is installed!" -ForegroundColor Green
Write-Host ""

# Check model file size
$modelPath = "C:\Users\deves\OneDrive\Desktop\sign_language_project_empty\sign_model.h5"
if (Test-Path $modelPath) {
    $sizeMB = [math]::Round((Get-Item $modelPath).Length/1MB, 2)
    Write-Host "📊 Model file size: $sizeMB MB" -ForegroundColor Cyan
    
    if ($sizeMB -gt 100) {
        Write-Host "⚠️  WARNING: Model file is too large for GitHub!" -ForegroundColor Red
        Write-Host "   You'll need to use Git LFS" -ForegroundColor Yellow
        Write-Host ""
    }
}

Write-Host ""
Write-Host ("─"*80) -ForegroundColor Gray
Write-Host "📝 STEP 1: CREATE GITHUB ACCOUNT (if you don't have one)" -ForegroundColor Yellow
Write-Host ("─"*80) -ForegroundColor Gray
Write-Host ""
Write-Host "   1. Visit: https://github.com/signup" -ForegroundColor White
Write-Host "   2. Create your account" -ForegroundColor White
Write-Host "   3. Verify your email" -ForegroundColor White
Write-Host ""

$hasAccount = Read-Host "Do you have a GitHub account? (y/n)"

if ($hasAccount -ne 'y') {
    Write-Host ""
    Write-Host "Please create a GitHub account first, then run this script again." -ForegroundColor Yellow
    Write-Host ""
    Start-Process "https://github.com/signup"
    Read-Host "Press Enter to exit"
    exit
}

Write-Host ""
Write-Host ("─"*80) -ForegroundColor Gray
Write-Host "📝 STEP 2: CREATE NEW REPOSITORY ON GITHUB" -ForegroundColor Yellow
Write-Host ("─"*80) -ForegroundColor Gray
Write-Host ""
Write-Host "   1. Opening GitHub in your browser..." -ForegroundColor White
Start-Process "https://github.com/new"
Write-Host ""
Write-Host "   2. Fill in the form:" -ForegroundColor White
Write-Host "      • Repository name: sign-language-detection" -ForegroundColor Cyan
Write-Host "      • Description: Real-time sign language detection using AI" -ForegroundColor Cyan
Write-Host "      • Public: ✓ (IMPORTANT for free Streamlit)" -ForegroundColor Cyan
Write-Host "      • DON'T add README, .gitignore, or license (you have these)" -ForegroundColor Cyan
Write-Host ""
Write-Host "   3. Click 'Create repository'" -ForegroundColor White
Write-Host ""

Read-Host "Press Enter after you've created the repository"

Write-Host ""
$username = Read-Host "Enter your GitHub username"

if ([string]::IsNullOrWhiteSpace($username)) {
    Write-Host "❌ Username cannot be empty!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit
}

Write-Host ""
Write-Host ("─"*80) -ForegroundColor Gray
Write-Host "📝 STEP 3: CONFIGURE GIT" -ForegroundColor Yellow
Write-Host ("─"*80) -ForegroundColor Gray
Write-Host ""

$name = Read-Host "Enter your full name (for Git commits)"
$email = Read-Host "Enter your email (used for GitHub)"

Write-Host ""
Write-Host "Setting up Git configuration..." -ForegroundColor Cyan

git config --global user.name "$name"
git config --global user.email "$email"

Write-Host "✅ Git configured!" -ForegroundColor Green

Write-Host ""
Write-Host ("─"*80) -ForegroundColor Gray
Write-Host "📝 STEP 4: INITIALIZE AND UPLOAD" -ForegroundColor Yellow
Write-Host ("─"*80) -ForegroundColor Gray
Write-Host ""

$projectPath = "C:\Users\deves\OneDrive\Desktop\sign_language_project_empty"
Set-Location $projectPath

Write-Host "📂 Working directory: $projectPath" -ForegroundColor Cyan
Write-Host ""

Write-Host "🔄 Initializing Git repository..." -ForegroundColor Cyan
git init

Write-Host "✅ Git initialized!" -ForegroundColor Green
Write-Host ""

Write-Host "📦 Adding all files..." -ForegroundColor Cyan
git add .

Write-Host "✅ Files added!" -ForegroundColor Green
Write-Host ""

Write-Host "💾 Creating commit..." -ForegroundColor Cyan
git commit -m "Initial commit: Sign language detection app"

Write-Host "✅ Commit created!" -ForegroundColor Green
Write-Host ""

Write-Host "🔗 Connecting to GitHub..." -ForegroundColor Cyan
$repoUrl = "https://github.com/$username/sign-language-detection.git"
git remote add origin $repoUrl

Write-Host "✅ Connected to GitHub!" -ForegroundColor Green
Write-Host ""

Write-Host "📤 Pushing to GitHub..." -ForegroundColor Cyan
Write-Host ""
Write-Host "⚠️  You'll be prompted for your GitHub credentials:" -ForegroundColor Yellow
Write-Host "   • Username: $username" -ForegroundColor White
Write-Host "   • Password: Your GitHub password or Personal Access Token" -ForegroundColor White
Write-Host ""

git branch -M main
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host ("="*80) -ForegroundColor Green
    Write-Host "✅ SUCCESS! Your code is now on GitHub! 🎉" -ForegroundColor Green
    Write-Host ("="*80) -ForegroundColor Green
    Write-Host ""
    Write-Host "🌐 View your repository:" -ForegroundColor Cyan
    Write-Host "   https://github.com/$username/sign-language-detection" -ForegroundColor White
    Write-Host ""
    
    # Open repository in browser
    Start-Process "https://github.com/$username/sign-language-detection"
    
    Write-Host ""
    Write-Host ("─"*80) -ForegroundColor Gray
    Write-Host "🚀 NEXT STEP: DEPLOY TO STREAMLIT CLOUD" -ForegroundColor Yellow
    Write-Host ("─"*80) -ForegroundColor Gray
    Write-Host ""
    Write-Host "   1. Go to: https://share.streamlit.io/" -ForegroundColor White
    Write-Host "   2. Sign in with GitHub" -ForegroundColor White
    Write-Host "   3. Click 'New app'" -ForegroundColor White
    Write-Host "   4. Select: $username/sign-language-detection" -ForegroundColor White
    Write-Host "   5. Main file: streamlit_app.py" -ForegroundColor White
    Write-Host "   6. Click 'Deploy!'" -ForegroundColor White
    Write-Host ""
    Write-Host "Your app will be live at:" -ForegroundColor Cyan
    Write-Host "   https://$username-sign-language-detection.streamlit.app" -ForegroundColor Green
    Write-Host ""
    
    $deploy = Read-Host "Open Streamlit Cloud to deploy now? (y/n)"
    if ($deploy -eq 'y') {
        Start-Process "https://share.streamlit.io/"
    }
    
} else {
    Write-Host ""
    Write-Host "❌ Upload failed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Common issues:" -ForegroundColor Yellow
    Write-Host "   • Wrong credentials - Check username/password" -ForegroundColor White
    Write-Host "   • Repository already exists - Delete or use different name" -ForegroundColor White
    Write-Host "   • Network issues - Check internet connection" -ForegroundColor White
    Write-Host ""
    Write-Host "💡 Alternative: Use GitHub Desktop (easier)" -ForegroundColor Cyan
    Write-Host "   Download from: https://desktop.github.com/" -ForegroundColor White
    Write-Host ""
}

Write-Host ""
Read-Host "Press Enter to exit"
