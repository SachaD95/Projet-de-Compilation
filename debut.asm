extern printf ; e.g stdio.h
section .data
hello: db "h" , "e" , 'l', 0x20, "lo: (%d): %s", 10, 0
X: dq 33
global main
section .text
main:
    push rbp
    mov rbp, rsp
    jmp la
    la: mov rcx, [X]; rcx = X
    inc rcx; rcx++
    sub rcx, 33
    cmp rcx, 0
    je fin
    mov [X],rdi
    mov rdx, [rsi + 8]
    ici: mov rdi, hello
    mov rsi, [X]
    mov rax, 0
    call printf
    fin:
    pop rbp
    ret