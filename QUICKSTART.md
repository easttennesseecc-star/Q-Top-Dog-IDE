# Top Dog (TopDog IDE) - Quick Start & Production Ready

![Top Dog](https://img.shields.io/badge/Q--IDE-Production%20Ready-green?style=for-the-badge)
![Version](https://img.shields.io/badge/version-0.1.0-blue?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)

## 🚀 Quick Start

### Prerequisites
- **Node.js** 18+ ([Install](https://nodejs.org/))
- **Python** 3.11+ ([Install](https://www.python.org/))
- **Rust** 1.70+ ([Install](https://rustup.rs/))
- **pnpm** ([Install](https://pnpm.io/))

### Development (30 seconds)

```bash
# Clone and setup
git clone https://github.com/quellum/Top Dog.git
cd Top Dog
pnpm install

# Start development server
pnpm run dev

# App opens at http://localhost:1431
```

### Production Build

```bash
# Build desktop application (Windows/macOS/Linux)
cd frontend
pnpm run build
pnpm tauri build

# Installers in: frontend/src-tauri/target/release/bundle/
```

## 📋 Documentation

| Document | Purpose |
|----------|---------|
| [DEPLOYMENT.md](DEPLOYMENT.md) | Deployment options, environment setup, troubleshooting |
| [TESTING.md](TESTING.md) | Test strategy, running tests, best practices |
| [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md) | Pre-release, release, and post-release procedures |
| [ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md) | System design, LLM agents, data flow |

## ✨ Features (Current Release)

✅ **Desktop Application** - Cross-platform (Windows/macOS/Linux)  
✅ **Background Customization** - Upload images, animated gradients, particles  
✅ **Local Storage** - IndexedDB for offline data persistence  
✅ **Export/Import** - Settings and media backup  
✅ **OAuth Integration** - Google & GitHub sign-in  
✅ **LLM Integration** - Connect to GPT-4, Claude, Ollama  
✅ **Build Health Dashboard** - Real-time status monitoring  
✅ **Responsive UI** - Tailwind CSS, dark mode  

## 🏗️ Project Structure

```
Top Dog/
├── frontend/                  # React + Tauri desktop app
│   ├── src/                   # TypeScript/React components
│   ├── e2e/                   # Playwright E2E tests
│   └── src-tauri/             # Rust/Tauri configuration
├── backend/                   # FastAPI Python backend
│   ├── main.py               # API entry point
│   ├── auth.py               # OAuth & session management
│   └── llm_pool.py           # LLM orchestration
├── .github/workflows/         # CI/CD pipelines
├── DEPLOYMENT.md             # Deployment guide
├── TESTING.md                # Test documentation
└── README.md                 # This file
```

## 🔒 Security

- ✅ Security headers configured (CSP, X-Frame-Options, etc.)
- ✅ CORS properly scoped for development/production
- ✅ OAuth2 for authentication (Google, GitHub)
- ✅ Session management with secure cookies
- ✅ Input validation on all API endpoints
- ✅ No secrets in source code (uses .env files)

**Security Checklist**: See [DEPLOYMENT.md](DEPLOYMENT.md#security-checklist)

## 🧪 Testing

```bash
# Frontend unit tests
pnpm test

# Frontend E2E tests (requires dev server)
pnpm exec playwright test

# Backend tests
cd backend && python -m pytest
```

**Test Coverage**: 80%+ target across all layers  
**Details**: See [TESTING.md](TESTING.md)

## 📦 Deployment

### Desktop Application
1. Download installer from [GitHub Releases](https://github.com/quellum/Top Dog/releases)
2. Run installer (Windows: `.msi`, macOS: `.dmg`, Linux: `.AppImage`)
3. Launch application

### Cloud Backend (Optional)
```bash
# Deploy backend to cloud provider
cd backend
# Push to AWS Lambda, Google Cloud Run, Azure Functions, etc.
```

**Full Guide**: See [DEPLOYMENT.md](DEPLOYMENT.md)

## 🌐 Environment Setup

### Development

```bash
# Create .env.development file
cat > .env.development << EOF
ENVIRONMENT=development
DEBUG=true
BACKEND_URL=http://127.0.0.1:8000
FRONTEND_URL=http://localhost:1431
GOOGLE_CLIENT_ID=your-dev-client-id
GOOGLE_CLIENT_SECRET=your-dev-secret
GITHUB_CLIENT_ID=your-dev-client-id
GITHUB_CLIENT_SECRET=your-dev-secret
EOF
```

### Production

```bash
# Set environment variables (never commit .env.production)
export ENVIRONMENT=production
export BACKEND_URL=https://api.Top Dog.com
export FRONTEND_URL=https://Top Dog.com
# ... other variables
```

**Details**: See `.env.example` and [DEPLOYMENT.md](DEPLOYMENT.md#environment-configuration)

## 🎯 Release Status

**Current Version**: v0.1.0  
**Status**: ✅ Production Ready  
**Release Date**: October 25, 2025  

### What's Included
- Desktop application for Windows, macOS, Linux
- Full OAuth authentication
- Background customization with media upload
- Local data persistence
- Settings export/import
- Build health monitoring
- LLM integration examples

### What's Coming
- Live collaboration & pair programming
- Advanced debugging tools
- Extension marketplace
- Remote workspace sync
- Plugin system

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit changes: `git commit -am 'Add my feature'`
4. Push to branch: `git push origin feature/my-feature`
5. Submit pull request

**Guidelines**: See contributing.md (coming soon)

## 🐛 Bug Reports & Support

- **Issues**: [GitHub Issues](https://github.com/quellum/Top Dog/issues)
- **Discussions**: [GitHub Discussions](https://github.com/quellum/Top Dog/discussions)
- **Email**: support@Top Dog.com
- **Security**: security@Top Dog.com

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

Built with:
- [Tauri](https://tauri.app/) - Desktop framework
- [React](https://react.dev/) - UI library
- [Tailwind CSS](https://tailwindcss.com/) - Styling
- [FastAPI](https://fastapi.tiangolo.com/) - Python backend
- [Playwright](https://playwright.dev/) - E2E testing

## 📞 Support & Contact

| Channel | Link |
|---------|------|
| Documentation | https://Top Dog.com/docs |
| Issues | https://github.com/quellum/Top Dog/issues |
| Email | support@Top Dog.com |
| Twitter | [@qIDEdev](https://twitter.com/qIDEdev) |

---

**Top Dog** - The Top Dog IDE  
Built with ❤️ by [Quellum Team](https://quellum.com)

*Last Updated: October 25, 2025*
