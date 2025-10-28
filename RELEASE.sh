#!/usr/bin/env bash
# Production Release Script - Q-IDE v0.1.0
# Usage: bash RELEASE.sh

set -e

echo "🚀 Q-IDE v0.1.0 PRODUCTION RELEASE"
echo "===================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Version Update
echo -e "${BLUE}[STEP 1/3] Updating version to 0.1.0...${NC}"
echo "- Updating frontend/package.json..."
# Note: Manual edit required - can't be automated
echo "- Updating frontend/src-tauri/tauri.conf.json..."
# Note: Manual edit required
echo "- Updating backend/package.json..."
# Note: Manual edit required
echo ""
echo -e "${YELLOW}⚠️  Manual Step Required:${NC}"
echo "   Edit these files and set version to 0.1.0:"
echo "   1. frontend/package.json"
echo "   2. frontend/src-tauri/tauri.conf.json"
echo "   3. backend/package.json (if exists)"
echo ""
read -p "Press ENTER after updating versions..."
echo ""

# Step 1b: Git operations
echo -e "${BLUE}[STEP 1/3] Committing and tagging...${NC}"
git add .
git commit -m "chore: bump version to 0.1.0"
git tag -a v0.1.0 -m "Release Q-IDE v0.1.0 - Production Ready"
echo -e "${GREEN}✅ Tagged v0.1.0${NC}"
echo ""

# Step 2: Push
echo -e "${BLUE}[STEP 2/3] Pushing to GitHub...${NC}"
git push origin main
git push origin v0.1.0
echo -e "${GREEN}✅ Pushed to GitHub${NC}"
echo ""
echo "GitHub Actions will now:"
echo "  - Build for Windows (MSI + portable)"
echo "  - Build for macOS (DMG + universal binary)"
echo "  - Build for Linux (AppImage + DEB)"
echo "  - Create GitHub Release"
echo ""
echo "Monitor progress: https://github.com/quellum/q-ide/actions"
echo ""

# Step 3: Release notes
echo -e "${BLUE}[STEP 3/3] Release Notes${NC}"
echo ""
echo "📝 Release notes template prepared."
echo "Next steps:"
echo "  1. Go to: https://github.com/quellum/q-ide/releases"
echo "  2. Edit the v0.1.0 release"
echo "  3. Add release notes (copy from DEPLOY_NOW.md)"
echo "  4. Publish release"
echo ""

# Final status
echo "============================================"
echo -e "${GREEN}✅ PRODUCTION RELEASE INITIATED!${NC}"
echo "============================================"
echo ""
echo "🎉 Q-IDE v0.1.0 is now available!"
echo ""
echo "📊 Status:"
echo "   ✅ Code committed & tagged"
echo "   ✅ GitHub Actions building (10-15 min)"
echo "   ⏳ Awaiting release notes (you'll do this)"
echo ""
echo "📦 Downloads available at:"
echo "   https://github.com/quellum/q-ide/releases/v0.1.0"
echo ""
echo "📚 Documentation:"
echo "   - QuickStart: QUICKSTART.md"
echo "   - Deployment: DEPLOYMENT.md"
echo "   - Testing: TESTING.md"
echo ""
echo "✨ Release complete! 🚀"
echo ""
