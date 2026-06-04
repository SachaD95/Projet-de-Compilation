extern printf, atoi

section .data
    argv:   dq 0
    format: db "%lld", 10, 0
    n: dq 0
    t_len: dq 5
    t_data: times 5 dq 0
    ligne0_len: dq 3
    ligne0_data: times 3 dq 0
    ligne1_len: dq 3
    ligne1_data: times 3 dq 0
    m_len: dq 2
    m_data: times 2 dq 0
    x: dq 0
    y: dq 0
    k: dq 0
    i: dq 0
    j: dq 0
DECL_FONCTIONS
global main
section .text
FONCTIONS
main:
    push rbp
    mov rbp, rsp
    push r12
    mov [argv], rsi
    mov rdi, [rel argv]
    add rdi, 8
    mov rdi, [rdi]
    call atoi
    mov [rel n], rax
    ; declaration locale
    ; declaration locale
    ; declaration locale
    ; declaration locale
    ; declaration locale
    ; declaration locale
    mov rax, 10
    mov [rel t_data + 0], rax
    mov rax, 20
    mov [rel t_data + 8], rax
    mov rax, 30
    mov [rel t_data + 16], rax
    mov rax, 40
    mov [rel t_data + 24], rax
    mov rax, 50
    mov [rel t_data + 32], rax
    mov rax, [rel t_len]
    mov rsi, rax
    mov rdi, format
    xor rax, rax
    call printf
    mov rax, 2
    imul rax, 8
    lea rbx, [rel t_data]
    add rax, rbx
    mov rax, [rax]
    mov rsi, rax
    mov rdi, format
    xor rax, rax
    call printf
    mov rax, 99
    mov r12, rax
    mov rax, 2
    imul rax, 8
    lea rcx, [rel t_data]
    add rcx, rax
    mov [rcx], r12
    mov rax, 2
    imul rax, 8
    lea rbx, [rel t_data]
    add rax, rbx
    mov rax, [rax]
    mov rsi, rax
    mov rdi, format
    xor rax, rax
    call printf
    mov rax, 0
    imul rax, 8
    lea rbx, [rel t_data]
    add rax, rbx
    mov rax, [rax]
    mov [rel x], rax
    mov rax, [rel x]
    mov rsi, rax
    mov rdi, format
    xor rax, rax
    call printf
    mov rax, 1
    mov [rel ligne0_data + 0], rax
    mov rax, 2
    mov [rel ligne0_data + 8], rax
    mov rax, 3
    mov [rel ligne0_data + 16], rax
    mov rax, 4
    mov [rel ligne1_data + 0], rax
    mov rax, 5
    mov [rel ligne1_data + 8], rax
    mov rax, 6
    mov [rel ligne1_data + 16], rax
    lea rax, [rel ligne0_data]
    mov r12, rax
    mov rax, 0
    imul rax, 8
    lea rcx, [rel m_data]
    add rcx, rax
    mov [rcx], r12
    lea rax, [rel ligne1_data]
    mov r12, rax
    mov rax, 1
    imul rax, 8
    lea rcx, [rel m_data]
    add rcx, rax
    mov [rcx], r12
    mov rax, [rel m_len]
    mov rsi, rax
    mov rdi, format
    xor rax, rax
    call printf
    mov rax, 0
    imul rax, 8
    lea rbx, [rel m_data]
    add rax, rbx
    mov rax, [rax]
    mov rax, [rax - 8]
    mov rsi, rax
    mov rdi, format
    xor rax, rax
    call printf
    mov rax, 1
    imul rax, 8
    lea rbx, [rel m_data]
    add rax, rbx
    mov rax, [rax]
    push rax
    mov rax, 2
    imul rax, 8
    pop rbx
    add rax, rbx
    mov rax, [rax]
    mov rsi, rax
    mov rdi, format
    xor rax, rax
    call printf
    mov rax, 42
    mov r12, rax
    mov rax, 1
    imul rax, 8
    lea rbx, [rel m_data]
    add rax, rbx
    mov rax, [rax]
    push rax
    mov rax, 2
    imul rax, 8
    pop rbx
    add rax, rbx
    mov rcx, rax
    mov [rcx], r12
    mov rax, 1
    imul rax, 8
    lea rbx, [rel m_data]
    add rax, rbx
    mov rax, [rax]
    push rax
    mov rax, 2
    imul rax, 8
    pop rbx
    add rax, rbx
    mov rax, [rax]
    mov rsi, rax
    mov rdi, format
    xor rax, rax
    call printf
    mov rax, 1
    imul rax, 8
    lea rbx, [rel m_data]
    add rax, rbx
    mov rax, [rax]
    push rax
    mov rax, 2
    imul rax, 8
    pop rbx
    add rax, rbx
    mov rax, [rax]
    mov [rel y], rax
    mov rax, [rel y]
    mov rsi, rax
    mov rdi, format
    xor rax, rax
    call printf
    mov rax, 0
    mov [rel k], rax
for_debut_0:
    mov rax, [rel k]
    push rax
    mov rax, [rel t_len]
    mov rbx, rax
    pop rax
    cmp rax, rbx
    setl al
    movzx rax, al
    cmp rax, 0
    jz for_fin_0
    mov rax, [rel k]
    imul rax, 8
    lea rbx, [rel t_data]
    add rax, rbx
    mov rax, [rax]
    mov rsi, rax
    mov rdi, format
    xor rax, rax
    call printf
    mov rax, [rel k]
    push rax
    mov rax, 1
    mov rbx, rax
    pop rax
    add rax, rbx
    mov [rel k], rax
    jmp for_debut_0
for_fin_0:
    mov rax, 0
    mov [rel i], rax
for_debut_2:
    mov rax, [rel i]
    push rax
    mov rax, [rel m_len]
    mov rbx, rax
    pop rax
    cmp rax, rbx
    setl al
    movzx rax, al
    cmp rax, 0
    jz for_fin_2
    mov rax, 0
    mov [rel j], rax
for_debut_1:
    mov rax, [rel j]
    push rax
    mov rax, [rel i]
    imul rax, 8
    lea rbx, [rel m_data]
    add rax, rbx
    mov rax, [rax]
    mov rax, [rax - 8]
    mov rbx, rax
    pop rax
    cmp rax, rbx
    setl al
    movzx rax, al
    cmp rax, 0
    jz for_fin_1
    mov rax, [rel i]
    imul rax, 8
    lea rbx, [rel m_data]
    add rax, rbx
    mov rax, [rax]
    push rax
    mov rax, [rel j]
    imul rax, 8
    pop rbx
    add rax, rbx
    mov rax, [rax]
    mov rsi, rax
    mov rdi, format
    xor rax, rax
    call printf
    mov rax, [rel j]
    push rax
    mov rax, 1
    mov rbx, rax
    pop rax
    add rax, rbx
    mov [rel j], rax
    jmp for_debut_1
for_fin_1:
    mov rax, [rel i]
    push rax
    mov rax, 1
    mov rbx, rax
    pop rax
    add rax, rbx
    mov [rel i], rax
    jmp for_debut_2
for_fin_2:

    mov rax, [rel n]

    mov rsi, rax
    mov rdi, format
    xor rax, rax
    call printf
    pop r12
    pop rbp
    ret