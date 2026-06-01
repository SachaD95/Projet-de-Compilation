import lark

grammaire = lark.Lark(r"""
IDENTIFIER : /[a-zA-Z_][a-zA-Z_0-9]*/
TYPE       : "int"
OPBIN      : /[+\-*\/<>]/

field_decl : TYPE IDENTIFIER       -> field_decl_int
           | IDENTIFIER IDENTIFIER -> field_decl_struct

struct_def : "typedef" "struct" "{" (field_decl ";")+ "}" IDENTIFIER ";" -> struct_def

decl : TYPE IDENTIFIER "[" expression "]" "[" expression "]" -> decl_array2d
     | TYPE IDENTIFIER "[" expression "]"                    -> decl_array
     | TYPE IDENTIFIER                                       -> decl_scalar
     | IDENTIFIER IDENTIFIER                                 -> decl_struct

vars : (decl ",")* decl -> liste_vars

row : "{" [expression ("," expression)*] "}"

expression : IDENTIFIER                                              -> variable
           | SIGNED_NUMBER                                           -> entier
           | expression OPBIN expression                             -> binaire
           | "(" expression ")"
           | "{" [expression ("," expression)*] "}"                  -> array_literal
           | "{" row ("," row)* "}"                                  -> array2d_literal
           | expression "[" expression "]" "[" expression "]"        -> index2d
           | expression "[" expression "]"                           -> index
           | expression "." IDENTIFIER                               -> field_access
           | "len" "(" expression ")"                                -> len
           | IDENTIFIER "(" [expression ("," expression)*] ")"       -> struct_constructor

lvalue : IDENTIFIER
       | lvalue "[" expression "]" "[" expression "]"  -> index2d_lvalue
       | lvalue "[" expression "]"                     -> index_lvalue
       | lvalue "." IDENTIFIER                         -> field_lvalue

commande : lvalue "=" expression ";"                                           -> assignation
         | IDENTIFIER IDENTIFIER "=" expression ";"                            -> decl_struct_init
         | decl ";"                                                            -> decl_commande
         | commande*                                                            -> sequence
         | "pass"                                                               -> pass
         | "print" "(" expression ")" ";"                                      -> print
         | "if" "(" expression ")" "{" commande "}"                            -> if
         | "while" "(" expression ")" "{" commande "}"                         -> while
         | "for" "(" TYPE IDENTIFIER "=" expression ";" expression ";" IDENTIFIER "=" IDENTIFIER OPBIN expression ")" "{" commande "}" -> for

main : "main" "(" vars ")" "{" commande "return" "(" expression ")" ";" "}"

program : struct_def* main -> program

%import common.WS
%import common.SIGNED_NUMBER
%ignore WS
""", start="program")

def pp_expression(ast):

    if ast.data == "variable":
        return ast.children[0].value

    if ast.data == "entier":
        return ast.children[0].value

    if ast.data == "binaire":
        gauche = pp_expression(ast.children[0])
        op     = ast.children[1].value
        droite = pp_expression(ast.children[2])
        return f"{gauche} {op} {droite}"

    if ast.data == "index":
        return f"{pp_expression(ast.children[0])}[{pp_expression(ast.children[1])}]"

    if ast.data == "row":
        elements = ", ".join(pp_expression(c) for c in ast.children)
        return "{" + elements + "}"

    if ast.data == "array2d_literal":
        lignes = ", ".join(pp_expression(r) for r in ast.children)
        return "{" + lignes + "}"

    if ast.data == "len":
        return f"len({pp_expression(ast.children[0])})"

    if ast.data == "array_literal":
        elements = ", ".join(pp_expression(c) for c in ast.children)
        return "{" + elements + "}"

    if ast.data == "struct_constructor":
        nom  = ast.children[0].value
        args = ", ".join(pp_expression(c) for c in ast.children[1:])
        return f"{nom}({args})"

    if ast.data == "field_access":
        return f"{pp_expression(ast.children[0])}.{ast.children[1].value}"


# Compteur global pour les étiquettes uniques
compteur_label = 0

def asm_expression(ast) -> str:
    global compteur_label

    if ast.data == "variable":
        nom_var = ast.children[0].value
        return f"    mov rax, [{nom_var}]\n"

    if ast.data == "entier":
        valeur = ast.children[0].value
        return f"    mov rax, {valeur}\n"

    if ast.data == "binaire":
        code_gauche = asm_expression(ast.children[0])
        op          = ast.children[1].value
        code_droite = asm_expression(ast.children[2])

        if op in ('+', '-', '*'):
            ops_assembleur = {'+': 'add', '-': 'sub', '*': 'imul'}
            inst_asm = ops_assembleur[op]
            return f"""{code_gauche}\
    push rax
{code_droite}\
    mov rbx, rax
    pop rax
    {inst_asm} rax, rbx
"""

        if op in ('<', '>'):
            inst_jmp = 'jl' if op == '<' else 'jg'
            label_vrai = f"cmp_vrai_{compteur_label}"
            label_fin  = f"cmp_fin_{compteur_label}"
            compteur_label += 1
            return f"""{code_gauche}\
    push rax
{code_droite}\
    mov rbx, rax
    pop rax
    cmp rax, rbx
    {inst_jmp} {label_vrai}
    mov rax, 0
    jmp {label_fin}
{label_vrai}:
    mov rax, 1
{label_fin}:
"""

    if ast.data == "struct_constructor":
        code_assembleur = ""
        # CORRIGÉ : ordre inverse pour que le premier champ soit au sommet de la pile
        for c in reversed(ast.children[1:]):
            code_argument = asm_expression(c)
            code_assembleur += f"""{code_argument}    push rax
"""
        return code_assembleur

    if ast.data == "field_access":
        # CORRIGÉ : on lit à l'adresse de la variable + offset du champ
        base   = pp_expression(ast.children[0])   # ex: "P"
        champ  = ast.children[1].value             # "x" ou "y"
        offsets = {"x": 0, "y": 8}
        off    = offsets.get(champ, 0)
        return f"    mov rax, [{base}+{off}]\n"

    if ast.data == "index":
        return f"{pp_expression(ast.children[0])}[{pp_expression(ast.children[1])}]"

    if ast.data == "len":
        return f"len({pp_expression(ast.children[0])})"


def asm_lvalue(ast) -> str:
    """Retourne le code ASM pour calculer l'adresse de la lvalue dans rdi."""
    if ast.data == "lvalue":
        nom = ast.children[0].value
        return f"    lea rdi, [{nom}]\n"

    if ast.data == "index_lvalue":
        code_base  = asm_lvalue(ast.children[0])
        code_index = asm_expression(ast.children[1])
        return f"""{code_base}\
{code_index}\
    imul rax, 8
    add rdi, rax
"""

    if ast.data == "field_lvalue":
        offsets   = {"x": 0, "y": 8}
        champ     = ast.children[1].value
        off       = offsets.get(champ, 0)
        code_base = asm_lvalue(ast.children[0])
        return f"""{code_base}\
    add rdi, {off}
"""


def pp_lvalue(ast):

    if ast.data == "lvalue":
        return ast.children[0].value

    if ast.data == "index_lvalue":
        return f"{pp_lvalue(ast.children[0])}[{pp_expression(ast.children[1])}]"

    if ast.data == "index2d_lvalue":
        return f"{pp_lvalue(ast.children[0])}[{pp_expression(ast.children[1])}][{pp_expression(ast.children[2])}]"

    if ast.data == "field_lvalue":
        return f"{pp_lvalue(ast.children[0])}.{ast.children[1].value}"


def pp_commande(ast):

    if ast.data == "assignation":
        lhs = pp_lvalue(ast.children[0])
        rhs = pp_expression(ast.children[1])
        return f"{lhs} = {rhs};\n"

    if ast.data == "pass":
        return "pass\n"

    if ast.data == "decl_commande":
        return pp_decl(ast.children[0]) + ";\n"

    if ast.data == "decl_struct_init":
        typ = ast.children[0].value
        nom = ast.children[1].value
        val = pp_expression(ast.children[2])
        return f"{typ} {nom} = {val};\n"

    if ast.data == "print":
        return f"print({pp_expression(ast.children[0])});\n"

    if ast.data == "sequence":
        return "".join(pp_commande(c) for c in ast.children)

    if ast.data == "if":
        test  = pp_expression(ast.children[0])
        corps = pp_commande(ast.children[1])
        return f"if ({test}) {{\n{corps}}}\n"

    if ast.data == "while":
        test  = pp_expression(ast.children[0])
        corps = pp_commande(ast.children[1])
        return f"while ({test}) {{\n{corps}}}\n"

    if ast.data == "for":
        typ      = ast.children[0].value
        var      = ast.children[1].value
        init     = pp_expression(ast.children[2])
        cond     = pp_expression(ast.children[3])
        lhs_inc  = ast.children[4].value
        src_inc  = ast.children[5].value
        op_inc   = ast.children[6].value
        val_inc  = pp_expression(ast.children[7])
        corps    = pp_commande(ast.children[8])
        return f"for ({typ} {var} = {init}; {cond}; {lhs_inc} = {src_inc} {op_inc} {val_inc}) {{\n{corps}}}\n"


def asm_commande(ast) -> str:
    global compteur_label

    if ast.data == "assignation":
        # CORRIGÉ : utilise asm_lvalue pour gérer t[i], A.x, etc.
        lhs_code = asm_lvalue(ast.children[0])
        rhs_code = asm_expression(ast.children[1])
        return f"""{lhs_code}\
    push rdi
{rhs_code}\
    pop rdi
    mov [rdi], rax
"""

    if ast.data == "decl_struct_init":
        # CORRIGÉ : cas ajouté — stocke les champs pushés dans la variable
        nom = ast.children[1].value
        rhs = asm_expression(ast.children[2])
        return f"""{rhs}\
    pop qword [{nom}+0]
    pop qword [{nom}+8]
"""

    if ast.data == "pass":
        return "    nop\n"

    if ast.data == "print":
        code_expr = asm_expression(ast.children[0])
        return f"""{code_expr}\
    mov rdi, format
    mov rsi, rax
    xor rax, rax
    call printf
"""

    if ast.data == "sequence":
        return "".join(asm_commande(c) for c in ast.children)

    if ast.data == "while":
        label_debut = f"debut_while_{compteur_label}"
        label_fin   = f"fin_while_{compteur_label}"
        compteur_label += 1

        cond = asm_expression(ast.children[0])
        cmd  = asm_commande(ast.children[1])

        return f"""{label_debut}:
{cond}\
    cmp rax, 0
    jz {label_fin}
{cmd}\
    jmp {label_debut}
{label_fin}:
"""

    if ast.data == "if":
        cpt = compteur_label
        compteur_label += 1

        test = asm_expression(ast.children[0])
        cmd  = asm_commande(ast.children[1])

        return f"""{test}\
    cmp rax, 0
    jz fin_{cpt}
{cmd}fin_{cpt}:
"""

    return ""


def pp_vars(ast):
    return ", ".join(pp_decl(d) for d in ast.children)


def pp_decl(ast):
    if ast.data == "decl_scalar":
        typ = ast.children[0].value
        nom = ast.children[1].value
        return f"{typ} {nom}"

    if ast.data == "decl_array":
        typ    = ast.children[0].value
        nom    = ast.children[1].value
        taille = pp_expression(ast.children[2])
        return f"{typ} {nom}[{taille}]"

    if ast.data == "decl_array2d":
        typ    = ast.children[0].value
        nom    = ast.children[1].value
        lignes = pp_expression(ast.children[2])
        cols   = pp_expression(ast.children[3])
        return f"{typ} {nom}[{lignes}][{cols}]"

    if ast.data == "decl_struct":
        typ = ast.children[0].value
        nom = ast.children[1].value
        return f"{typ} {nom}"


def pp_field_decl(ast):
    typ = ast.children[0].value
    nom = ast.children[1].value
    return f"    {typ} {nom}"


def pp_struct_def(ast):
    champs = [pp_field_decl(c) for c in ast.children[:-1]]
    nom    = ast.children[-1].value
    corps  = ";\n".join(champs) + ";"
    return f"typedef struct {{\n{corps}\n}} {nom};\n"


def pp_main(ast):
    params = pp_vars(ast.children[0])
    corps  = pp_commande(ast.children[1])
    retour = pp_expression(ast.children[2])
    return f"main({params}) {{\n{corps}return ({retour});\n}}"


def pp_program(ast):
    parties = []
    for child in ast.children:
        if child.data == "struct_def":
            parties.append(pp_struct_def(child))
        elif child.data == "main":
            parties.append(pp_main(child))
    return "\n".join(parties)


if __name__ == "__main__":
    import sys
    fichier = sys.argv[1] if len(sys.argv) > 1 else "source.c"
    src = open(fichier).read()
    arbre = grammaire.parse(src)

    noeud_main     = arbre.children[-1]
    noeud_commande = noeud_main.children[1]

    print("; --- CODE ASSEMBLEUR GÉNÉRÉ ---")
    print(asm_commande(noeud_commande))