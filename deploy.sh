#!/bin/bash

# Investor Event Assistant - Deployment Script
echo "🚀 Deploying Investor Event Assistant..."

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "❌ Git repository not found. Initializing..."
    git init
    echo "✅ Git repository initialized"
fi

# Add all files (excluding .gitignore items)
echo "📁 Adding files to git..."
git add .

# Check if there are changes to commit
if git diff --staged --quiet; then
    echo "ℹ️  No changes to commit"
else
    # Commit changes
    echo "💾 Committing changes..."
    git commit -m "Deploy: Updated Investor Event Assistant $(date '+%Y-%m-%d %H:%M:%S')"
    echo "✅ Changes committed"
fi

# Check if origin remote exists
if git remote | grep -q "origin"; then
    echo "🔄 Pushing to GitHub..."
    git push origin main
    echo "✅ Code pushed to GitHub"
else
    echo "⚠️  No remote 'origin' found."
    echo "🔧 Add your GitHub repository:"
    echo "   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git"
    echo "   git branch -M main"
    echo "   git push -u origin main"
fi

echo ""
echo "🎉 Deployment script complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Go to https://share.streamlit.io"
echo "2. Sign in with GitHub"
echo "3. Create new app from your repository"
echo "4. Add your GEMINI_API_KEY in Secrets"
echo "5. Deploy and enjoy! 🚀"
echo ""
echo "📖 Full guide: See DEPLOYMENT.md" 