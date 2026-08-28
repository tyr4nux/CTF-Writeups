---
tags:
  - HTB
  - Easy
  - Challenge
---
https://app.hackthebox.com/challenges/SpookyPass/
# Add Hosts
Append to the `/etc/hosts` file:
```text
<IP-TARGET> <MACHINE>.htb <SUBDOMAIN>.<MACHINE>.htb
```
Found subdomain `<SUBDOMAIN>`.
# Scanning
```console
$ nmap -p<PORT1,PORT2> -sV -sC <MACHINE>.htb

PORT   STATE   SERVICE   VERSION
```
# Discovery
Check website (what is on it), HTML comments, OSINT.
# Enumeration
FTP, whatweb, fuzzing automation.
# Extra step
Any extra step?
# Exploitation
Gaining access (SQL injection, XSS, SSRF, RCE, etc).
# Post-Exploitation
Privilege escalation steps.
# Notes
- Add steps to get user and root flags.
- Remember to change the tags.