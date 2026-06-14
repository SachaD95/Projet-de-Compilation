section .data
format: db "%d", 10, 0
n: dq 0

section .text
global main
extern printf
extern atoi

add:
    push rbp
    mov rbp, rsp
    sub rsp, 512
    mov [rbp-8], rdi
    mov [rbp-16], rsi
    mov rax, [rbp-8]
    push rax
    mov rax, [rbp-16]
    mov rbx, rax
    pop rax
    add rax, rbx
    push rax
    lea rcx, [rbp-24]
    pop rax
    mov [rcx], rax
    mov rax, [rbp-24]
    mov rsp, rbp
    pop rbp
    ret

sub:
    push rbp
    mov rbp, rsp
    sub rsp, 512
    mov [rbp-8], rdi
    mov [rbp-16], rsi
    mov rax, [rbp-8]
    push rax
    mov rax, [rbp-16]
    mov rbx, rax
    pop rax
    sub rax, rbx
    push rax
    lea rcx, [rbp-24]
    pop rax
    mov [rcx], rax
    mov rax, [rbp-24]
    mov rsp, rbp
    pop rbp
    ret

mul:
    push rbp
    mov rbp, rsp
    sub rsp, 512
    mov [rbp-8], rdi
    mov [rbp-16], rsi
    mov rax, [rbp-8]
    push rax
    mov rax, [rbp-16]
    mov rbx, rax
    pop rax
    imul rax, rbx
    push rax
    lea rcx, [rbp-24]
    pop rax
    mov [rcx], rax
    mov rax, [rbp-24]
    mov rsp, rbp
    pop rbp
    ret

fact:
    push rbp
    mov rbp, rsp
    sub rsp, 512
    mov [rbp-8], rdi
    mov rax, 1
    push rax
    lea rcx, [rbp-16]
    pop rax
    mov [rcx], rax
    mov rax, [rbp-8]
    push rax
    mov rax, 1
    mov rbx, rax
    pop rax
    cmp rax, rbx
    setg al
    movzx rax, al
    cmp rax, 0
    je .end_if_1
    mov rax, [rbp-8]
    push rax
    mov rax, fact
    push rax
    mov rax, [rbp-8]
    push rax
    mov rax, 1
    mov rbx, rax
    pop rax
    sub rax, rbx
    push rax
    pop rdi
    pop rax
    call rax
    mov rbx, rax
    pop rax
    imul rax, rbx
    push rax
    lea rcx, [rbp-16]
    pop rax
    mov [rcx], rax
.end_if_1:
    mov rax, [rbp-16]
    mov rsp, rbp
    pop rbp
    ret

main:
    push rbp
    mov rbp, rsp
    sub rsp, 512
    push rsi
    mov rdi, [rsp]
    mov rdi, [rdi + 8]
    call atoi
    mov [n], rax
    pop rsi

    mov rax, 60
    push rax
    mov rax, 50
    push rax
    mov rax, 40
    push rax
    mov rax, 30
    push rax
    mov rax, 20
    push rax
    mov rax, 10
    push rax
    lea rcx, [rbp-8]
    pop rax
    mov [rcx - 0], rax
    pop rax
    mov [rcx - 8], rax
    pop rax
    mov [rcx - 16], rax
    pop rax
    mov [rcx - 24], rax
    pop rax
    mov [rcx - 32], rax
    pop rax
    mov [rcx - 40], rax
    mov rax, 1
    mov rdi, format
    mov rsi, rax
    xor rax, rax
    call printf
    mov rax, [rbp-8]
    push rax
    mov rax, 2
    push rax
    pop rax
    imul rax, 8
    pop rbx
    sub rbx, rax
    mov rax, [rbx]
    mov rdi, format
    mov rsi, rax
    xor rax, rax
    call printf
    mov rax, 99
    push rax
    lea rcx, [rbp-8]
    push rcx
    mov rax, 2
    push rax
    pop rax
    imul rax, 8
    pop rbx
    sub rbx, rax
    mov rcx, rbx
    pop rax
    mov [rcx], rax
    mov rax, [rbp-8]
    push rax
    mov rax, 2
    push rax
    pop rax
    imul rax, 8
    pop rbx
    sub rbx, rax
    mov rax, [rbx]
    mov rdi, format
    mov rsi, rax
    xor rax, rax
    call printf
    mov rax, 3
    push rax
    mov rax, 2
    push rax
    mov rax, 1
    push rax
    lea rcx, [rbp-32]
    pop rax
    mov [rcx - 0], rax
    pop rax
    mov [rcx - 8], rax
    pop rax
    mov [rcx - 16], rax
    mov rax, 6
    push rax
    mov rax, 5
    push rax
    mov rax, 4
    push rax
    lea rcx, [rbp-56]
    pop rax
    mov [rcx - 0], rax
    pop rax
    mov [rcx - 8], rax
    pop rax
    mov [rcx - 16], rax
    lea rax, [rbp-32]
    push rax
    lea rcx, [rbp-72]
    push rcx
    mov rax, 0
    push rax
    pop rax
    imul rax, 8
    pop rbx
    sub rbx, rax
    mov rcx, rbx
    pop rax
    mov [rcx], rax
    lea rax, [rbp-56]
    push rax
    lea rcx, [rbp-72]
    push rcx
    mov rax, 1
    push rax
    pop rax
    imul rax, 8
    pop rbx
    sub rbx, rax
    mov rcx, rbx
    pop rax
    mov [rcx], rax
    mov rax, 2
    mov rdi, format
    mov rsi, rax
    xor rax, rax
    call printf
    mov rax, 1
    mov rdi, format
    mov rsi, rax
    xor rax, rax
    call printf
    lea rax, [rbp-72]
    push rax
    mov rax, 1
    shl rax, 3
    pop rbx
    sub rbx, rax
    mov rbx, [rbx]
    push rbx
    mov rax, 2
    shl rax, 3
    pop rbx
    sub rbx, rax
    mov rax, [rbx]
    mov rdi, format
    mov rsi, rax
    xor rax, rax
    call printf
    mov rax, 42
    push rax
    lea rcx, [rbp-72]
    push rcx
    mov rax, 1
    shl rax, 3
    pop rcx
    sub rcx, rax
    mov rcx, [rcx]
    push rcx
    mov rax, 2
    shl rax, 3
    pop rcx
    sub rcx, rax
    pop rax
    mov [rcx], rax
    lea rax, [rbp-72]
    push rax
    mov rax, 1
    shl rax, 3
    pop rbx
    sub rbx, rax
    mov rbx, [rbx]
    push rbx
    mov rax, 2
    shl rax, 3
    pop rbx
    sub rbx, rax
    mov rax, [rbx]
    mov rdi, format
    mov rsi, rax
    xor rax, rax
    call printf
    mov rax, [rbp-96]
    push rax
    mov rax, 2
    push rax
    mov rax, 4
    push rax
    pop rsi
    pop rdi
    pop rax
    call rax
    push rax
    lea rcx, [rbp-88]
    pop rax
    mov rsi, [rax - 0]
    mov [rcx - 0], rsi
    mov rsi, [rax - 8]
    mov [rcx - 8], rsi
    lea rax, [rbp-88]
    add rax, 0
    mov rax, [rax]
    mov rdi, format
    mov rsi, rax
    xor rax, rax
    call printf
    lea rax, [rbp-88]
    add rax, -8
    mov rax, [rax]
    mov rdi, format
    mov rsi, rax
    xor rax, rax
    call printf
    mov rax, [rbp-96]
    push rax
    mov rax, 1
    push rax
    mov rax, 2
    push rax
    pop rsi
    pop rdi
    pop rax
    call rax
    push rax
    lea rcx, [rbp-128]
    push rcx
    mov rax, 0
    push rax
    pop rax
    imul rax, 16
    pop rbx
    sub rbx, rax
    mov rcx, rbx
    pop rax
    mov rsi, [rax - 0]
    mov [rcx - 0], rsi
    mov rsi, [rax - 8]
    mov [rcx - 8], rsi
    mov rax, [rbp-96]
    push rax
    mov rax, 7
    push rax
    mov rax, 8
    push rax
    pop rsi
    pop rdi
    pop rax
    call rax
    push rax
    lea rcx, [rbp-128]
    push rcx
    mov rax, 1
    push rax
    pop rax
    imul rax, 16
    pop rbx
    sub rbx, rax
    mov rcx, rbx
    pop rax
    mov rsi, [rax - 0]
    mov [rcx - 0], rsi
    mov rsi, [rax - 8]
    mov [rcx - 8], rsi
    lea rax, [rbp-128]
    push rax
    mov rax, 0
    push rax
    pop rax
    imul rax, 16
    pop rbx
    sub rbx, rax
    mov rax, rbx
    add rax, 0
    mov rax, [rax]
    mov rdi, format
    mov rsi, rax
    xor rax, rax
    call printf
    lea rax, [rbp-128]
    push rax
    mov rax, 1
    push rax
    pop rax
    imul rax, 16
    pop rbx
    sub rbx, rax
    mov rax, rbx
    add rax, -8
    mov rax, [rax]
    mov rdi, format
    mov rsi, rax
    xor rax, rax
    call printf
    mov rax, [rbp-96]
    push rax
    mov rax, 10
    push rax
    mov rax, 20
    push rax
    pop rsi
    pop rdi
    pop rax
    call rax
    push rax
    lea rcx, [rbp-160]
    add rcx, 0
    pop rax
    mov rsi, [rax - 0]
    mov [rcx - 0], rsi
    mov rsi, [rax - 8]
    mov [rcx - 8], rsi
    mov rax, [rbp-96]
    push rax
    mov rax, 30
    push rax
    mov rax, 40
    push rax
    pop rsi
    pop rdi
    pop rax
    call rax
    push rax
    lea rcx, [rbp-160]
    add rcx, -16
    pop rax
    mov rsi, [rax - 0]
    mov [rcx - 0], rsi
    mov rsi, [rax - 8]
    mov [rcx - 8], rsi
    lea rax, [rbp-160]
    add rax, 0
    add rax, 0
    mov rax, [rax]
    mov rdi, format
    mov rsi, rax
    xor rax, rax
    call printf
    lea rax, [rbp-160]
    add rax, -16
    add rax, -8
    mov rax, [rax]
    mov rdi, format
    mov rsi, rax
    xor rax, rax
    call printf
    mov rax, sub
    push rax
    mov rax, add
    push rax
    mov rax, mul
    push rax
    mov rax, [rbp-168]
    push rax
    mov rax, [rbp-168]
    push rax
    pop rsi
    pop rdi
    pop rax
    call rax
    push rax
    mov rax, fact
    push rax
    mov rax, 4
    push rax
    pop rdi
    pop rax
    call rax
    push rax
    pop rsi
    pop rdi
    pop rax
    call rax
    push rax
    mov rax, 3
    push rax
    pop rsi
    pop rdi
    pop rax
    call rax
    mov rdi, format
    mov rsi, rax
    xor rax, rax
    call printf
    mov rax, 0
    mov [rbp-176], rax
.f_cond_2:
    mov rax, [rbp-176]
    push rax
    mov rax, 1
    mov rbx, rax
    pop rax
    cmp rax, rbx
    setl al
    movzx rax, al
    cmp rax, 0
    je .f_end_3
    mov rax, [rbp-8]
    push rax
    mov rax, [rbp-176]
    push rax
    pop rax
    imul rax, 8
    pop rbx
    sub rbx, rax
    mov rax, [rbx]
    mov rdi, format
    mov rsi, rax
    xor rax, rax
    call printf
    mov rax, [rbp-176]
    push rax
    mov rax, 1
    mov rbx, rax
    pop rax
    add rax, rbx
    mov [rbp-176], rax
    jmp .f_cond_2
.f_end_3:
    mov rax, [rbp-168]
    mov rsp, rbp
    pop rbp
    ret
