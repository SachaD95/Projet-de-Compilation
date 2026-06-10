import lark

grammaire = lark.Lark("""
IDENTIFIER: /[a-zA-Z_][a-zA-Z_0-9]*/
TYPE: "int"
OPBIN: /[+\\-*\\/<>]/

decl : TYPE IDENTIFIER
vars : decl ("," decl)* -> liste_vars                      
expression : IDENTIFIER -> variable
        | SIGNED_NUMBER -> entier
        | expression OPBIN expression -> binaire
        | IDENTIFIER "(" args ")" -> appel
        
args : expression ("," expression)* -> liste_args                      
commande : IDENTIFIER "=" expression ";" -> assignation
        | commande* commande -> sequence
        | "pass" -> pass    
        | "print" "(" expression ")" ";" -> print
        | "if" "(" expression ")" "{" commande "}" -> if
        | "while" "(" expression ")" "{" commande "}" -> while
                      
fonction : "int" IDENTIFIER "(" vars ")" "{" commande* "return" "(" expression ")" ";" "}"
                      
main : "main" "(" vars ")" "{" commande* "return" "(" expression ")" ";" "}"

programme : fonction* main


%import common.WS
%import common.SIGNED_NUMBER
%ignore WS
""", start="programme")


compteur = iter(range(1000000000)) 

def pp_expression(ast):
    if ast.data in ("variable", "entier"):
        return ast.children[0].value
    if ast.data == "appel":
        return f"{ast.children[0].value}({pp_args(ast.children[1])})"
    eg = f"{pp_expression(ast.children[0])}"
    op = ast.children[1].value
    ed = f"{pp_expression(ast.children[2])}"
    return f"{eg} {op} {ed}"


def asm_expression(ast, contexte={}):

    if ast.data == "variable":
        nom = ast.children[0].value
        if nom in contexte:
            return f"mov rax, [rbp{contexte[nom]}]\n"  #locale
        return f"mov rax, [{nom}]\n"  #globale

    if ast.data == "entier":
        return f"mov rax, {ast.children[0].value}\n"
    
    if ast.data == "appel":
        nom = ast.children[0].value
        args = ast.children[1].children
        regs = ["rdi", "rsi", "rdx", "rcx", "r8", "r9"]
        code = ""
        for i, arg in enumerate(args):
            code += asm_expression(arg, contexte)
            code += f"push rax\n"
           # code += f"mov {regs[i]}, rax\n"
        
        for i in range(len(args)-1, -1, -1):
            code += f"pop {regs[i]}\n"
            
        code += f"call {nom}\n"
        return code

    eg = asm_expression(ast.children[0], contexte)
    op = ast.children[1].value
    ed = asm_expression(ast.children[2], contexte)

    if op == "+":
        return eg + "push rax\n" + ed + "pop rbx\nadd rax, rbx\n"

    if op == "-":
        return eg + "push rax\n" + ed + "push rax\npop rbx\npop rax\nsub rax, rbx\n"

    if op == "*":
        return eg + "push rax\n" + ed + "pop rbx\nimul rax, rbx\n"

    if op == "/":
        return eg + "push rax\n" + ed + "push rax\npop rbx\npop rax\ncqo\nidiv rbx\n"
    
    if op == ">" or op == "<":
        cpt = next(compteur)
        jmp = "jg" if op == ">" else "jl"
        return (eg + "push rax\n" + ed +
                "push rax\npop rbx\npop rax\n" +
                f"cmp rax, rbx\n{jmp} vrai_{cpt}\n" +
                f"mov rax, 0\njmp fin_cmp_{cpt}\n" +
                f"vrai_{cpt}: mov rax, 1\n" +
                f"fin_cmp_{cpt}:\n")

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


def asm_commande(ast, contexte={}):
    if ast.data == "assignation":
        lhs = ast.children[0].value
        rhs = asm_expression(ast.children[1], contexte)
        if lhs in contexte:
            return f" {rhs}\nmov [rbp{contexte[lhs]}],rax \n"  #localee
        return f" {rhs}\nmov [{lhs}],rax \n"   #globale
    
    if ast.data == "pass":
        return "nop\n"
    
    if ast.data == "print":
        return f"""{asm_expression(ast.children[0], contexte)}
mov rdi, format
mov rsi, rax
xor rax, rax
call printf
"""
    if ast.data == "sequence":
        cg = asm_commande(ast.children[0], contexte)
        cd = asm_commande(ast.children[1], contexte)
        return f"{cg}\n{cd}"
    if ast.data == "while":
        test = asm_expression(ast.children[0], contexte)
        cmd = asm_commande(ast.children[1], contexte)
        cpt=next(compteur)
        return f"""debut_{cpt}:
{test}
cmp rax, 0
jz fin_{cpt}
{cmd}
jmp debut_{cpt}
fin_{cpt}:
"""

    if ast.data == "if":
        test = asm_expression(ast.children[0], contexte)
        cmd = asm_commande(ast.children[1], contexte)
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
    return "\n".join (f"""mov rdi, [argv]
add rdi, {(i+1)*8}
mov rdi, [rdi]
call atoi
mov [{ast.children[i].children[1].value}], rax
""" for i in range(len(ast.children)))


def asm_decls_vars(ast):
    return "\n".join(f"{ast.children[i].children[1].value}: dq 0"
        for i in range(len(ast.children))
    )


def pp_main(ast):
    vs= pp_vars(ast.children[0])
    cmds = ""
    for c in ast.children[2:-1]:
        cmds += pp_commande(c)    
    ret = pp_expression(ast.children[-1])
    return f"main({vs}){{{cmds} return({ret}); }}"

def asm_main(ast):
    decls= asm_decls_vars(ast.children[0])
    vs= asm_vars(ast.children[0])
    cmd = ""
    for c in ast.children[2:-1]:
        cmd += asm_commande(c)
    ret = asm_expression(ast.children[-1])
    squelette = open("squelette.asm").read()
    squelette = squelette.replace("INIT_VARS", vs)
    squelette = squelette.replace("DECL_VARS", decls)
    squelette = squelette.replace("COMMAND", cmd)
    squelette = squelette.replace("RETURN", ret)
    return squelette

def pp_args(ast):
    return ", ".join(
        pp_expression(arg)
        for arg in ast.children
    )

def pp_fonction(ast):
    nom = ast.children[0].value
    vars = pp_vars(ast.children[1])
    cmds = ""
    for c in ast.children[2:-1]:
        cmds += pp_commande(c)
    ret = pp_expression(ast.children[-1])
    return f"int {nom}({vars}){{{cmds} return({ret}); }}"

def asm_fonction(ast):
    nom = ast.children[0].value
    params = ast.children[1].children
    regs = ["rdi", "rsi", "rdx", "rcx", "r8", "r9"]

    contexte = {}
    
    for i,p in enumerate(params):
        contexte[p.children[1].value] = -(i+1)*8
   
    # on cherche les variables locales dans le body
    def trouver_locales(cmd):
        if cmd.data == "assignation":
            nom_var = cmd.children[0].value
            if nom_var not in contexte:
                contexte[nom_var] = -(len(contexte)+1)*8
        if cmd.data == "sequence":
            for c in cmd.children:
                trouver_locales(c)
        if cmd.data in ("while", "if"):
            trouver_locales(cmd.children[1])  
            
    for c in ast.children[2:-1]:
        trouver_locales(c)

    taille = len(contexte)*8

    save_params = "\n".join(
        f"mov [rbp{contexte[p.children[1].value]}], {regs[i]}"  
        for i, p in enumerate(params)
    )


    body = "\n".join(asm_commande(c, contexte) for c in ast.children[2:-1])
    ret = asm_expression(ast.children[-1], contexte)

    code = f"""
{nom}:
push rbp
mov rbp, rsp
sub rsp, {taille}
{save_params}
{body}
{ret}
mov rsp, rbp
pop rbp
ret
"""
    return code 

def pp_programme(ast):
    fonctions = "\n".join(pp_fonction(f) for f in ast.children if f.data == "fonction")
    for f in ast.children:
        if f.data == "main":
            main = pp_main(f)    
    return fonctions + "\n" + main

def asm_programme(ast):
    fonctions_code = []

    for f in ast.children:
        if f.data == "fonction":
            code = asm_fonction(f)
            fonctions_code.append(code)

    for f in ast.children:
        if f.data == "main":
            main = asm_main(f)

    main = main.replace("DECL_FONCTIONS","")
    main = main.replace("FONCTIONS", "\n".join(fonctions_code))

    return main


if __name__ == "__main__":
    src = open("source.c").read()
    t = grammaire.parse(src)
    print(pp_programme(t))
    with open("result.asm", "w") as f:
       f.write(asm_programme(t))