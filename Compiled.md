---
tags:
  - THM
  - Easy
  - Challenge
  - File-Analysis
---
https://tryhackme.com/room/compiled/
# Binary analysis
We are given a binary named `Compiled.Compiled`.

We are asked for a password when executing it:
```console
$ ./Compiled.Compiled

Password: abc
Try again!
```
Using Ghidra, we get the source code:
```c
undefined8 main(void)

{
  int iVar1;
  char local_28 [32];

  fwrite("Password: ",1,10,stdout);
  __isoc99_scanf("DoYouEven%sCTF",local_28);
  iVar1 = strcmp(local_28,"__dso_handle");
  if ((-1 < iVar1) && (iVar1 = strcmp(local_28,"__dso_handle"), iVar1 < 1)) {
    printf("Try again!");
    return 0;
  }
  iVar1 = strcmp(local_28,"_init");
  if (iVar1 == 0) {
    printf("Correct!");
  }
  else {
    printf("Try again!");
  }
  return 0;
}
```
Create our own `Test.c` file to understand the binary's behavior:
```c
#include <stdio.h>

int main() {
    char local_28[32];
    printf("Password: ");
    scanf("DoYouEven%sCTF", local_28);
    printf("Value: %s\n", local_28);
    return 0;
}
```
Only the content after `DoYouEven` is being saved:
```console
$ gcc -o Test Test.c

$ ./Test
Password: DoYouEven%sCTF
Value: %sCTF
```
Looking at the source code, we need that content to be `_init_` and get the **password**:
```console
$ ./Compiled.Compiled

Password: DoYouEven_init
Correct!
```