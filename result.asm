section .data
    format: db "%d", 10, 0
    argv: dq 0
    tableau_global_len: dq 4
    tableau_global_data: times 4 dq 0
    tableau_global_0_len: dq 0
    tableau_global_0_data: times 1024 dq 0
    tableau_global_1_len: dq 0
    tableau_global_1_data: times 1024 dq 0
    tableau_global_2_len: dq 0
    tableau_global_2_data: times 1024 dq 0
    tableau_global_3_len: dq 0
    tableau_global_3_data: times 1024 dq 0

section .text
    global main
    extern printf
    extern atoi

multiplier_tableau:
    push rbp
    mov rbp, rsp
    sub rsp, 80
    mov [rbp-8], rdi

    mov rax, 0
    mov [rbp-16], rax
    mov rax, [rel tableau_global_len]
    mov [rbp-24], rax
    mov rax, 0
    mov [rbp-32], rax
for_debut_0:
    mov rax, [rbp-32]
    mov [rbp-72], rax
    mov rax, [rbp-24]
    mov rbx, rax
    mov rax, [rbp-72]
    cmp rax, rbx
    setl al
    movzx rax, al
    cmp rax, 0
    jz for_fin_0
    mov rax, [rbp-32]
    imul rax, 8
    lea rbx, [rel tableau_global_data]
    add rax, rbx
    mov rax, [rax]
    mov [rbp-80], rax
    mov rax, [rbp-8]
    mov rbx, rax
    mov rax, [rbp-80]
    imul rax, rbx
    mov r12, rax
    mov rax, [rbp-32]
    imul rax, 8
    lea rcx, [rel tableau_global_data]
    add rcx, rax
    mov [rcx], r12
    mov rax, [rbp-16]
    mov [rbp-88], rax
    mov rax, [rbp-32]
    imul rax, 8
    lea rbx, [rel tableau_global_data]
    add rax, rbx
    mov rax, [rax]
    mov rbx, rax
    mov rax, [rbp-88]
    add rax, rbx
    mov [rbp-16], rax
    mov rax, [rbp-32]
    push rax
    mov rax, 1
    mov rbx, rax
    pop rax
    add rax, rbx
    mov [rbp-32], rax
    jmp for_debut_0
for_fin_0:

    mov rax, [rbp-16]

    mov rsp, rbp
    pop rbp
    ret


main:
    push rbp
    mov rbp, rsp
    sub rsp, 96
    mov [argv], rsi
    mov rdi, [argv]
    mov rdi, [rdi + 8]
    call atoi
    mov [rbp-80], rax
    mov rdi, [argv]
    mov rdi, [rdi + 16]
    call atoi
    mov [rbp-88], rax

    mov rax, 1
    mov [rel tableau_global_data + 0], rax
    mov rax, 2
    mov [rel tableau_global_data + 8], rax
    mov rax, 3
    mov [rel tableau_global_data + 16], rax
    mov rax, 4
    mov [rel tableau_global_data + 24], rax
    mov rax, 9999
    mov rsi, rax
    mov rdi, format
    xor rax, rax
    call printf
    mov rax, 0
    mov [rbp-16], rax
    mov rax, [rbp-80]
    mov [rbp-96], rax
    mov rax, [rbp-88]
    mov rbx, rax
    mov rax, [rbp-96]
    cmp rax, rbx
    setg al
    movzx rax, al
    cmp rax, 0
    jz fin_1
    mov rax, [rbp-80]
    mov [rbp-16], rax
    mov rax, [rbp-16]
    mov rsi, rax
    mov rdi, format
    xor rax, rax
    call printf
fin_1:
    mov rax, [rbp-80]
    mov [rbp-104], rax
    mov rax, [rbp-88]
    mov rbx, rax
    mov rax, [rbp-104]
    cmp rax, rbx
    setl al
    movzx rax, al
    cmp rax, 0
    jz fin_2
    mov rax, [rbp-88]
    mov [rbp-16], rax
    mov rax, [rbp-16]
    mov rsi, rax
    mov rdi, format
    xor rax, rax
    call printf
fin_2:
    mov rax, 9999
    mov rsi, rax
    mov rdi, format
    xor rax, rax
    call printf
    mov rax, 3
    mov [rbp-40], rax
debut_3:
    mov rax, [rbp-40]
    mov [rbp-112], rax
    mov rax, 0
    mov rbx, rax
    mov rax, [rbp-112]
    cmp rax, rbx
    setg al
    movzx rax, al
    cmp rax, 0
    jz fin_3
    mov rax, [rbp-40]
    mov rsi, rax
    mov rdi, format
    xor rax, rax
    call printf
    mov rax, [rbp-40]
    mov [rbp-120], rax
    mov rax, 1
    mov rbx, rax
    mov rax, [rbp-120]
    sub rax, rbx
    mov [rbp-40], rax
    jmp debut_3
fin_3:
    mov rax, 9999
    mov rsi, rax
    mov rdi, format
    xor rax, rax
    call printf
    mov rax, [rbp-80]
    mov [rbp-128], rax
    mov rdi, [rbp-128]
    call multiplier_tableau
    mov [rbp-64], rax
    mov rax, [rbp-64]
    mov rsi, rax
    mov rdi, format
    xor rax, rax
    call printf

    mov rax, 0

    add rsp, 96
    pop rbp
    ret


section .note.GNU-stack noalloc noexec nowrite progbits
