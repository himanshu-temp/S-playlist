import os
import re
import json
import requests
from dotenv import load_dotenv

# === Load env variables ===
load_dotenv()
SOURCE_URL = os.environ.get("SOURCE_URL")
CHANNEL_GROUPS_RAW = os.getenv("CHANNEL_GROUPS")

if not SOURCE_URL or not CHANNEL_GROUPS_RAW:
    print("❌ SOURCE_URL or CHANNEL_GROUPS not set in .env")
    exit()

# Convert CHANNEL_GROUPS JSON string to dict
try:
    channel_groups = json.loads(CHANNEL_GROUPS_RAW)
except json.JSONDecodeError as e:
    print(f"❌ Invalid CHANNEL_GROUPS format: {e}")
    exit()

# Create lowercase lookup for allowed channels
allowed_channels = {}
for group, channels in channel_groups.items():
    for name in channels:
        allowed_channels[name.lower()] = group

# === Your custom EXTINF replacements ===
custom_channel_data = {
  "sony yay": {
    "tvg-id": "",
    "tvg-name": "Sony Yay",
    "tvg-logo": "http://jiotv.catchup.cdn.jio.com/dare_images/images/Sony_Yay_Hindi.png",
    "display-name": "Sony Yay"
  },
  "sony max hd": {
    "tvg-id": "sonymaxhd.in",
    "tvg-name": "Sony Max HD",
    "tvg-logo": "https://watchindia.net/images/channels/hindi/Sony_Max_HD.png",
    "display-name": "Sony MAX HD"
  },
  "sony max": {
    "tvg-id": "",
    "tvg-name": "Sony MAX",
    "tvg-logo": "http://jiotv.catchup.cdn.jio.com/dare_images/images/SET_MAX.png",
    "display-name": "Sony MAX"
  },
  "sony sab hd": {
    "tvg-id": "sonysabhd.in",
    "tvg-name": "Sony Sab HD",
    "tvg-logo": "https://watchindia.net/images/channels/hindi/Sony_Sab_HD.png",
    "display-name": "Sony SAB HD"
  },
  "set hd": {
    "tvg-id": "sonyhd.in",
    "tvg-name": "Sony TV HD",
    "tvg-logo": "https://watchindia.net/images/channels/hindi/Sony_TV_HD.png",
    "display-name": "SET HD"
  },
  "sony pal": {
    "tvg-id": "",
    "tvg-name": "Sony Pal",
    "tvg-logo": "http://jiotv.catchup.cdn.jio.com/dare_images/images/Sony_Pal.png",
    "display-name": "Sony Pal"
  },
  "sony bbc earth hd": {
    "tvg-id": "",
    "tvg-name": "Sony BBC Earth HD",
    "tvg-logo": "http://jiotv.catchup.cdn.jio.com/dare_images/images/Sony_BBC_Earth_HD.png",
    "display-name": "Sony BBC Earth HD"
  }
}

# === Fetch playlist ===
print(f"📥 Fetching playlist from: {SOURCE_URL}")
try:
    response = requests.get(SOURCE_URL)
    response.raise_for_status()
    lines = response.text.splitlines()
except Exception as e:
    print(f"❌ Error fetching playlist: {e}")
    exit()

# === Process 2-line blocks ===
output_blocks = []
i = 0
while i + 1 < len(lines):
    if lines[i].startswith("#EXTINF:") and lines[i+1].startswith("http"):
        extinf = lines[i]
        url = lines[i+1]
        channel_name = extinf.split(",")[-1].strip()
        group = allowed_channels.get(channel_name.lower())

        if group:
            channel_key = channel_name.lower()
            custom_info = custom_channel_data.get(channel_key)

            if custom_info:
                updated_extinf = (
                    f'#EXTINF:-1 '
                    f'tvg-id="{custom_info.get("tvg-id", "")}" '
                    f'tvg-name="{custom_info.get("tvg-name", "")}" '
                    f'tvg-logo="{custom_info.get("tvg-logo", "")}" '
                    f'group-title="{group}",' 
                    f'{custom_info.get("display-name", channel_name)}'
                )
            else:
                # fallback: only update group-title
                if 'group-title="' in extinf:
                    updated_extinf = re.sub(r'group-title=".*?"', f'group-title="{group}"', extinf)
                else:
                    updated_extinf = extinf.replace(",", f' group-title="{group}",', 1)

            output_blocks.append(f"{updated_extinf}\n{url}")
        i += 2
    else:
        i += 1

# === Write output ===
output_file = "Sony.m3u"
if output_blocks:
    print(f"✅ Found {len(output_blocks)} categorized channels.")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n# Updated By Himanshu\n\n")
        for block in output_blocks:
            f.write(block + "\n")
else:
    print("⚠️ No matching channels found.")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n# No matching channels found\n")

os.chmod(output_file, 0o666)
print(f"✅ '{output_file}' written successfully.")
