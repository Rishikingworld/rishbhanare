import os
import random
import subprocess
import time
from pathlib import Path

import requests
import torch
from PIL import Image
from diffusers import StableVideoDiffusionPipeline
from diffusers.utils import export_to_video
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "input" / "source.png"
OUTPUT_DIR = ROOT / "public-media"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

load_dotenv(ROOT / ".env")

IG_USER_ID = os.environ["IG_USER_ID"]
IG_ACCESS_TOKEN = os.environ["IG_ACCESS_TOKEN"]
GITHUB_PUBLIC_BASE = os.environ["GITHUB_PUBLIC_BASE"].rstrip("/")
MODEL_ID = os.getenv("MODEL_ID", "stabilityai/stable-video-diffusion-img2vid-xt")
FPS = int(os.getenv("FPS", "7"))

CAPTIONS = [
    "A little moment, a little motion, and a whole mood.",
    "Keeping it simple, natural, and in the moment.",
    "Just another frame turned into a memory.",
    "Soft light, natural vibes, and a little movement.",
]
HASHTAGS = "#reels #instagramreels #aivideo #photorealistic #dailyreel #creator"


def run(cmd, cwd=ROOT):
    subprocess.run(cmd, cwd=cwd, check=True)


def make_vertical_source(image: Image.Image) -> Image.Image:
    # Prepare a portrait image while keeping the subject centered.
    image = image.convert("RGB")
    target_ratio = 9 / 16
    w, h = image.size
    ratio = w / h
    if ratio > target_ratio:
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        image = image.crop((left, 0, left + new_w, h))
    elif ratio < target_ratio:
        new_h = int(w / target_ratio)
        top = max(0, (h - new_h) // 2)
        image = image.crop((0, top, w, min(h, top + new_h)))
    return image.resize((576, 1024), Image.Resampling.LANCZOS)


def generate_video() -> Path:
    if not INPUT.exists():
        raise FileNotFoundError(f"Missing source image: {INPUT}")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    if device != "cuda":
        raise RuntimeError("A local NVIDIA CUDA GPU is required for practical free local video generation.")

    image = make_vertical_source(Image.open(INPUT))
    # SVD expects a 16:9 conditioning frame. Resize only for model input, then crop output back to 9:16.
    model_image = image.resize((1024, 576), Image.Resampling.LANCZOS)

    dtype = torch.float16
    pipe = StableVideoDiffusionPipeline.from_pretrained(
        MODEL_ID,
        torch_dtype=dtype,
        variant="fp16",
    )
    pipe.enable_model_cpu_offload()

    generator = torch.manual_seed(random.randint(1, 2**31 - 1))
    frames = pipe(
        model_image,
        decode_chunk_size=2,
        motion_bucket_id=random.randint(90, 125),
        noise_aug_strength=0.02,
        generator=generator,
    ).frames[0]

    # Convert 1024x576 frames into a 9:16 Reel by center-cropping and resizing.
    vertical_frames = []
    for frame in frames:
        frame = Image.fromarray(frame).convert("RGB")
        crop_w = int(frame.height * 9 / 16)
        left = (frame.width - crop_w) // 2
        frame = frame.crop((left, 0, left + crop_w, frame.height))
        vertical_frames.append(frame.resize((1080, 1920), Image.Resampling.LANCZOS))

    filename = time.strftime("reel_%Y%m%d_%H%M%S.mp4")
    output = OUTPUT_DIR / filename
    export_to_video(vertical_frames, str(output), fps=FPS)
    return output


def publish_instagram(video_url: str, caption: str) -> dict:
    base = "https://graph.facebook.com/v23.0"
    create = requests.post(
        f"{base}/{IG_USER_ID}/media",
        data={
            "media_type": "REELS",
            "video_url": video_url,
            "caption": caption,
            "share_to_feed": "true",
            "access_token": IG_ACCESS_TOKEN,
        },
        timeout=60,
    )
    create.raise_for_status()
    creation_id = create.json()["id"]

    for _ in range(60):
        status = requests.get(
            f"{base}/{creation_id}",
            params={"fields": "status_code,status", "access_token": IG_ACCESS_TOKEN},
            timeout=30,
        )
        status.raise_for_status()
        data = status.json()
        if data.get("status_code") == "FINISHED":
            break
        if data.get("status_code") in {"ERROR", "EXPIRED"}:
            raise RuntimeError(f"Instagram media processing failed: {data}")
        time.sleep(10)
    else:
        raise TimeoutError("Instagram did not finish processing the Reel within the timeout.")

    publish = requests.post(
        f"{base}/{IG_USER_ID}/media_publish",
        data={"creation_id": creation_id, "access_token": IG_ACCESS_TOKEN},
        timeout=60,
    )
    publish.raise_for_status()
    return publish.json()


def main():
    output = generate_video()

    # Commit the generated MP4 to the public repository so Meta can fetch it.
    run(["git", "add", str(output.relative_to(ROOT))])
    run(["git", "commit", "-m", f"Add generated Reel {output.name}"])
    run(["git", "push", "origin", os.getenv("GITHUB_BRANCH", "main")])

    public_url = f"{GITHUB_PUBLIC_BASE}/{output.name}"
    for _ in range(30):
        try:
            response = requests.get(public_url, stream=True, timeout=20)
            if response.status_code == 200:
                break
        except requests.RequestException:
            pass
        time.sleep(5)
    else:
        raise RuntimeError(f"Generated video is not publicly reachable yet: {public_url}")

    caption = os.getenv("CAPTION", f"{random.choice(CAPTIONS)}\n\n{HASHTAGS}")
    result = publish_instagram(public_url, caption)
    print("Published Instagram Reel:", result)
    print("Video URL:", public_url)


if __name__ == "__main__":
    main()
