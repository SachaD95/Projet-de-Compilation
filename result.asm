section .data
format: db "%d", 10, 0
n: dq 0

section .text
global main
extern printf
extern atoi



main:
    push rbp
    mov rbp, rsp
    sub rsp, 48
    push rsi
    mov rdi, [rsp]
    mov rdi, [rdi + 8]
    call atoi
    mov [n], rax
    pop rsi

    mov rax, 2
    push rax
    mov rax, 4
    push rax
    pop rax
    mov [rbp-24], rax
    pop rax
    mov [rbp-32], rax

    mov rax, [rbp-32]
    mov [rbp-48], rax
    mov rax, [rbp-24]
    mov [rbp-40], rax

    mov rax, [rbp-32]
    mov rdi, format
    mov rsi, rax
    xor rax, rax
    call printf


    mov rax, 0

    mov rsp, rbp
    pop rbp
    ret