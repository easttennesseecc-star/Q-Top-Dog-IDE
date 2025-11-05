# LLMDirectoryPanel

A simple React component that renders provider cards from a list, intended to be fed by `marketplace/LLM_DIRECTORY.json`.

## Usage

```tsx
import React, { useEffect, useState } from 'react';
import LLMDirectoryPanel, { Provider } from './LLMDirectoryPanel';

export const LLMDirectoryExample: React.FC = () => {
  const [providers, setProviders] = useState<Provider[]>([]);

  useEffect(() => {
    fetch('/marketplace/LLM_DIRECTORY.json')
      .then((r) => r.json())
      .then(setProviders)
      .catch(() => setProviders([]));
  }, []);

  return <LLMDirectoryPanel providers={providers} />;
};
```

Notes
- Ensure your web server serves the repository root so `/marketplace/LLM_DIRECTORY.json` is resolvable at runtime; otherwise, adjust the fetch path.
- The component is UI-only; BYOK secrets and validations should be handled in your existing settings flows.
