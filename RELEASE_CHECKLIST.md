# Production Release Checklist - Top Dog v0.1.0

## Pre-Release (1 week before)

### Code Quality
- [ ] All tests passing (unit, integration, E2E)
- [ ] No TypeScript compilation errors
- [ ] No ESLint warnings
- [ ] No security vulnerabilities (npm audit, safety)
- [ ] Code review completed
- [ ] Branch protection rules enforced

### Documentation
- [ ] README.md up-to-date
- [ ] DEPLOYMENT.md completed
- [ ] TESTING.md completed
- [ ] API documentation current
- [ ] Changelog updated
- [ ] Contributing guidelines defined

### Testing
- [ ] Unit test coverage > 80%
- [ ] E2E tests passing on all platforms
- [ ] Manual testing checklist completed
- [ ] Performance benchmarks run
- [ ] Security scanning completed

## Release Day (Before Publishing)

### Version Bump
- [ ] Update version in `package.json` (frontend)
- [ ] Update version in `backend/package.json` (if exists)
- [ ] Update version in `tauri.conf.json`
- [ ] Update `CHANGELOG.md`
- [ ] Commit with message: "chore: bump version to X.Y.Z"

### Build Verification
- [ ] Frontend builds without errors
  ```bash
  pnpm run build
  ```
- [ ] Backend tests pass
  ```bash
  cd backend && python -m pytest
  ```
- [ ] Tauri builds on target platform
  ```bash
  pnpm tauri build
  ```

### Security Checks
- [ ] No API keys in code
- [ ] No secrets in git history
- [ ] OAuth credentials not hardcoded
- [ ] Environment variables documented
- [ ] Security headers configured
- [ ] CORS properly scoped

### Configuration Verification
- [ ] `tauri.conf.json` production settings
- [ ] Environment variables set correctly
- [ ] Database migrations run (if applicable)
- [ ] Cache cleared
- [ ] CDN configured (if using)

## Release (Publishing)

### Create Release Tag
```bash
# Commit release
git add .
git commit -m "release: v0.1.0"

# Create tag
git tag -a v0.1.0 -m "Release version 0.1.0"

# Push to GitHub
git push origin main
git push origin v0.1.0
```

### Publish to GitHub Releases
- [ ] GitHub Actions completed successfully
- [ ] All platform builds present
- [ ] Release notes written
- [ ] Upload additional docs if needed
- [ ] Mark as "Latest Release"

### Post-Release
- [ ] Update download links in documentation
- [ ] Announce on social media
- [ ] Send release email to stakeholders
- [ ] Close related GitHub issues

## Post-Release (First Week)

### Monitoring
- [ ] No critical bugs reported
- [ ] Error rates normal
- [ ] Performance metrics within baseline
- [ ] User feedback monitored
- [ ] Crash reports reviewed

### Support
- [ ] Issues triaged and responded to
- [ ] Common problems documented
- [ ] FAQ updated
- [ ] Known issues documented

### Follow-up
- [ ] Release retrospective conducted
- [ ] Lessons learned documented
- [ ] Process improvements identified
- [ ] Next sprint planned

## Platform-Specific Checklist

### Windows Release
- [ ] MSI installer tested
- [ ] Portable .exe tested
- [ ] File associations set (if applicable)
- [ ] Start menu shortcuts created
- [ ] Uninstall process verified
- [ ] Registry settings minimal
- [ ] SmartScreen whitelisting requested (if needed)

### macOS Release
- [ ] .dmg installer tested
- [ ] .app bundle tested
- [ ] Code signing certificate valid
- [ ] Notarization completed
- [ ] Gatekeeper whitelist applied (if needed)
- [ ] Universal binary includes both architectures

### Linux Release
- [ ] .AppImage tested
- [ ] .deb package tested
- [ ] Desktop entry file valid
- [ ] Icon included
- [ ] Install paths correct
- [ ] Launcher integration verified

## Communication Template

```markdown
# Top Dog Release v0.1.0 🎉

**Release Date**: October 25, 2025

## What's New
- [Feature 1]
- [Feature 2]
- Bug fixes and improvements

## Downloads
- [Windows](link-to-msi)
- [macOS](link-to-dmg)
- [Linux](link-to-appimage)

## Installation
See [DEPLOYMENT.md](link) for detailed instructions.

## Known Issues
- [Issue 1]
- [Issue 2]

## Support
- Documentation: https://Top Dog.com/docs
- Issues: https://github.com/quellum/Top Dog/issues
- Email: support@Top Dog.com

Thank you for using Top Dog!
```

## Rollback Plan

If critical issues discovered:

1. **Identify Issue**
   - Reproduce locally
   - Determine impact
   - Check error logs

2. **Hotfix**
   - Create hotfix branch: `git checkout -b hotfix/issue-name main`
   - Fix issue
   - Test thoroughly
   - Merge to main

3. **Re-release**
   - Bump version to v0.1.1
   - Tag and push
   - GitHub Actions rebuilds
   - Publish new release

4. **Communication**
   - Notify users of issue
   - Release hotfix announcement
   - Document lessons learned

## Success Criteria

✅ Release is successful when:
- [ ] All builds published to GitHub Releases
- [ ] No critical bugs reported in first 24 hours
- [ ] Download metrics show adoption
- [ ] Support tickets minimal
- [ ] Community feedback positive

❌ Rollback if:
- [ ] Critical security vulnerability
- [ ] Application crash on startup
- [ ] Data corruption
- [ ] Complete feature broken
- [ ] OAuth/authentication completely broken

---

**Release Manager**: [Your Name]  
**Release Date**: October 25, 2025  
**Status**: Ready for Release ✅
