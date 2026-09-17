---
tags:
  - HTB
  - Linux
  - Easy
---
# Information

- Machine: [Name](https://app.hackthebox.com/machines/MACHINE)
- Target: `<TARGET>`
- Attacker: `<ATTACKER>`

# Enumeration

## Ports

Scanned all TCP ports:

```console
$ sudo nmap -p- --open -sS -Pn -n <TARGET>

PORT   STATE   SERVICE
```

Service version detection for open ports:

```console
$ nmap -p<PORTS> -sV -sC <TARGET>

PORT   STATE   SERVICE   VERSION
```

Append to the `/etc/hosts` file:

```text
<TARGET> <MACHINE>.htb
```

## Subdomains

Detected nginx reverse proxy running:

```console
$ whatweb 'http://<TARGET>'
```

Found subdomains:

```console
$ ffuf -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt -H 'Host: FUZZ.<MACHINE>.htb' -u 'http://<MACHINE>.htb'
```

Modified the `/etc/hosts` file:

```text
<TARGET> <MACHINE>.htb <SUB>.<MACHINE>.htb
```

## Web

Gobuster, ffuf, nikto, etc.

## Extra

SSH, FTP, Telnet, etc.

# Exploitation

Gaining access (SQL injection, XSS, SSRF, RCE, etc).

# Post-Exploitation

Privilege escalation steps.

# Notes

- Check [information](#Information).
- Change `<TARGET>`, `<MACHINE>`, `<PORTS>`, `<SUB>`, `<ATTACKER>`.
- Add user flag step.
- Add root flag step.
- Change tags.