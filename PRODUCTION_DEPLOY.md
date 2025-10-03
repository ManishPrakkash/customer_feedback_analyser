# Production Deployment Guide

## Backend Deployment Summary

Your Customer Feedback Analysis backend is now **production-ready** with the following improvements:

### ✅ Production Features Added

1. **Security & Validation**
   - Request validation with Pydantic models
   - Trusted host middleware for production
   - CORS properly configured
   - Input sanitization and length limits

2. **Error Handling & Logging**
   - Structured logging with timestamps
   - Global exception handlers
   - Graceful fallback mechanisms
   - Request timing middleware

3. **Monitoring & Health Checks**
   - Comprehensive `/health` endpoint with database status
   - Startup/shutdown logging
   - Request performance tracking

4. **Configuration Management**
   - Environment-based configuration
   - Secure secrets handling
   - Production/development mode switching

5. **Performance & Reliability**
   - Gunicorn for production WSGI
   - Connection pooling for database
   - Optimized dependency versions
   - Fallback responses when AI fails

## Quick Deploy to Render

### Option A: Simple Deploy (Recommended)
**Render Settings:**
- **Root Directory**: `agent-service`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

**Environment Variables:**
```
ENVIRONMENT=production
DEMO_MODE=true
ALLOWED_ORIGINS=*
```

### Option B: Production Deploy with Gunicorn
**Render Settings:**
- **Root Directory**: `agent-service`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app.main:app -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`

**Environment Variables:**
```
ENVIRONMENT=production
DEMO_MODE=true
ALLOWED_ORIGINS=*
LOG_LEVEL=INFO
```

### Option C: From Repository Root
**Render Settings:**
- **Root Directory**: (leave empty - repository root)
- **Build Command**: `pip install -r agent-service/requirements.txt`
- **Start Command**: `python agent-service/run_server.py`

**Environment Variables:**
```
ENVIRONMENT=production
DEMO_MODE=true
ALLOWED_ORIGINS=*
```

## Security Configuration

After getting your Vercel frontend URL, update these settings:

1. **Restrict CORS** (Important!)
   ```
   ALLOWED_ORIGINS=https://your-app.vercel.app
   ```

2. **Set Trusted Hosts**
   ```
   TRUSTED_HOSTS=your-backend.onrender.com
   ```

3. **Disable Demo Mode** (if using real AI)
   ```
   DEMO_MODE=false
   OPENAI_API_KEY=your_real_key
   ```

## Testing Your Deployed Backend

Once deployed, test these endpoints:

```bash
# Health check
curl https://your-backend.onrender.com/health

# Basic info
curl https://your-backend.onrender.com/

# Analyze feedback
curl -X POST https://your-backend.onrender.com/analyze \
  -H "Content-Type: application/json" \
  -d '{"feedback":"Great product, love it!"}'
```

## What's Different from Dev Version

| Feature | Development | Production |
|---------|-------------|------------|
| Error Responses | Detailed stack traces | Generic error messages |
| Documentation | `/docs` available | `/docs` disabled |
| CORS | `*` (all origins) | Specific domains only |
| Logging | Print statements | Structured logging |
| Security | Minimal | Trusted hosts, validation |
| Performance | Single process | Multi-worker Gunicorn |
| Fallbacks | None | Graceful degradation |

## Monitoring in Production

Your backend now logs:
- Request timing and status codes
- Error details with timestamps  
- Database connection health
- Environment and configuration info

Check Render logs to monitor:
- Response times via `X-Process-Time` header
- Error patterns and frequencies
- Health check results

## Next Steps

1. **Deploy backend** using one of the options above
2. **Test all endpoints** with the curl commands
3. **Note your backend URL** for frontend configuration
4. **Deploy frontend** to Vercel with `NEXT_PUBLIC_AGENT_SERVICE_URL`
5. **Restrict CORS** to your actual domain
6. **Monitor logs** for any issues

Your backend is now enterprise-ready! 🚀