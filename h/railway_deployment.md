# 🚂 Railway Deployment Guide for ESP32 Carbon Credit Backend

## 🎯 Why Railway is Perfect for This Project

- ✅ **Full FastAPI Support** - No serverless limitations
- ✅ **WebSocket Support** - Real-time dashboard works perfectly
- ✅ **Automatic Deployments** - Push to GitHub = instant deploy
- ✅ **Environment Variables** - Secure Supabase integration
- ✅ **Custom Domains** - Professional URLs
- ✅ **Generous Free Tier** - Perfect for development

## 🚀 Step-by-Step Deployment

### Step 1: Prepare Your Code

1. **Push to GitHub** (if not already done):
   ```bash
   git init
   git add .
   git commit -m "ESP32 Carbon Credit Backend"
   git branch -M main
   git remote add origin https://github.com/yourusername/esp32-carbon-backend.git
   git push -u origin main
   ```

### Step 2: Setup Railway

1. **Install Railway CLI**:
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway**:
   ```bash
   railway login
   ```
   This opens your browser to authenticate.

3. **Create New Project**:
   ```bash
   cd h
   railway init
   ```
   - Choose "Deploy from GitHub repo"
   - Select your repository
   - Choose the `h` folder as root

### Step 3: Configure Environment Variables

```bash
# Set Supabase credentials
railway variables set SUPABASE_URL=https://your-project.supabase.co
railway variables set SUPABASE_ANON_KEY=your_supabase_anon_key

# Optional: Guardian API settings
railway variables set GUARDIAN_API_URL=http://localhost:3000/api/v1
railway variables set GUARDIAN_API_KEY=your_guardian_key
```

### Step 4: Deploy

```bash
railway up
```

That's it! Railway will:
- Detect Python automatically
- Install dependencies from `requirements.txt`
- Start your FastAPI server
- Give you a live URL

## 🔧 Railway-Optimized Configuration

Let me create Railway-specific files for optimal deployment:
## 📁 Ra
ilway-Optimized Files Created

I've added these files for optimal Railway deployment:

- `Procfile` - Tells Railway how to start your app
- `railway.toml` - Railway configuration
- `nixpacks.toml` - Build configuration
- `.railwayignore` - Files to ignore during deployment
- Health check endpoint at `/health`

## 🌐 After Deployment

### Your Live URLs
Railway will give you URLs like:
- **Dashboard**: `https://your-app-name.up.railway.app/`
- **API**: `https://your-app-name.up.railway.app/api/energy-data`
- **Health Check**: `https://your-app-name.up.railway.app/health`

### Update ESP32 Code
Change your ESP32 serverName to:
```cpp
const char* serverName = "https://your-app-name.up.railway.app/api/energy-data";
```

## 🔧 Railway Dashboard Features

### 1. **Metrics & Monitoring**
- CPU usage
- Memory usage
- Request logs
- Error tracking

### 2. **Environment Variables**
- Secure credential storage
- Easy updates without redeployment

### 3. **Custom Domains**
- Add your own domain
- Automatic SSL certificates

### 4. **Automatic Deployments**
- Push to GitHub = automatic deploy
- Rollback to previous versions
- Branch-based deployments

## 🚨 Troubleshooting

### Common Issues & Solutions

1. **Build Fails**
   ```bash
   # Check logs
   railway logs
   
   # Redeploy
   railway up --detach
   ```

2. **Environment Variables Not Working**
   ```bash
   # List current variables
   railway variables
   
   # Set missing variables
   railway variables set KEY=value
   ```

3. **Port Issues**
   - Railway automatically sets PORT environment variable
   - Your code now uses `int(os.getenv("PORT", 5000))`

4. **WebSocket Connection Issues**
   - Use `wss://` instead of `ws://` for HTTPS
   - Update dashboard WebSocket URL

### Logs & Debugging
```bash
# View live logs
railway logs

# View specific service logs
railway logs --service your-service-name
```

## 🎯 Production Optimizations

### 1. **Database Connection Pooling**
Add to your requirements.txt:
```
asyncpg==0.28.0
sqlalchemy[asyncio]==2.0.23
```

### 2. **Redis for Caching** (Optional)
```bash
# Add Redis service in Railway dashboard
railway add redis

# Update code to use Redis for latest_readings
```

### 3. **Monitoring & Alerts**
- Set up Railway monitoring
- Configure Supabase alerts
- Add error tracking (Sentry)

## 💰 Railway Pricing

### Free Tier (Perfect for Development)
- $5 credit per month
- Automatic sleep after inactivity
- All features included

### Pro Plan ($20/month)
- $20 credit included
- No sleeping
- Priority support
- Custom domains

## 🔄 Continuous Deployment Workflow

1. **Develop Locally**
   ```bash
   python main.py
   # Test at http://localhost:5000
   ```

2. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Update feature"
   git push
   ```

3. **Automatic Deploy**
   - Railway detects push
   - Builds and deploys automatically
   - Live in ~2 minutes

## 🌟 Advanced Features

### Custom Build Commands
In `railway.toml`:
```toml
[build]
builder = "NIXPACKS"

[build.nixpacksConfig]
cmds = ["pip install -r requirements.txt", "python setup.py"]
```

### Multiple Environments
```bash
# Create staging environment
railway environment create staging

# Deploy to staging
railway up --environment staging
```

### Database Backups
```bash
# If using Railway PostgreSQL
railway db backup create
railway db backup list
```

## 🎉 You're Ready!

Your ESP32 Carbon Credit Backend is now production-ready on Railway with:

- ✅ **Real-time WebSocket dashboard**
- ✅ **Supabase integration**
- ✅ **Guardian API compatibility**
- ✅ **Automatic deployments**
- ✅ **Professional monitoring**
- ✅ **Scalable infrastructure**

## 📞 Next Steps

1. **Deploy to Railway** using the steps above
2. **Update ESP32 code** with your Railway URL
3. **Setup Supabase** for data persistence
4. **Configure Guardian** for carbon credit verification
5. **Add custom domain** (optional)
6. **Monitor and scale** as needed

Happy deploying! 🚂⚡🌱