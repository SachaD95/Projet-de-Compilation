section .data
format: db "%d", 10, 0
DECL_VARS

section .text
global main
extern printf
extern atoi

FONCTIONS

main:
    push rbp
    mov rbp, rsp
    sub rsp, STACK_SIZE
INIT_VARS
COMMAND
RETURN
    mov rsp, rbp
    pop rbp
    ret