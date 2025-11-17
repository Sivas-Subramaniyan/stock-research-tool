# Deployment Guide

## Important: GitHub Pages Limitation

**GitHub Pages cannot host this application** because it requires a Python backend server (FastAPI). GitHub Pages only serves static HTML/CSS/JS files and cannot run Python code or API servers.

## Recommended Deployment Options

### Option 1: Render (Easiest - Recommended)

1. **Sign up** at [render.com](https://render.com) (free tier available)

2. **Create a New Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select your repository

3. **Configure the Service**:
   - **Name**: `stock-research-tool` (or your choice)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn api:app --host 0.0.0.0 --port $PORT`

4. **Add Environment Variables**:
   - Go to "Environment" tab
   - Add:
     - `TAVILY_API_KEY` = your Tavily API key
     - `OPENAI_API_KEY` = your OpenAI API key

5. **Deploy**:
   - Click "Create Web Service"
   - Render will automatically build and deploy
   - Your app will be available at: `https://your-app-name.onrender.com`

### Option 2: Railway

1. **Sign up** at [railway.app](https://railway.app)

2. **Create New Project**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

3. **Configure**:
   - Railway auto-detects FastAPI
   - Add environment variables:
     - `TAVILY_API_KEY`
     - `OPENAI_API_KEY`

4. **Deploy**:
   - Railway automatically deploys
   - Get your URL from the dashboard

### Option 3: Heroku

1. **Install Heroku CLI**: [heroku.com/cli](https://devcenter.heroku.com/articles/heroku-cli)

2. **Create Procfile** (in project root):
   ```
   web: uvicorn api:app --host 0.0.0.0 --port $PORT
   ```

3. **Deploy**:
   ```bash
   heroku login
   heroku create your-app-name
   heroku config:set TAVILY_API_KEY=your_key
   heroku config:set OPENAI_API_KEY=your_key
   git push heroku master
   ```

### Option 4: DigitalOcean App Platform

1. **Sign up** at [digitalocean.com](https://www.digitalocean.com)

2. **Create App**:
   - Connect GitHub repository
   - Select "Python" as runtime
   - Set start command: `uvicorn api:app --host 0.0.0.0 --port $PORT`

3. **Add Environment Variables** and deploy

## Alternative: Separate Frontend/Backend

If you want to use GitHub Pages for the frontend:

1. **Deploy Backend** to Render/Railway/Heroku (as above)

2. **Update Frontend** to point to backend URL:
   - Edit `frontend/script.js`
   - Change `API_BASE_URL` to your backend URL

3. **Deploy Frontend to GitHub Pages**:
   - Create `gh-pages` branch
   - Push frontend files
   - Enable GitHub Pages in repository settings

## Environment Variables

All deployment platforms require these environment variables:

- `TAVILY_API_KEY`: Your Tavily API key
- `OPENAI_API_KEY`: Your OpenAI API key
- `API_HOST`: (Optional) Defaults to `0.0.0.0`
- `API_PORT`: (Optional) Defaults to `8000` (or use `$PORT` for cloud platforms)

## Post-Deployment

After deployment:

1. **Test the API**: Visit `https://your-app-url/docs` to see API documentation
2. **Test the Frontend**: Visit `https://your-app-url/` to use the application
3. **Monitor Logs**: Check platform logs for any errors
4. **Set up Custom Domain** (optional): Configure in platform settings

## Troubleshooting

### Common Issues:

1. **Port Error**: Make sure to use `$PORT` environment variable in start command
2. **API Keys Not Working**: Verify environment variables are set correctly
3. **Build Fails**: Check that all dependencies are in `requirements.txt`
4. **CORS Issues**: FastAPI CORS is already configured in `api.py`

### Need Help?

- Check platform-specific documentation
- Review application logs
- Test API endpoints using `/docs` endpoint

