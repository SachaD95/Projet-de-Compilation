extern printf, atoi
section .data
argv: dq 0
format: db "%lld\n", 0
a: dq 0
b: dq 0

global main
section .text

add:
push rbp
mov rbp, rsp
sub rsp, 24
mov [rbp-8], rdi
mov [rbp-16], rsi
 mov rax, [rbp-8]
push rax
mov rax, [rbp-16]
pop rbx
add rax, rbx

mov [rbp-24],rax 

mov rax, [rbp-24]

mov rsp, rbp
pop rbp
ret


sub:
push rbp
mov rbp, rsp
sub rsp, 24
mov [rbp-8], rdi
mov [rbp-16], rsi
 mov rax, [rbp-8]
push rax
mov rax, [rbp-16]
push rax
pop rbx
pop rax
sub rax, rbx

mov [rbp-24],rax 

mov rax, [rbp-24]

mov rsp, rbp
pop rbp
ret


mul:
push rbp
mov rbp, rsp
sub rsp, 24
mov [rbp-8], rdi
mov [rbp-16], rsi
 mov rax, [rbp-8]
push rax
mov rax, [rbp-16]
pop rbx
imul rax, rbx

mov [rbp-24],rax 

mov rax, [rbp-24]

mov rsp, rbp
pop rbp
ret


fact:
push rbp
mov rbp, rsp
sub rsp, 16
mov [rbp-8], rdi
 mov rax, 1

mov [rbp-16],rax 

mov rax, [rbp-8]
push rax
mov rax, 1
push rax
pop rbx
pop rax
cmp rax, rbx
jg vrai_0
mov rax, 0
jmp fin_cmp_0
vrai_0: mov rax, 1
fin_cmp_0:

cmp rax, 0
jz fin_1
 mov rax, [rbp-8]
push rax
mov rax, [rbp-8]
push rax
mov rax, 1
push rax
pop rbx
pop rax
sub rax, rbx
push rax
pop rdi
call fact
pop rbx
imul rax, rbx

mov [rbp-16],rax 

fin_1:

mov rax, [rbp-16]

mov rsp, rbp
pop rbp
ret

main:
push rbp
mov rbp, rsp
mov [argv], rsi
mov rdi, [argv]
add rdi, 8
mov rdi, [rdi]
call atoi
mov [a], rax

mov rdi, [argv]
add rdi, 16
mov rdi, [rdi]
call atoi
mov [b], rax


mov rax, [a]
push rax
mov rax, [a]
push rax
pop rsi
pop rdi
call mul
push rax
mov rax, [b]
push rax
mov rax, [b]
push rax
pop rsi
pop rdi
call mul
push rax
pop rsi
pop rdi
call add
push rax
mov rax, [a]
push rax
pop rdi
call fact
push rax
pop rsi
pop rdi
call sub

mov rsi, rax
mov rdi, format
xor rax, rax
call printf
pop rbp
ret