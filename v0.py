import lark

grammaire = lark.Lark("""
IDENTIFIER: /[a-zA-Z_][a-zA-Z_0-9]*/
TYPE: "int"
OPBIN: /[+\\-*\\/<>]/

decl : TYPE IDENTIFIER
vars : (decl ",")* decl -> liste_vars

expression : IDENTIFIER -> variable
       | SIGNED_NUMBER -> entier
       | expression OPBIN expression -> binaire
        
commande : IDENTIFIER "=" expression ";" -> assignation
| commande* commande -> sequence
| "pass" -> pass    
| "print" "(" expression ")" ";" -> print
| "if" "(" expression ")" "{" commande "}" -> if
| "while" "(" expression ")" "{" commande "}" -> while

main : "main" "(" vars ")" "{" commande "return" "(" expression ")" ";" "}"
%import common.WS
%import common.SIGNED_NUMBER
%ignore WS
""", start="main")


compteur = iter(range(1000000000))

def pp_expression(ast):
    if ast.data in ("variable", "entier"):
        return ast.children[0].value
    eg = f"{pp_expression(ast.children[0])}"
    op = ast.children[1].value
    ed = f"{pp_expression(ast.children[2])}"
    return f"{eg} {op} {ed}"

def asm_expression(ast):

    if ast.data == "variable":
        return f"mov rax, [{ast.children[0].value}]\n"

    if ast.data == "entier":
        return f"mov rax, {ast.children[0].value}\n"

    eg = asm_expression(ast.children[0])
    op = ast.children[1].value
    ed = asm_expression(ast.children[2])

    if op == "+":
        return eg + "push rax\n" + ed + "pop rbx\nadd rax, rbx\n"

    if op == "-":
        return eg + "push rax\n" + ed + "pop rbx\nsub rax, rbx\n"

    if op == "*":
        return eg + "push rax\n" + ed + "pop rbx\nimul rax, rbx\n"

    if op == "/":
        return (
            eg
            + "push rax\n"
            + ed
            + "pop rbx\n"
            + "mov rax, rbx\n"
            + "cqo\n"
            + "idiv rax\n"
        )

def pp_commande(ast):
    if ast.data == "assignation":
        lhs = ast.children[0].value
        rhs = pp_expression(ast.children[1])
        return f"{lhs} = {rhs};"
    if ast.data == "pass":
        return "pass"
    if ast.data == "print":
        return f"print({pp_expression(ast.children[0])});"
    if ast.data == "sequence":
        cg = pp_commande(ast.children[0])
        cd = pp_commande(ast.children[1])
        return f"{cg}{cd}"
    if ast.data in ("while","if"):
        test = pp_expression(ast.children[0])
        cmd = pp_commande(ast.children[1])
        return f"{ast.data}({test}) {{{cmd}}}"
    return "to be implemented"


def asm_commande(ast):
    if ast.data == "assignation":
        lhs = ast.children[0].value
        rhs = asm_expression(ast.children[1])
        return f" {rhs}\nmov [{lhs}],rax \n"
    if ast.data == "pass":
        return "nop\n"
    if ast.data == "print":
        return f"""{asm_expression(ast.children[0])}
mov rdi, format
mov rsi, rax
xor rax, rax
call printf
"""
    if ast.data == "sequence":
        cg = asm_commande(ast.children[0])
        cd = asm_commande(ast.children[1])
        return f"{cg}\n{cd}"
    if ast.data == "while":
        test = asm_expression(ast.children[0])
        cmd = asm_commande(ast.children[1])
        cpt=next(compteur)
        return f"""debut_{cpt}:
                {test}
                cmp rax, 0
                jz fin_{cpt}
                {cmd}jmp debut_{cpt} 
                fin_{cpt}:
                """
        #zdt jmp debut_ {cpt}

    if ast.data == "if":
        test = asm_expression(ast.children[0])
        cmd = asm_commande(ast.children[1])
        cpt=next(compteur)
        return f"""{test}
                cmp rax, 0
                jz fin_{cpt}
                {cmd}
                fin_{cpt}:
                """
    return "to be implemented"

def pp_vars(ast):
    return ", ".join(
        f"{v.children[0].value} {v.children[1].value}"
        for v in ast.children
    )


def asm_vars(ast):
    return "\n".join (f""" mov rdi, [argv]
        add rdi, {(i+1)*8}
        mov rdi, [rbx]
        call atoi
        mov [{ast.children[i].children[1].value}], rax
        """ for i in range(len(ast.children)))


def asm_decls_vars(ast):
    return "\n".join(f"{ast.children[i].children[1].value}: dq 0"
        for i in range(len(ast.children))
    )


def pp_main(ast):
    vs= pp_vars(ast.children[0])
    cmd = pp_commande(ast.children[1])
    ret = pp_expression(ast.children[2])
    return f"main({vs}){{{cmd} return({ret}); }}"

def asm_main(ast):
    decls= asm_decls_vars(ast.children[0])
    vs= asm_vars(ast.children[0])
    cmd = asm_commande(ast.children[1])
    ret = asm_expression(ast.children[2])
    squelette = open("squelette.asm").read()
    squelette = squelette.replace("INIT_VARS", vs)
    squelette = squelette.replace("DECL_VARS", decls)
    squelette = squelette.replace("COMMAND", cmd)
    squelette = squelette.replace("RETURN", ret)
    return squelette

if __name__ == "__main__":
    src = open("source.c").read()
    t = grammaire.parse(src)
    print(pp_main(t))
    with open("result.asm", "w") as f:
        f.write(asm_main(t))