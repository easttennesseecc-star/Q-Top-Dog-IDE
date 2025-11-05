import React from 'react';

export type Provider = {
  provider: string;
  signup_url: string;
  docs_url: string;
  key_env_var?: string;
  models_examples?: string[];
  notes?: string;
};

export interface LLMDirectoryPanelProps {
  providers: Provider[];
  className?: string;
}

export const LLMDirectoryPanel: React.FC<LLMDirectoryPanelProps> = ({ providers, className }) => {
  return (
    <div className={className ?? ''}>
      <h2>LLM Provider Directory (BYOK)</h2>
      <p>
        Bring your own provider API keys and paste them into Aura Development. Your usage is billed by providers; Top Dog subscriptions cover IDE features.
      </p>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: 16 }}>
        {providers.map((p) => (
          <div key={p.provider} style={{ border: '1px solid #e0e0e0', borderRadius: 8, padding: 12 }}>
            <h3 style={{ margin: '4px 0 8px' }}>{p.provider}</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
              <a href={p.signup_url} target="_blank" rel="noreferrer">Get API Key</a>
              <a href={p.docs_url} target="_blank" rel="noreferrer">Docs</a>
              {p.key_env_var && (
                <div><strong>Env Var:</strong> <code>{p.key_env_var}</code></div>
              )}
              {p.models_examples && p.models_examples.length > 0 && (
                <div>
                  <strong>Examples:</strong>
                  <ul style={{ margin: '6px 0 0 18px' }}>
                    {p.models_examples.slice(0, 3).map((m) => (
                      <li key={m}>{m}</li>
                    ))}
                  </ul>
                </div>
              )}
              {p.notes && <div style={{ fontSize: 12, color: '#666' }}>{p.notes}</div>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default LLMDirectoryPanel;
