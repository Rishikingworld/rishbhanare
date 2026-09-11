# YouTube Auto-Publishing Setup

## 1. Google Cloud

Create/select a Google Cloud project and enable **YouTube Data API v3**.

Create an OAuth 2.0 Client ID for a desktop application and download the JSON file.

Place it locally at:

`secrets/client_secret.json`

Do not commit this file.

## 2. First authorization

Install dependencies:

```bash
pip install -r requirements-social-agent.txt
```

Then run:

```bash
python -m agents.publishers.youtube_publisher ./output/video.mp4 --title "My AI Video" --privacy private
```

A Google authorization page will open. Sign in with the Google account that owns the target YouTube channel and grant the requested YouTube upload permission.

The refresh token is stored locally in `secrets/youtube_token.json`; keep that file private and never commit it.

## 3. Auto Mode publishing

For safe first testing, use `--privacy private`. After the account and API project are verified, Auto Mode can use `public` or a scheduled `publishAt` timestamp according to the project's publishing policy.

YouTube's `videos.insert` API requires OAuth authorization and supports metadata such as title, description, tags, privacy status and scheduled publication. New/unverified API projects created after July 28, 2020 can have uploads restricted to private viewing until the project completes Google's audit process.

## 4. Production secret storage

For GitHub Actions or a hosted deployment, store OAuth credentials/tokens in the deployment platform's encrypted secret store. Never put access tokens, refresh tokens, client secrets, or API keys in Git commits.
