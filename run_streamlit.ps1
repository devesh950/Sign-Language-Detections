# Run Streamlit App Locally

Write-Host ""
Write-Host ("="*80) -ForegroundColor Cyan
Write-Host "🤟 SIGN LANGUAGE DETECTION - STREAMLIT APP" -ForegroundColor Yellow
Write-Host ("="*80) -ForegroundColor Cyan
Write-Host ""

# Set Keras backend
$env:KERAS_BACKEND = "jax"
Write-Host "✓ Keras backend set to JAX" -ForegroundColor Green

Write-Host ""
Write-Host "🚀 Starting Streamlit server..." -ForegroundColor Yellow
Write-Host ""
Write-Host "📱 ACCESS FROM:" -ForegroundColor Cyan
Write-Host "   • Local: http://localhost:8501" -ForegroundColor White
Write-Host "   • Network: http://YOUR_IP:8501" -ForegroundColor White
Write-Host ""
Write-Host "💡 TIPS:" -ForegroundColor Yellow
Write-Host "   • Allow camera access when prompted" -ForegroundColor Gray
Write-Host "   • Use good lighting for best detection" -ForegroundColor Gray
Write-Host "   • Hold gestures steady for 1-2 seconds" -ForegroundColor Gray
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Red
Write-Host ""
Write-Host ("="*80) -ForegroundColor Cyan
Write-Host ""

# Run Streamlit
C:/Users/deves/AppData/Local/Microsoft/WindowsApps/python3.12.exe -m streamlit run streamlit_app.py

Write-Host ""
Write-Host "Server stopped." -ForegroundColor Yellow
