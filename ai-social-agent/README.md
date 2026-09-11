# AI Social Media Multi-Agent

Auto-mode architecture for creating and distributing original video content across connected social platforms.

## Pipeline

Research -> Strategy -> Script -> Fact Check -> Voice -> Visuals -> Edit -> Captions -> Thumbnail -> QA -> Platform Adaptation -> Publish/Schedule -> Analytics -> Learning.

## Agents

- Research Agent: discovers India-relevant trends and evergreen topics.
- Strategy Agent: selects topic, angle, hook, audience, duration and platform mix.
- Script Agent: writes original Hindi/Hinglish/English scripts.
- Fact Check Agent: verifies current claims and flags uncertain facts.
- Media Agent: coordinates video, image, voice and music generation.
- Editor Agent: assembles platform-specific videos.
- Metadata Agent: creates titles, descriptions, hashtags and thumbnail briefs.
- QA Agent: checks audio, captions, aspect ratio, factual/copyright/policy risks.
- Publisher Agent: publishes only through official APIs/integrations and only to explicitly connected accounts.
- Analytics Agent: collects performance metrics and feeds learnings back into strategy.

## Auto mode

Set `AUTO_PUBLISH=true` only after OAuth/API connections are configured. If a platform has no supported official publishing API for the connected account, the workflow stops at `READY_TO_PUBLISH` instead of attempting credential/browser bypasses.

## Secrets

Never commit API keys, OAuth client secrets, access tokens, refresh tokens, or passwords. Store them in the deployment platform's secret manager / environment variables.

## Planned platform adapters

YouTube, Instagram, Facebook, ShareChat, Moj, Josh, Chingari, Roposo, Snapchat, LinkedIn, X, Pinterest, Telegram Channels and WhatsApp Channels, subject to each platform's current official API and account eligibility.
