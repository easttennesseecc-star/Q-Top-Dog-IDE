# Easy Setup Guide — Top Dog by Quellum

The fastest path to a working environment. No deep configuration, just keys where needed and simple API calls.

1) Brand & Editions
- Company: Quellum
- Brand: Top Dog (autonomous IDE)
- Editions: Aura Developer, Aura Medical, Aura Scientific

2) Game Engines (all four)
- Construct 3: See docs/containers/CONSTRUCT3_CONTAINER_README.md (export HTML5, then one POST)
- Godot & Unreal: Already supported via containers (POST /api/v1/game-engine/containers/start)
- GameMaker: Scaffolded (license + installer required). See docs/containers/GAMEMAKER_CONTAINER_README.md

3) Media Providers (DALL·E 3, Midjourney proxy, Runway, Stable Diffusion)
- See docs/media/PROVIDERS_QUICK_SETUP.md for direct links and one-call configure API

4) Verified Code (Overwatch)
- Integrated in chat path; quotas set by tier. See FEATURES_ATTESTATION_REPORT.md for code pointers

5) SSO & Teams
- OAuth (Google/GitHub) wired; billing and role system present. See backend/main.py and frontend billing pages

Need even simpler?
- I can create a minimal web form for /media/configure that stores keys locally for dev and shows provider status live. Say the word.
