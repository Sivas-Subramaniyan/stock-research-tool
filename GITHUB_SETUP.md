# GitHub Repository Setup Guide

## Step 1: Create GitHub Repository

1. **Go to GitHub**: Visit [github.com](https://github.com) and sign in

2. **Create New Repository**:
   - Click the "+" icon in the top right
   - Select "New repository"

3. **Repository Settings**:
   - **Repository name**: `stock-research-tool` (or your preferred name)
   - **Description**: "AI-powered stock research and analysis tool with FastAPI backend"
   - **Visibility**: Choose Public or Private
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
   - Click "Create repository"

## Step 2: Connect Local Repository to GitHub

After creating the repository, GitHub will show you commands. Use these commands in your terminal:

```bash
# Add the remote repository (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/stock-research-tool.git

# Rename branch to main (if needed)
git branch -M main

# Push your code to GitHub
git push -u origin main
```

## Step 3: Verify Upload

1. **Refresh your GitHub repository page**
2. **You should see all your files** including:
   - README.md
   - api.py
   - frontend/ folder
   - requirements.txt
   - All other project files

## Step 4: Update Git Config (Optional but Recommended)

Update your Git configuration with your actual details:

```bash
git config --global user.email "your-actual-email@example.com"
git config --global user.name "Your Actual Name"
```

## Important Notes

### ⚠️ GitHub Pages Limitation

**GitHub Pages CANNOT host this application** because:
- It requires a Python backend server (FastAPI)
- GitHub Pages only serves static files (HTML/CSS/JS)
- No server-side processing is available

### ✅ Deployment Options

See `DEPLOYMENT.md` for deployment options:
- **Render** (Recommended - Free tier available)
- **Railway** (Easy setup)
- **Heroku** (Traditional option)
- **DigitalOcean App Platform**

### 🔐 Security Reminder

**Never commit API keys!** Make sure:
- `.env` file is in `.gitignore` (already done)
- API keys are only set as environment variables on your deployment platform
- Never hardcode API keys in your code

## Next Steps

1. ✅ Repository is created and code is pushed
2. 📖 Read `DEPLOYMENT.md` for hosting options
3. 🚀 Deploy to Render, Railway, or another platform
4. 🔗 Share your deployed application URL

## Repository Structure

Your GitHub repository should have:
```
├── README.md              # Main documentation
├── DEPLOYMENT.md          # Deployment guide
├── requirements.txt       # Python dependencies
├── api.py                 # FastAPI application
├── frontend/              # Frontend files
│   ├── index.html
│   ├── styles.css
│   └── script.js
├── research_agent.py      # Research logic
├── summarization_agent.py # Report generation
└── ... (other files)
```

## Troubleshooting

### If push fails:
- Check you're authenticated: `git config --list`
- Try using SSH instead: `git remote set-url origin git@github.com:USERNAME/REPO.git`
- Or use GitHub CLI: `gh auth login`

### If files are missing:
- Check `.gitignore` isn't excluding important files
- Verify files are committed: `git status`
- Check branch: `git branch`

