#!/usr/bin/env python3
"""Trend-to-prompt engine for the Instagram bot.

Fetches India trending topics from Google Trends RSS and Google News RSS,
filters out unsafe/irrelevant topics, and writes a fresh photo-to-video prompt.
This module intentionally does not contain any API secrets.
"""
from __future__ import annotations

import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

BASE = Path(__file__).resolve().parent
OUT = BASE / "output"
OUT.mkdir(exist_ok=True)
PROMPT_FILE = OUT / "latest_video_prompt.txt"
TREND_FILE = OUT / "latest_trend.txt"

HEADERS = {"User-Agent": "Mozilla/5.0 (Android; Termux) InstagramTrendBot/1.0"}


def fetch_xml(url: str) -> bytes:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read()


def text_of(el: ET.Element | None) -> str:
    return (el.text or "").strip() if el is not None else ""


def google_trends_india() -> list[str]:
    url = "https://trends.google.com/trending/rss?geo=IN"
    root = ET.fromstring(fetch_xml(url))
    out: list[str] = []
    for item in root.iter():
        if item.tag.endswith("item"):
            title = next((text_of(c) for c in item if c.tag.endswith("title")), "")
            if title:
                out.append(title)
    return out


def google_news_india() -> list[str]:
    q = urllib.parse.quote("India trending OR viral OR Instagram")
    url = f"https://news.google.com/rss/search?q={q}&hl=en-IN&gl=IN&ceid=IN:en"
    root = ET.fromstring(fetch_xml(url))
    out: list[str] = []
    for item in root.iter():
        if item.tag.endswith("item"):
            title = next((text_of(c) for c in item if c.tag.endswith("title")), "")
            if title:
                out.append(re.sub(r"\s+-\s+[^-]+$", "", title).strip())
    return out


def clean_topic(topic: str) -> str:
    topic = re.sub(r"\s+", " ", topic).strip()
    return topic[:180]


def choose_topic(items: list[str]) -> str:
    blocked = ("death", "murder", "suicide", "explicit", "porn", "war crime", "gore")
    for raw in items:
        t = clean_topic(raw)
        if t and not any(x in t.lower() for x in blocked):
            return t
    return "India lifestyle and fashion trend"


def build_prompt(topic: str) -> str:
    return f"""PHOTO_TO_VIDEO_TASK

TREND:
Create a short Instagram Reel inspired by this currently trending India topic:
{topic}

IDENTITY:
Use the provided reference photo as the identity source.
Keep the same recognizable face identity, facial structure, eyes, nose, lips,
jawline, skin tone and distinctive facial features. Do not redesign or replace
identity. Keep the person naturally recognizable.

CREATIVE DIRECTION:
Interpret the trend as a tasteful, realistic lifestyle/fashion concept.
Invent a fresh scene, outfit, styling and composition that fit the trend.
Do not copy a celebrity or copyrighted character.

EMOTION:
Choose an expression that naturally matches the trend: confident, happy,
curious, calm, playful or thoughtful. Keep facial expression consistent.

CLOTHING:
Choose a complete realistic outfit appropriate to the concept, including
fabric, color, footwear and tasteful accessories. Make cloth folds and motion
physically believable.

ACTION:
Create a clear human action sequence: natural walking, turning, looking at
camera, subtle hand movement, hair movement or interaction with the scene.
Avoid frozen-face motion. Keep anatomy stable throughout.

BACKGROUND:
Photorealistic real-world location that naturally fits the trend. Match
perspective, depth, lighting, shadows and reflections to the subject.

CAMERA:
Vertical 9:16 Reel. Cinematic tracking/dolly movement, subtle depth of field,
natural motion blur, realistic 24/30 fps appearance.

LIGHTING:
Natural realistic lighting appropriate to the location and time of day.

QUALITY:
Photorealistic, natural skin texture, realistic hair, realistic cloth physics,
stable hands and body, temporal consistency, no flicker.

NEGATIVE:
identity change, face replacement, face distortion, age change, warped face,
extra fingers, missing fingers, deformed hands, duplicate limbs, rubbery body,
melting clothing, flicker, frame jumps, unstable background, artificial skin,
text artifacts, logos, watermarks, celebrity imitation.
"""


def main() -> int:
    trends: list[str] = []
    errors: list[str] = []
    for fn, label in ((google_trends_india, "Google Trends"), (google_news_india, "Google News")):
        try:
            trends.extend(fn())
        except Exception as exc:
            errors.append(f"{label}: {exc}")
    topic = choose_topic(trends)
    prompt = build_prompt(topic)
    TREND_FILE.write_text(topic + "\n", encoding="utf-8")
    PROMPT_FILE.write_text(prompt, encoding="utf-8")
    print("TREND:", topic)
    print("PROMPT:", PROMPT_FILE)
    if errors:
        print("WARNINGS:")
        for e in errors:
            print("-", e)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
