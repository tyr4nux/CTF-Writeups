#!/usr/bin/python3

import re
import requests
from pathlib import Path


for file in Path(__file__).parent.parent.glob('*.md'):
    url = re.search(r"^https?.*$", file.read_text(), re.MULTILINE).group(0)

    # Get title according to the platform
    if 'hackthebox' in url:
        title = re.search(r"(?<=\/machines\/).*", url).group(0).removesuffix('/')
    elif 'tryhackme' in url:
        room_code = re.search(r"(?<=\/room\/).*", url).group(0).removesuffix('/')
        title = requests.get(f"https://tryhackme.com/api/v2/rooms/details?roomCode={room_code}").json()['data']['title']
    elif 'vulnhub' in url:
        web = requests.get(url).text
        title = re.search(r"(?<=<title>).*?(?=</title>)", web).group(0).removesuffix('~ VulnHub').strip()

    # Compare the filename with the machine's title
    while ':' in title:
        title = title.replace(':', '')
    if file.stem != title:
        print(f"{title}\t{file.resolve()}\t{url}")

