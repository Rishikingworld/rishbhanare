# Free Instagram AI Video Bot

This project is designed to run locally with open/free-to-use AI tooling instead of a paid video-generation API.

## Pipeline

1. Put the day's portrait/photo in `input/source.png`.
2. Animate it locally with Stable Video Diffusion (image-to-video).
3. Export a vertical 9:16 MP4.
4. Push the MP4 to this public GitHub repository so Instagram can fetch a public media URL.
5. Publish the Reel through the official Instagram Graph API.

> Important: the AI model itself is free/open weights, but running it requires your own computer/GPU. This avoids per-video Runway/OpenArt API charges; it does not provide free cloud GPU compute.

## Requirements

- Python 3.10+
- NVIDIA GPU with enough VRAM for the selected Diffusers model (CPU is generally impractical for video generation).
- Git installed and authenticated for this repository.
- An Instagram Professional account connected to a Facebook Page, with an Instagram Graph API access token and the required permissions.

## Setup

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Fill in `.env` and place a source image at `input/source.png`.

Run:

```bash
python generate_and_publish.py
```

The script creates a vertical Reel, uploads it to the public GitHub repo through git, waits briefly for the raw URL to become available, and publishes it with Instagram Graph API.

## Scheduling

Use Windows Task Scheduler, cron, or a local always-on machine to run the script daily. Do not put API tokens in GitHub source files; keep them in `.env` or your machine's secret store.

## Limitations

- This is not an unlimited free cloud service. Local GPU compute is required.
- Stable Video Diffusion animates an existing image; it is not a full text-to-video cinematic model.
- Instagram API publishing has Meta's own account/API restrictions.
- AI-generated/altered content should be disclosed where required by Instagram.
