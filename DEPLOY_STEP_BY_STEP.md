# 🚀 Step-by-Step Deployment Guide

## Prerequisites
- GitHub account with your repository
- Render account (free tier available)

## Step 1: Prepare Your Code for Deployment

### 1.1 Commit Your Changes
```powershell
# From your project root
git add .
git commit -m "Add production-ready backend with error handling and security"
git push origin master
```

## Step 2: Deploy Backend to Render

### 2.1 Sign Up/Login to Render
1. Go to [render.com](https://render.com)
2. Click "Get Started"
3. Sign up with GitHub (recommended)
4. Authorize Render to access your repositories

### 2.2 Create New Web Service
1. On Render dashboard, click **"New +"** button
2. Select **"Web Service"**
3. Click **"Build and deploy from a Git repository"**
4. Click **"Connect"** next to your GitHub account

### 2.3 Select Your Repository
1. Find `customer_feedback_analyser` in the list
2. Click **"Connect"**

### 2.4 Configure Service Settings
Fill in these exact values:

**Basic Information:**
- **Name**: `customer-feedback-api` (or your choice)
- **Region**: Choose closest to you (e.g., Ohio, Oregon)
- **Branch**: `master`
- **Root Directory**: `agent-service`
- **Runtime**: `Python 3`

**Build & Deploy Commands:**
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

**Pricing:**
- **Instance Type**: `Free` (sufficient for testing)

### 2.5 Set Environment Variables
Click **"Advanced"** then **"Add Environment Variable"** for each:

| Key | Value |
|-----|-------|
| `ENVIRONMENT` | `production` |
| `DEMO_MODE` | `true` |
| `ALLOWED_ORIGINS` | `*` |
| `LOG_LEVEL` | `INFO` |

### 2.6 Deploy
1. Click **"Create Web Service"**
2. Wait for deployment (5-10 minutes)
3. Watch the build logs for any errors

## Step 3: Test Your Deployed Backend

### 3.1 Get Your Backend URL
- After deployment, you'll see your URL like: `https://customer-feedback-api.onrender.com`
- Copy this URL - you'll need it for the frontend

### 3.2 Test Endpoints
Open PowerShell and test:

```powershell
# Replace YOUR_BACKEND_URL with your actual URL
$backend = "https://customer-feedback-api.onrender.com"

# Test health check
Invoke-WebRequest -Uri "$backend/health" -Method GET

# Test basic info
Invoke-WebRequest -Uri "$backend/" -Method GET

# Test analyze endpoint
Invoke-WebRequest -Uri "$backend/analyze" -Method POST -ContentType "application/json" -Body '{"feedback":"Great product, love the features!"}'
```

**Expected Results:**
- All should return `StatusCode: 200`
- Health check returns status info
- Analyze returns structured feedback analysis

## Step 4: Deploy Frontend to Vercel

### 4.1 Sign Up/Login to Vercel
1. Go to [vercel.com](https://vercel.com)
2. Sign up with GitHub
3. Authorize Vercel

### 4.2 Import Your Project
1. Click **"New Project"**
2. Import `customer_feedback_analyser` repository
3. Configure deployment:
   - **Framework Preset**: `Next.js`
   - **Root Directory**: `agent-ui`
   - **Build Command**: `npm run build` (auto-detected)
   - **Output Directory**: `.next` (auto-detected)

### 4.3 Set Environment Variables
Click **"Environment Variables"** and add:

| Key | Value |
|-----|-------|
| `NEXT_PUBLIC_AGENT_SERVICE_URL` | Your backend URL (e.g., `https://customer-feedback-api.onrender.com`) |

### 4.4 Deploy Frontend
1. Click **"Deploy"**
2. Wait for build completion (3-5 minutes)
3. Get your frontend URL (e.g., `https://your-app.vercel.app`)

## Step 5: Secure Your Backend (Important!)

### 5.1 Update CORS Settings
1. Go back to Render dashboard
2. Select your backend service
3. Go to **"Environment"** tab
4. Edit `ALLOWED_ORIGINS` variable
5. Change from `*` to your Vercel URL: `https://your-app.vercel.app`
6. Click **"Save Changes"**
7. Service will auto-redeploy

### 5.2 Add Trusted Hosts (Optional)
Add another environment variable:
- **Key**: `TRUSTED_HOSTS`
- **Value**: `your-backend.onrender.com`

## Step 6: Final Testing

### 6.1 Test Full Stack
1. Open your Vercel URL in browser
2. Try submitting feedback through the UI
3. Verify it returns analysis results
4. Check both positive and negative feedback

### 6.2 Monitor Logs
- **Render**: Go to your service → "Logs" tab to see backend activity
- **Vercel**: Go to your project → "Functions" tab for frontend logs

## Step 7: Optional Enhancements

### 7.1 Custom Domain (Optional)
- **Render**: Add custom domain in service settings
- **Vercel**: Add custom domain in project settings

### 7.2 Enable Real AI (Optional)
If you want to use real OpenAI instead of demo mode:
1. Get OpenAI API key from [platform.openai.com](https://platform.openai.com)
2. In Render, set environment variables:
   - `DEMO_MODE`: `false`
   - `OPENAI_API_KEY`: `your_actual_key`

## Troubleshooting

### Common Issues:

**Backend won't start:**
- Check build logs in Render
- Ensure Root Directory is set to `agent-service`
- Verify Start Command is correct

**Frontend can't connect to backend:**
- Check `NEXT_PUBLIC_AGENT_SERVICE_URL` is set correctly
- Ensure CORS allows your frontend domain
- Test backend endpoints directly first

**CORS errors:**
- Update `ALLOWED_ORIGINS` to include your frontend URL
- Don't use `*` in production

**Slow responses:**
- Free tier has limited resources
- Consider upgrading to paid tier for better performance

## Success Checklist ✅

- [ ] Backend deployed to Render
- [ ] Backend health check returns 200
- [ ] Backend analyze endpoint works
- [ ] Frontend deployed to Vercel  
- [ ] Frontend can connect to backend
- [ ] CORS properly configured
- [ ] Full stack works end-to-end

## Your Live URLs

After deployment, update these in your documentation:

- **Backend API**: `https://your-backend.onrender.com`
- **Frontend App**: `https://your-app.vercel.app`
- **API Documentation**: `https://your-backend.onrender.com/docs` (dev only)

🎉 **Congratulations!** Your Customer Feedback Analysis app is now live!

## Next Steps After Deployment

1. **Share your app** - Send the Vercel URL to users
2. **Monitor usage** - Check logs for any errors
3. **Iterate** - Add new features based on feedback
4. **Scale** - Upgrade to paid tiers if needed