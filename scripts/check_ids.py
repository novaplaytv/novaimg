import gzip
import re

try:
    with gzip.open('guide.xml.gz', 'rb') as f:
        content = f.read().decode('utf-8')
        ids = re.findall(r'channel id="([^"]+)"', content)
        print(f"Total IDs: {len(ids)}")
        for i in ids[:200]:
            print(i)
except Exception as e:
    print(f"Error: {e}")
