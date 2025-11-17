# Render Deployment Guide

## Quick Fix for "Could not import module 'api'" Error

### Problem
Render can't find the `api` module because the files weren't in the GitHub repository.

### Solution Applied
✅ All files have been pushed to GitHub:
- `api.py` - Main FastAPI application
- `run_orchestrator.py` - Orchestrator script
- `run_research.py` - Research script
- `Procfile` - Process file for Render
- `runtime.txt` - Python version specification
- `render.yaml` - Render configuration (optional)

## Deployment Steps on Render

### Step 1: Connect Repository
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository: `Sivas-Subramaniyan/stock-research-tool`
4. Select the repository

### Step 2: Configure Service

**Basic Settings:**
- **Name**: `stock-research-tool` (or your choice)
- **Environment**: `Python 3`
- **Region**: Choose closest to you
- **Branch**: `main`

**Build & Deploy:**
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn api:app --host 0.0.0.0 --port $PORT`

**OR** use the Procfile (Render will auto-detect it):
- Start Command: Leave empty (Render will use Procfile automatically)

### Step 3: Add Environment Variables

Go to "Environment" tab and add:

1. **TAVILY_API_KEY**
   - Key: `TAVILY_API_KEY`
   - Value: Your Tavily API key

2. **OPENAI_API_KEY**
   - Key: `OPENAI_API_KEY`
   - Value: Your OpenAI API key

### Step 4: Deploy

1. Click "Create Web Service"
2. Render will:
   - Clone your repository
   - Install dependencies
   - Start the application
3. Wait for deployment to complete (2-5 minutes)

### Step 5: Access Your Application

Once deployed, your app will be available at:
- **URL**: `https://stock-research-tool.onrender.com` (or your custom name)
- **API Docs**: `https://stock-research-tool.onrender.com/docs`
- **Frontend**: `https://stock-research-tool.onrender.com/`

## Troubleshooting

### Error: "Could not import module 'api'"

**Fixed!** This was because `api.py` wasn't in the repository. It's now been added and pushed.

### Error: "TAVILY_API_KEY environment variable is required"

**Solution**: Make sure you've added the environment variables in Render dashboard:
1. Go to your service
2. Click "Environment" tab
3. Add `TAVILY_API_KEY` and `OPENAI_API_KEY`
4. Click "Save Changes"
5. Render will automatically redeploy

### Error: "Module not found"

**Solution**: Check that all dependencies are in `requirements.txt`:
```bash
pip install -r requirements.txt
```

### Build Fails

**Check:**
1. Python version in `runtime.txt` (currently 3.11.0)
2. All dependencies in `requirements.txt`
3. Build logs in Render dashboard

### Application Crashes on Start

**Check:**
1. Environment variables are set correctly
2. Start command is correct: `uvicorn api:app --host 0.0.0.0 --port $PORT`
3. Port is using `$PORT` (not hardcoded)

## Using render.yaml (Optional)

If you want to use the `render.yaml` file:

1. In Render dashboard, select "Apply Render YAML"
2. Render will use the configuration from `render.yaml`
3. You still need to set environment variables in the dashboard

## Post-Deployment

### Test Your Deployment

1. **Check API**: Visit `https://your-app.onrender.com/docs`
2. **Check Frontend**: Visit `https://your-app.onrender.com/`
3. **Test Endpoints**: Try `/companies` endpoint

### Monitor Logs

- Go to "Logs" tab in Render dashboard
- Check for any errors or warnings
- Monitor application performance

### Custom Domain (Optional)

1. Go to "Settings" → "Custom Domain"
2. Add your domain
3. Follow DNS configuration instructions

## Important Notes

- **Free Tier**: Render free tier spins down after 15 minutes of inactivity
- **Cold Starts**: First request after spin-down may take 30-60 seconds
- **Upgrade**: For always-on service, upgrade to paid plan
- **Environment Variables**: Never commit API keys to code (already fixed)

## Next Steps

1. ✅ Repository is updated with all files
2. ✅ Procfile and runtime.txt added
3. 🔄 **Redeploy on Render** (it should auto-detect the new files)
4. ✅ Set environment variables
5. 🎉 Your app should be live!

## Support

If you still encounter issues:
1. Check Render build logs
2. Verify all files are in GitHub repository
3. Ensure environment variables are set
4. Check that `api.py` is in the root directory

