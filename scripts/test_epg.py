import json
import urllib.request
import os

CHANNELS_API = 'https://iptv-org.github.io/api/channels.json'
GUIDES_API = 'https://iptv-org.github.io/api/guides.json'

TARGET_COUNTRIES = ['AR', 'PY', 'UY', 'MX', 'CL', 'CO', 'PE']
ENABLED_SITES = ['mi.tv', 'gatotv.com', 'directv.com.ar', 'reportv.com.ar']

def get_json(url):
    with urllib.request.urlopen(url) as response:
        return json.loads(response.read().decode())

try:
    print("Fetching channels...")
    channels = get_json(CHANNELS_API)
    channel_meta = {}
    for ch in channels:
        codes = [c['code'] for c in ch.get('countries', [])]
        if any(c in TARGET_COUNTRIES for c in codes):
            channel_meta[ch['id']] = ch.get('name', '')

    print(f"Channels in target countries: {len(channel_meta)}")

    print("Fetching guides...")
    guides = get_json(GUIDES_API)
    count = 0
    for g in guides:
        ch_id = g.get('channel')
        site = g.get('site')
        if ch_id in channel_meta and site in ENABLED_SITES:
            count += 1
            if count < 5:
                print(f"Match: {ch_id} on {site}")

    print(f"Total matches: {count}")

except Exception as e:
    print(f"Error: {e}")
