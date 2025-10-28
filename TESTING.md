# Testing Guide - Q-IDE

## Overview
Q-IDE uses a comprehensive testing strategy covering unit tests, integration tests, and end-to-end tests.

## Test Structure

```
frontend/
  src/
    __tests__/          # Unit tests
    hooks/
      __tests__/        # Hook tests
    components/
      __tests__/        # Component tests
  e2e/
    *.spec.ts           # E2E tests (Playwright)

backend/
  tests/                # Python unit tests
  __tests__/            # Pytest configuration
```

## Running Tests

### Frontend Unit Tests
```bash
cd frontend

# Run all tests
pnpm test

# Run specific test file
pnpm test App.test.tsx

# Run with coverage
pnpm test -- --coverage

# Watch mode for development
pnpm test -- --watch
```

### Frontend E2E Tests
```bash
cd frontend

# Prerequisites: dev server running on localhost:1431
pnpm run dev &
sleep 3

# Run all E2E tests
pnpm exec playwright test

# Run specific test
pnpm exec playwright test e2e/background-flow.spec.ts

# Run in headed mode (see browser)
pnpm exec playwright test --headed

# Run with single worker (slower but more stable)
pnpm exec playwright test --workers=1
```

### Backend Tests
```bash
cd backend

# Run all tests
python -m pytest -v

# Run specific test file
python -m pytest tests/test_auth.py -v

# Run with coverage
python -m pytest --cov=. tests/ -v

# Run specific test
python -m pytest tests/test_auth.py::test_create_session -v
```

## Writing Tests

### Unit Test Example (React Component)

```typescript
// components/__tests__/BackgroundSettings.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import BackgroundSettings from '../BackgroundSettings';

describe('BackgroundSettings', () => {
  it('renders preset buttons', () => {
    render(<BackgroundSettings />);
    expect(screen.getByText(/Gradient/i)).toBeInTheDocument();
  });

  it('changes background kind when preset is clicked', () => {
    render(<BackgroundSettings />);
    fireEvent.click(screen.getByText(/Particles/i));
    expect(screen.getByLabelText(/Particle density/i)).toBeInTheDocument();
  });
});
```

### Unit Test Example (Hook)

```typescript
// hooks/__tests__/useBackground.test.ts
import { renderHook, act } from '@testing-library/react';
import useBackground from '../useBackground';

describe('useBackground', () => {
  it('returns default gradient setting', () => {
    const { result } = renderHook(() => useBackground());
    const [setting] = result.current;
    expect(setting.kind).toBe('gradient');
  });

  it('updates setting when setSetting is called', () => {
    const { result } = renderHook(() => useBackground());
    act(() => {
      result.current[1]({ kind: 'particles', particleCount: 50 });
    });
    expect(result.current[0].kind).toBe('particles');
  });
});
```

### E2E Test Example (Playwright)

```typescript
// e2e/example.spec.ts
import { test, expect } from '@playwright/test';

test('user can navigate to settings', async ({ page }) => {
  await page.goto('http://localhost:1431/');
  
  // Click settings button
  const settingsBtn = page.getByRole('button', { name: /Settings/i });
  await expect(settingsBtn).toBeVisible();
  await settingsBtn.click();
  
  // Verify settings panel is visible
  expect(page.url()).toContain('settings');
});
```

## Test Coverage Goals

| Area | Target | Current |
|------|--------|---------|
| Frontend Components | 80% | -- |
| Frontend Hooks | 85% | -- |
| Backend API | 90% | -- |
| Overall | 85% | -- |

## Continuous Integration

Tests run automatically on:
- **Pull Requests**: All tests must pass before merge
- **Commits to main**: Tests verify stable build
- **Release tags**: Full test suite + build verification

### GitHub Actions Workflow
See `.github/workflows/build-and-release.yml` for CI/CD configuration.

## Performance Testing

### Bundle Analysis
```bash
cd frontend
pnpm run build -- --analyze

# Outputs bundle-report.html
```

### Runtime Performance
```bash
cd frontend
pnpm run dev

# Open browser DevTools → Performance tab
# Record a trace and analyze
```

## Debugging Tests

### Frontend Debugging
```bash
# Run tests with debugger
node --inspect-brk node_modules/.bin/jest --runInBand

# Run Playwright headed with debug
pnpm exec playwright test --headed --debug
```

### Backend Debugging
```bash
# Run with Python debugger
python -m pdb backend/main.py

# Or use breakpoints with IDE
# pytest -k test_name --pdb
```

## Test Data Management

### Fixtures (Playwright)
```typescript
// fixtures for reusable test data
const mockUser = {
  id: '123',
  email: 'test@example.com',
  name: 'Test User'
};
```

### Mocking APIs
```typescript
// Mock backend responses
page.route('/api/builds', route => {
  route.abort('blockedreason');
  // or
  route.continue({ response: mockResponse });
});
```

## Best Practices

1. **Test Behavior, Not Implementation**
   - Test what users see and do
   - Avoid testing internal state

2. **Keep Tests Isolated**
   - Each test should be independent
   - Clean up resources after tests

3. **Use Descriptive Names**
   ```typescript
   // Good
   test('uploads image and shows preview')
   
   // Bad
   test('test upload')
   ```

4. **Avoid Flaky Tests**
   - Use appropriate waits (waitFor, expect with timeout)
   - Don't rely on sleep timings
   - Mock external dependencies

5. **Test Edge Cases**
   - Empty states
   - Error states
   - Large data sets
   - User errors

## Troubleshooting

### E2E Tests Timeout
```bash
# Increase timeout in playwright.config.ts
timeout: 30 * 1000,  // 30 seconds
```

### Port Already in Use
```bash
# Kill process on port 1431
lsof -i :1431 | grep -v PID | awk '{print $2}' | xargs kill -9  # macOS/Linux
netstat -ano | findstr :1431  # Windows - then taskkill /PID
```

### Module Not Found
```bash
# Clear cache and reinstall
rm -rf node_modules pnpm-lock.yaml
pnpm install
pnpm test
```

## Resources

- [Jest Documentation](https://jestjs.io/)
- [React Testing Library](https://testing-library.com/react)
- [Playwright Documentation](https://playwright.dev/)
- [pytest Documentation](https://docs.pytest.org/)

---

**Version**: 0.1.0  
**Last Updated**: October 2025
