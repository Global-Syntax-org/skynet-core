# GitHub Repository Setup Script for Skynet Lite

Write-Host "🚀 Setting up Skynet Lite for GitHub..." -ForegroundColor Green

# Initialize git if not already done
if (-not (Test-Path ".git")) {
    git init
    Write-Host "✅ Git repository initialized" -ForegroundColor Green
}

# Add all files
git add .

# Initial commit
git commit -m "🎉 Initial commit: Skynet Lite v1.0.0

- Local AI chatbot with Ollama integration
- Web search capabilities with Bing API
- Modular plugin architecture
- Async/await implementation
- Comprehensive documentation
- CI/CD pipeline ready"

Write-Host "✅ Initial commit created" -ForegroundColor Green

# Set up remote instructions
Write-Host "🔗 To connect to GitHub:" -ForegroundColor Yellow
Write-Host "1. Create a new repository on GitHub named 'skynet-lite'" -ForegroundColor White
Write-Host "2. Run: git remote add origin https://github.com/yourusername/skynet-lite.git" -ForegroundColor White
Write-Host "3. Run: git branch -M main" -ForegroundColor White
Write-Host "4. Run: git push -u origin main" -ForegroundColor White

Write-Host ""
Write-Host "🎯 Repository is ready for GitHub!" -ForegroundColor Green
Write-Host "📋 Don't forget to:" -ForegroundColor Yellow
Write-Host "   - Update the repository URL in README.md" -ForegroundColor White
Write-Host "   - Add repository secrets for CI/CD" -ForegroundColor White
Write-Host "   - Configure branch protection rules" -ForegroundColor White
Write-Host "   - Add collaborators if needed" -ForegroundColor White