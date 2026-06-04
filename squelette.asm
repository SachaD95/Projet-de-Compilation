extern printf, atoi

section .data
    argv:   dq 0
    format: db "%lld", 10, 0
DECL_VARS
DECL_FONCTIONS
global main
section .text
FONCTIONS
main:
    push rbp
    mov rbp, rsp
    push r12
    mov [argv], rsi
INIT_VARS
COMMAND
RETURN
    mov rsi, rax
    mov rdi, format
    xor rax, rax
    call printf
    pop r12
    pop rbp
    ret