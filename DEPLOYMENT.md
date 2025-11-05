# Deployment Guide - Top Dog (TopDog)

## Table of Contents
1. [System Requirements](#system-requirements)
2. [Local Development Setup](#local-development-setup)
3. [Production Build](#production-build)
4. [Deployment Options](#deployment-options)
5. [Environment Configuration](#environment-configuration)
6. [Security Checklist](#security-checklist)
7. [Troubleshooting](#troubleshooting)

## System Requirements

### Minimum Requirements
- **OS**: Windows 10+, macOS 10.15+, Ubuntu 18.04+
- **CPU**: 2 cores
- **RAM**: 4 GB
- **Storage**: 2 GB free space
- **Node.js**: 18+ (for development)
- **Python**: 3.11+ (for backend)
- **Rust**: 1.70+ (for Tauri)

### Recommended Requirements
- **CPU**: 4+ cores
- **RAM**: 8 GB
- **Storage**: 10 GB free space
- **Node.js**: 20 LTS
- **Python**: 3.12
- **Rust**: Latest stable

## Local Development Setup

### Prerequisites
```bash
# Install Node.js 20+ and Python 3.11+
# Install Rust via https://rustup.rs/

# Verify installations
node --version  # v20.x.x
python --version  # 3.11.x
cargo --version  # 1.70+
```

### Setup Steps
```bash
# Clone repository
git clone https://github.com/your-org/Top Dog.git
cd Top Dog

# Install dependencies
pnpm install

# Install backend dependencies
cd backend
pip install -r requirements.txt
cd ..

# Start dev server
pnpm run dev
```

### Development Ports
- **Frontend**: http://localhost:1431
- **Backend API**: http://127.0.0.1:8000
- **HMR (Hot Module Reload)**: ws://localhost:1432

## Production Build

### Desktop Application (Windows/macOS/Linux)

```bash
# Build frontend
cd frontend
pnpm run build

# Build Tauri application
cd frontend
pnpm tauri build

# Outputs in: frontend/src-tauri/target/release/bundle/
```

### Build Options by Platform

**Windows:**
```bash
pnpm tauri build --target x86_64-pc-windows-msvc
# Creates: .msi and portable .exe installers
```

**macOS:**
```bash
pnpm tauri build --target universal-apple-darwin
# Creates: .dmg and .app bundle
```

**Linux:**
```bash
pnpm tauri build --target x86_64-unknown-linux-gnu
# Creates: AppImage and deb packages
```

### Optimizations
- Tree shaking and minification enabled by default
- Code splitting for lazy loading
- Asset optimization (images, fonts)
- CSS minification via Tailwind
- React 19 with optimized rendering

## Deployment Options

### Option 1: Self-Hosted Desktop App
1. Build application using steps above
2. Create GitHub Release with built artifacts
3. Users download and install directly
4. App auto-updates via GitHub Releases (optional)

### Option 2: Cloud Deployment (Backend)
1. Deploy backend to cloud provider
2. Configure frontend to connect to cloud backend
3. Users access web interface or download desktop app

### Option 3: Hybrid (Recommended)
1. Desktop app for primary UI
2. Cloud backend for persistence and collaboration
3. Tauri for desktop integration

### Option 4: Web-Only
1. Deploy frontend to static hosting (Vercel, Netlify)
2. Deploy backend to serverless or container (AWS Lambda, Docker)
3. Users access via web browser

## Environment Configuration

### Backend Environment Variables

**Development (.env.dev)**
```bash
# Backend
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
BACKEND_URL=http://127.0.0.1:8000

# OAuth (Dev)
GOOGLE_CLIENT_ID=your-dev-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-dev-secret
GITHUB_CLIENT_ID=your-dev-client-id
GITHUB_CLIENT_SECRET=your-dev-secret

# Frontend
FRONTEND_URL=http://localhost:1431

# Optional: LLM Integration
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

**Production (.env.production)**
```bash
# Backend
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING
BACKEND_URL=https://api.Top Dog.com

# OAuth (Production)
GOOGLE_CLIENT_ID=your-prod-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-prod-secret
GITHUB_CLIENT_ID=your-prod-client-id
GITHUB_CLIENT_SECRET=your-prod-secret

# Frontend
FRONTEND_URL=https://Top Dog.com

# Security
SESSION_SECRET=your-random-secret-key-min-32-chars
SECURE_COOKIES=true
CORS_ORIGINS=https://Top Dog.com

# Database (if using persistent storage)
DATABASE_URL=postgresql://user:pass@host:5432/q_ide_prod

# LLM Integration (Production)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

### Frontend Configuration (vite.config.ts)
```typescript
// Update devUrl and proxy for production
server: {
  port: 1431,
  proxy: {
    '/api': {
      target: process.env.BACKEND_URL || 'http://127.0.0.1:8000',
      changeOrigin: true,
    }
  }
}
```

### Tauri Configuration (tauri.conf.json)
```json
{
  "productName": "Top Dog",
  "version": "0.1.0",
  "app": {
    "windows": [{
      "title": "Top Dog - TopDog IDE",
      "minWidth": 900,
      "minHeight": 600
    }],
    "security": {
      "csp": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
    }
  }
}
```

## Security Checklist

### Backend Security
- [ ] Environment variables not committed to git (use .env.example)
- [ ] OAuth secrets stored securely
- [ ] HTTPS enforced in production
- [ ] CORS properly configured
- [ ] Rate limiting implemented
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention (use parameterized queries)
- [ ] CSRF tokens for state-changing operations
- [ ] Security headers configured (CSP, X-Frame-Options, etc.)
- [ ] Logging doesn't expose secrets
- [ ] Session timeout configured
- [ ] Secure session cookies (HttpOnly, Secure, SameSite)

### Frontend Security
- [ ] CSP headers properly configured
- [ ] No hardcoded API keys or secrets
- [ ] Input sanitization for user-generated content
- [ ] API calls only to trusted origins
- [ ] XSS protection via React (auto-escaping)
- [ ] Dependencies scanned for vulnerabilities

### Application Security
- [ ] Tauri sandbox enabled
- [ ] File access restricted to necessary directories
- [ ] IPC commands properly validated
- [ ] Desktop app code signed (Windows/macOS)
- [ ] Auto-updates from trusted source only

### Infrastructure Security
- [ ] Firewall configured
- [ ] DDoS protection enabled
- [ ] Database backups encrypted
- [ ] Logs stored securely
- [ ] Monitoring and alerting configured
- [ ] Incident response plan documented

## Troubleshooting

### Build Issues

**Rust compilation fails**
```bash
# Update Rust
rustup update

# Clear build cache
cargo clean

# Rebuild
pnpm tauri build
```

**Node dependencies conflict**
```bash
# Clear node_modules
rm -r node_modules pnpm-lock.yaml

# Reinstall
pnpm install
```

**Tauri command not found**
```bash
# Install Tauri CLI globally
npm install -g @tauri-apps/cli

# Or use pnpm
pnpm add -g @tauri-apps/cli
```

### Runtime Issues

**Backend connection refused**
```bash
# Verify backend is running
curl http://127.0.0.1:8000/health

# Check port is not in use
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows
```

**OAuth redirect loop**
- Verify redirect URIs match OAuth app configuration
- Check BACKEND_URL environment variable
- Ensure session cookies are enabled

**Performance issues**
- Check bundle size: `pnpm run build -- --analyze`
- Monitor backend response times
- Check database query performance
- Verify no memory leaks in DevTools

## GitHub Release Creation

```bash
# Create tag and push
git tag v0.1.0
git push origin v0.1.0

# GitHub Actions automatically:
# 1. Builds for all platforms
# 2. Creates release
# 3. Uploads artifacts
```

## Monitoring & Logging

### Backend Logging
```python
import logging
logger = logging.getLogger(__name__)
logger.info("Application started")
logger.error("Error occurred", exc_info=True)
```

### Application Metrics
- Monitor API response times
- Track error rates
- Count build success/failure
- Measure resource usage (CPU, memory, disk)

## Support & Resources

- **Documentation**: See README.md
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Security**: security@Top Dog.com

---

**Version**: 0.1.0  
**Last Updated**: October 2025  
**Maintainer**: Quellum Team
