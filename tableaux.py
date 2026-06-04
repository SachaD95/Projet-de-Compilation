import lark
grammaire = lark.Lark(r"""
IDENTIFIER: /[a-zA-Z_][a-zA-Z_0-9]*/
TYPE: "int"
OPBIN: /[+\-*\/<>]/

decl : TYPE IDENTIFIER "[" expression "]" -> decl_array
     | TYPE IDENTIFIER                    -> decl_scalar

vars : (decl ",")* decl -> liste_vars

row : "{" [expression ("," expression)*] "}" -> row

expression : IDENTIFIER -> variable
           | SIGNED_NUMBER -> entier
           | expression OPBIN expression -> binaire
           | "(" expression ")"
           | "{" [expression ("," expression)*] "}" -> array_literal
           | "{" row ("," row)* "}"  -> array2d_literal
           | expression "[" expression "]" -> index
           | "len" "(" expression ")" -> len

lvalue : IDENTIFIER
       | lvalue "[" expression "]" -> index_lvalue

commande : lvalue "=" expression ";"                              -> assignation
         | decl ";"                                               -> decl_commande
         | commande*                                              -> sequence
         | "pass"                                                 -> pass
         | "print" "(" expression ")" ";"                        -> print
         | "if" "(" expression ")" "{" commande "}"              -> if
         | "while" "(" expression ")" "{" commande "}"           -> while
         | "for" "(" TYPE IDENTIFIER "=" expression ";"expression ";" IDENTIFIER "=" IDENTIFIER OPBIN expression ")""{" commande "}"-> for

main : "main" "(" vars ")" "{" commande "return" "(" expression ")" ";" "}"

%import common.WS
%import common.SIGNED_NUMBER
%ignore WS
""", start="main", ambiguity="resolve")


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

def pp_lvalue(ast):
    if ast.data == "lvalue":
        return ast.children[0].value
    if ast.data == "index_lvalue":
        return f"{pp_lvalue(ast.children[0])}[{pp_expression(ast.children[1])}]"

def pp_commande(ast):
    if ast.data == "assignation":
        return f"{pp_lvalue(ast.children[0])} = {pp_expression(ast.children[1])};\n"
    if ast.data == "pass":
        return "pass\n"
    if ast.data == "decl_commande":
        return pp_decl(ast.children[0]) + ";\n"
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
        typ     = ast.children[0].value
        var     = ast.children[1].value
        init    = pp_expression(ast.children[2])
        cond    = pp_expression(ast.children[3])
        lhs_inc = ast.children[4].value
        src_inc = ast.children[5].value
        op_inc  = ast.children[6].value
        val_inc = pp_expression(ast.children[7])
        corps   = pp_commande(ast.children[8])
        return f"for ({typ} {var} = {init}; {cond}; {lhs_inc} = {src_inc} {op_inc} {val_inc}) {{\n{corps}}}\n"

def pp_decl(ast):
    if ast.data == "decl_scalar":
        return f"{ast.children[0].value} {ast.children[1].value}"
    if ast.data == "decl_array":
        return f"{ast.children[0].value} {ast.children[1].value}[{pp_expression(ast.children[2])}]"

def pp_vars(ast):
    return ", ".join(pp_decl(d) for d in ast.children)

def pp_main(ast):
    params = pp_vars(ast.children[0])
    corps  = pp_commande(ast.children[1])
    retour = pp_expression(ast.children[2])
    return f"main({params}) {{\n{corps}return ({retour});\n}}"



compteur = iter(range(1000000000))
MAX_TAILLE = 1024
tableaux = set()


def est_entier_litteral(expr_ast):
    if expr_ast.data == "entier":
        return expr_ast.children[0].value
    return None


def nom_racine(noeud):
    if noeud.data in ("lvalue", "variable"):
        return noeud.children[0].value
    if noeud.data in ("index_lvalue", "index"):
        return nom_racine(noeud.children[0])


def asm_expression(ast):
    if ast.data == "variable":
        nom = ast.children[0].value
    # tableau:renvoyer adresse du tableau
        if nom in tableaux:
            return f"    lea rax, [rel {nom}_data]\n"
    # scalaire
        return f"    mov rax, [rel {nom}]\n"

    if ast.data == "entier":
        return f"    mov rax, {ast.children[0].value}\n"

    if ast.data == "binaire":
        gauche = asm_expression(ast.children[0])
        op     = ast.children[1].value
        droite = asm_expression(ast.children[2])
        code   = gauche
        code  += "    push rax\n"
        code  += droite
        code  += "    mov rbx, rax\n"
        code  += "    pop rax\n"
        if op == "+":  code += "    add rax, rbx\n"
        if op == "-":  code += "    sub rax, rbx\n"
        if op == "*":  code += "    imul rax, rbx\n"
        if op == "/":
            code += "    cqo\n"
            code += "    idiv rbx\n"
        if op == "<":
            code += "    cmp rax, rbx\n"
            code += "    setl al\n"
            code += "    movzx rax, al\n"
        if op == ">":
            code += "    cmp rax, rbx\n"
            code += "    setg al\n"
            code += "    movzx rax, al\n"
        return code

    if ast.data == "len":
        inner = ast.children[0]
        if inner.data == "variable":
            # len(t):lit t_len
            nom = inner.children[0].value
            return f"    mov rax, [rel {nom}_len]\n"
        if inner.data == "index":
            # len(t[i]):lire t[i]:adresse:lire [adresse - 8] (convention : longueur juste avant _data)
            nom   = nom_racine(inner.children[0])
            idx_i = asm_expression(inner.children[1])
            code  = idx_i
            code += "    imul rax, 8\n"
            code += f"    lea rbx, [rel {nom}_data]\n"
            code += "    add rax, rbx\n"
            code += "    mov rax, [rax]\n"       # rax = adresse du sous-tableau
            code += "    mov rax, [rax - 8]\n"   # rax = longueur (juste avant _data)
            return code

    if ast.data == "index":
        if ast.children[0].data == "index":
            # t[i][j] — tableau de tableaux
            # étape 1 : lire t[i]:adresse du soustab
            # étape 2 : lire case j dans ce soustab
            nom   = nom_racine(ast)
            idx_i = asm_expression(ast.children[0].children[1])  # i
            idx_j = asm_expression(ast.children[1])               # j
            code  = idx_i
            code += "    imul rax, 8\n"
            code += f"    lea rbx, [rel {nom}_data]\n"
            code += "    add rax, rbx\n"
            code += "    mov rax, [rax]\n"       # rax = adresse soustabt[i]
            code += "    push rax\n"             # sauvegarde adresse
            code += idx_j
            code += "    imul rax, 8\n"
            code += "    pop rbx\n"              # rbx = adresse soutab
            code += "    add rax, rbx\n"
            code += "    mov rax, [rax]\n"       # rax = t[i][j]
            return code
        else:
            # t[i] simple : entier ou adresse de sous-tableau
            nom  = nom_racine(ast)
            idx  = asm_expression(ast.children[1])
            code  = idx
            code += "    imul rax, 8\n"
            code += f"    lea rbx, [rel {nom}_data]\n"
            code += "    add rax, rbx\n"
            code += "    mov rax, [rax]\n"
            return code

    raise ValueError(f"asm_expression : cas non géré → {ast.data}")


def asm_lvalue(ast):

    if ast.data == "lvalue":
        return ast.children[0].value

    if ast.data == "index_lvalue":
        if ast.children[0].data == "index_lvalue":
            # t[i][j] = ...
            nom   = nom_racine(ast)
            idx_i = asm_expression(ast.children[0].children[1])
            idx_j = asm_expression(ast.children[1])
            code  = idx_i
            code += "    imul rax, 8\n"
            code += f"    lea rbx, [rel {nom}_data]\n"
            code += "    add rax, rbx\n"
            code += "    mov rax, [rax]\n"       # rax = adresse soustableau t[i]
            code += "    push rax\n"
            code += idx_j
            code += "    imul rax, 8\n"
            code += "    pop rbx\n"
            code += "    add rax, rbx\n"
            code += "    mov rcx, rax\n"         # rcx = adresse de t[i][j]
            return code
        else:
            # t[i] simple
            nom  = nom_racine(ast)
            idx  = asm_expression(ast.children[1])
            code  = idx
            code += "    imul rax, 8\n"
            code += f"    lea rcx, [rel {nom}_data]\n"
            code += "    add rcx, rax\n"
            return code


def asm_commande(ast):

    if ast.data == "assignation":
        lv  = ast.children[0]
        rhs = ast.children[1]

        # cas : t = {{1,2},{3,4}}  — array2d_literal explicite
        if rhs.data == "array2d_literal":
            nom  = lv.children[0].value
            code = ""
            for i, row in enumerate(rhs.children):
                nb_elems = len(row.children)
                # convention
                # _len juste avant _data 
                code += f"    mov qword [rel {nom}_{i}_len], {nb_elems}\n"
                for j, elem in enumerate(row.children):
                    code += asm_expression(elem)
                    code += f"    mov [rel {nom}_{i}_data + {j*8}], rax\n"
                # stocker l'adresse du soustableau dans t[i]
                code += f"    lea rax, [rel {nom}_{i}_data]\n"
                code += f"    mov [rel {nom}_data + {i*8}], rax\n"
            return code

        # cas : t = {1,2,3} ou t = {{1,2},{3,4}} déguisé en array_literal
        if rhs.data == "array_literal":
            nom  = lv.children[0].value
            # détecter si c'est un 2D déguisé
            if (len(rhs.children) > 0 and hasattr(rhs.children[0], "data") and rhs.children[0].data == "array_literal"):
                # 2D déguisé
                code = ""
                for i, ligne in enumerate(rhs.children):
                    nb_elems = len(ligne.children)
                    code += f"    mov qword [rel {nom}_{i}_len], {nb_elems}\n"
                    for j, elem in enumerate(ligne.children):
                        code += asm_expression(elem)
                        code += f"    mov [rel {nom}_{i}_data + {j*8}], rax\n"
                    code += f"    lea rax, [rel {nom}_{i}_data]\n"
                    code += f"    mov [rel {nom}_data + {i*8}], rax\n"
                return code
            else:
                # 1D normal
                code = ""
                for i, elem in enumerate(rhs.children):
                    code += asm_expression(elem)
                    code += f"    mov [rel {nom}_data + {i*8}], rax\n"
                return code

        # cas normal : scalaire ou case de tableau
        rhs_code = asm_expression(rhs)
        lhs_code = asm_lvalue(lv)

        if lv.data == "lvalue":
            return rhs_code + f"    mov [rel {lhs_code}], rax\n"
        else:
            code  = rhs_code
            code += "    mov r12, rax\n"   # r12 sauvegarde la valeur
            code += lhs_code               # rcx = adresse destination
            code += "    mov [rcx], r12\n"
            return code

    if ast.data == "pass":
        return "    nop\n"

    if ast.data == "decl_commande":
        d   = ast.children[0]
        nom = d.children[1].value
        code = ""
        if d.data == "decl_array":
            if not est_entier_litteral(d.children[2]):
                code += asm_expression(d.children[2])
                code += f"    mov [rel {nom}_len], rax\n"
        return code if code else "    ; declaration locale\n"

    if ast.data == "print":
        return (asm_expression(ast.children[0]) +
                "    mov rsi, rax\n"
                "    mov rdi, format\n"
                "    xor rax, rax\n"
                "    call printf\n")

    if ast.data == "sequence":
        return "".join(asm_commande(c) for c in ast.children)

    if ast.data == "if":
        test = asm_expression(ast.children[0])
        cmd  = asm_commande(ast.children[1])
        cpt  = next(compteur)
        return (test +
                f"    cmp rax, 0\n"
                f"    jz fin_{cpt}\n"
                + cmd +
                f"fin_{cpt}:\n")

    if ast.data == "while":
        test = asm_expression(ast.children[0])
        cmd  = asm_commande(ast.children[1])
        cpt  = next(compteur)
        return (f"debut_{cpt}:\n"
                + test +
                f"    cmp rax, 0\n"
                f"    jz fin_{cpt}\n"
                + cmd +
                f"    jmp debut_{cpt}\n"
                f"fin_{cpt}:\n")

    if ast.data == "for":
        var   = ast.children[1].value
        init  = asm_expression(ast.children[2])
        cond  = asm_expression(ast.children[3])
        op    = ast.children[6].value
        val   = asm_expression(ast.children[7])
        corps = asm_commande(ast.children[8])
        cpt   = next(compteur)

        increment  = f"    mov rax, [rel {var}]\n"
        increment += "    push rax\n"
        increment += val
        increment += "    mov rbx, rax\n"
        increment += "    pop rax\n"
        if op == "+": increment += "    add rax, rbx\n"
        if op == "-": increment += "    sub rax, rbx\n"
        increment += f"    mov [rel {var}], rax\n"

        return (init +
                f"    mov [rel {var}], rax\n"
                f"for_debut_{cpt}:\n"
                + cond +
                f"    cmp rax, 0\n"
                f"    jz for_fin_{cpt}\n"
                + corps
                + increment +
                f"    jmp for_debut_{cpt}\n"
                f"for_fin_{cpt}:\n")

    return "    ; commande non implementee\n"


def asm_decls_vars(ast):
    # réserve la mémoire pour les paramètres de main
    lignes = []
    for d in ast.children:
        nom = d.children[1].value
        if d.data == "decl_scalar":
            lignes.append(f"    {nom}: dq 0")
        if d.data == "decl_array":
            tableaux.add(nom)
            taille_val = est_entier_litteral(d.children[2])
            if taille_val:
                lignes.append(f"    {nom}_len: dq {taille_val}")
                lignes.append(f"    {nom}_data: times {taille_val} dq 0")
            else:
                lignes.append(f"    {nom}_len: dq 0")
                lignes.append(f"    {nom}_data: times {MAX_TAILLE} dq 0")

    return "\n".join(lignes)


def asm_decls_corps(cmd_ast, lignes=None, vus=None):
    # scanne le corps pour trouver toutes les déclarations locales
    if lignes is None: lignes = []
    if vus    is None: vus    = set()

    if cmd_ast.data == "decl_commande":
        d   = cmd_ast.children[0]
        nom = d.children[1].value
        if nom not in vus:
            vus.add(nom)
            if d.data == "decl_scalar":
                lignes.append(f"    {nom}: dq 0")
            if d.data == "decl_array":
                tableaux.add(nom)
                taille_val = est_entier_litteral(d.children[2])

                if taille_val:
                    lignes.append(f"    {nom}_len: dq {taille_val}")
                    lignes.append(f"    {nom}_data: times {taille_val} dq 0")
                else:
                    lignes.append(f"    {nom}_len: dq 0")
                    lignes.append(f"    {nom}_data: times {MAX_TAILLE} dq 0")
    if cmd_ast.data == "for":
        # variable de boucle → scalaire en BSS
        nom = cmd_ast.children[1].value
        if nom not in vus:
            vus.add(nom)
            lignes.append(f"    {nom}: dq 0")

    # scanner les assignations pour détecter les soustableaux t_0, t_1...
    # créés lors d'une initialisation {{1,2},{3,4}}
    if cmd_ast.data == "assignation":
        lv  = cmd_ast.children[0]
        rhs = cmd_ast.children[1]
        if lv.data == "lvalue":
            nom = lv.children[0].value
            rows = None
            if rhs.data == "array2d_literal":
                rows = rhs.children
            elif (rhs.data == "array_literal"
                  and len(rhs.children) > 0
                  and hasattr(rhs.children[0], "data")
                  and rhs.children[0].data == "array_literal"):
                rows = rhs.children
            if rows is not None:
                for i, row in enumerate(rows):
                    sous_nom = f"{nom}_{i}"
                    if sous_nom not in vus:
                        vus.add(sous_nom)
                        nb = len(row.children)

                        lignes.append(f"    {sous_nom}_len: dq {nb}")
                        lignes.append(f"    {sous_nom}_data: times {nb} dq 0")

    for c in cmd_ast.children:
        if hasattr(c, "data"):
            asm_decls_corps(c, lignes, vus)

    return lignes


def asm_vars(ast):
    # lit argv[1], argv[2]... pour initialiser les scalaires
    # calcul les longueurs dynamique pour les tabs
    lignes = []
    i = 0
    for d in ast.children:
        nom = d.children[1].value
        if d.data == "decl_scalar":
            lignes.append(f"    mov rdi, [rel argv]\n"
                          f"    add rdi, {(i+1)*8}\n"
                          f"    mov rdi, [rdi]\n"
                          f"    call atoi\n"
                          f"    mov [rel {nom}], rax")
            i += 1
        if d.data == "decl_array":
            if not est_entier_litteral(d.children[2]):
                lignes.append(
                    asm_expression(d.children[2]) +
                    f"    mov [rel {nom}_len], rax\n")
    return "\n".join(lignes)


def asm_main(ast):
    decls_params = asm_decls_vars(ast.children[0])
    decls_locaux = asm_decls_corps(ast.children[1])

    decls = decls_params
    if decls_locaux:
        decls += "\n" + "\n".join(decls_locaux)

    vs  = asm_vars(ast.children[0])
    cmd = asm_commande(ast.children[1])
    ret = asm_expression(ast.children[2])

    squelette = open("squelette.asm").read()
    squelette = squelette.replace("DECL_VARS", decls)
    squelette = squelette.replace("INIT_VARS", vs)
    squelette = squelette.replace("COMMAND",   cmd)
    squelette = squelette.replace("RETURN",    ret)
    return squelette


if __name__ == "__main__":
    src = open("tab.c").read()
    t   = grammaire.parse(src)

    print("******Pretty-print*********")
    print(pp_main(t))

    asm = asm_main(t)
    with open("result.asm", "w") as f:
        f.write(asm)
    print("******result.asm généré******")
