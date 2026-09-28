# Free Social Video Automation (Android + Termux)

Backup of the free-only automation project.

## Run on a new device
pkg update -y && pkg install -y python ffmpeg git
git clone https://github.com/Rishikingworld/rishbhanare.git
cd rishbhanare/free-social-video-automation
pip install -r requirements.txt
cp .env.example .env
python auto.py

The default mode is DRY_RUN=true. It creates a video locally and does not publish.
Keep API keys/tokens OUT of GitHub. Add them again in .env on each device.

Pipeline:
Google News RSS -> topic selection -> Hindi script -> Edge TTS -> original cartoon panels -> FFmpeg 9:16 MP4 -> metadata -> YouTube/Meta publishing adapters.

YouTube uses the official YouTube Data API. Instagram/Facebook publishing requires the appropriate Meta account/app permissions and a publicly reachable video URL for Reels publishing.
