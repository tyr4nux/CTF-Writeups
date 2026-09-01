---
tags:
  - HTB
  - Linux
  - Easy
---
https://app.hackthebox.com/machines/MACHINE/

# Add Hosts

Append to the `/etc/hosts` file:

```text
<IP-TARGET> <MACHINE>.htb
```

# Enumeration

Port scanning:

```console
$ nmap -p<PORT1,PORT2> -sV -sC <MACHINE>.htb

PORT   STATE   SERVICE   VERSION
```

FTP, whatweb, fuzzing automation, etc.

# Extra step

Any extra step?

# Exploitation

Gaining access (SQL injection, XSS, SSRF, RCE, etc).

# Post-Exploitation

Privilege escalation steps.

# Notes

- Add steps to get user and root flags.
- Remember to change the tags.