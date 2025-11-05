# Production Verification Plan (Flip 🟡 to ✅)

Record proof points (URLs, screenshots, logs) as you validate. Update the main features doc accordingly.

- Authentication
  - [ ] Email/password sign-up and login
    - Proof: screenshot of successful login and user record in DB
  - [ ] OAuth login (GitHub/Google/Microsoft)
    - Proof: screenshot of consent + returned session

- Billing (Stripe)
  - [ ] Subscribe to PRO (webhook processed)
    - Proof: Stripe event logs + app subscription state updated
  - [ ] Upgrade/downgrade; verify proration and invoice
    - Proof: Stripe invoice + app plan reflected
  - [ ] Cancel subscription; access changes, invoice generated
    - Proof: app access downgraded + Stripe invoice

- LLM Orchestration (BYOK)
  - [ ] Configure at least two providers (OpenAI + Anthropic)
    - Proof: masked keys present in settings; test call success
  - [ ] Chat request streams, token/cost displayed
    - Proof: video or GIF of UI + logs
  - [ ] Model switch mid‑conversation
    - Proof: UI transcript showing both models

- Agents
  - [ ] Create + run agent; tools and logs present
    - Proof: agent run log with timestamps
  - [ ] Approval gate pause/resume
    - Proof: UI screenshot of approval step

- Collaboration
  - [ ] Two users edit same file; presence/cursors/chat
    - Proof: short video of session
  - [ ] Screen share + optional recording
    - Proof: saved recording reference

- Game Engines
  - [ ] Select engine per tier; toggles active
    - Proof: settings page screenshot
  - [ ] In‑IDE test session launches
    - Proof: UI capture of test run

- Media Synthesis
  - [ ] Trigger DALL·E/Midjourney/Runway; asset saved
    - Proof: media library entry with metadata

- Observability
  - [ ] Centralized logs capture client/server errors
    - Proof: query screenshot
  - [ ] Uptime monitor for frontend and API
    - Proof: status page links
