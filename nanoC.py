import lark


grammaire = lark.Lark(r"""
IDENTIFIER : /[a-zA-Z_][a-zA-Z_0-9]*/
TYPE       : "int"
OPBIN      : /[+\-*\/<>]/

type : TYPE       -> type_int
     | IDENTIFIER -> type_struct

field_decl : type IDENTIFIER -> field_decl

struct_def : "typedef" "struct" "{" (field_decl ";")+ "}" IDENTIFIER ";" -> struct_def

decl : type IDENTIFIER "[" expression "]" -> decl_array
     | type IDENTIFIER                    -> decl_scalar

vars : (decl ",")* decl -> liste_vars

row : "{" [expression ("," expression)*] "}" -> row

expression : IDENTIFIER                                              -> variable
            | SIGNED_NUMBER                                          -> entier
            | expression OPBIN expression                            -> binaire
            | "(" expression ")"
            | "{" [expression ("," expression)*] "}"                 -> array_literal
            | "{" row ("," row)* "}"                                 -> array2d_literal
            | expression "[" expression "]" "[" expression "]"       -> index2d
            | expression "[" expression "]"                          -> index
            | expression "." IDENTIFIER                              -> field_access
            | "len" "(" expression ")"                                -> len
            | IDENTIFIER "(" [expression ("," expression)*] ")"       -> appel

lvalue : IDENTIFIER                                                  -> lvalue
       | lvalue "[" expression "]" "[" expression "]"                 -> index2d_lvalue
       | lvalue "[" expression "]"                                   -> index_lvalue
       | lvalue "." IDENTIFIER                                       -> field_lvalue

commande : lvalue "=" expression ";"                                  -> assignation
         | type IDENTIFIER "=" expression ";"                         -> decl_init
         | decl ";"                                                   -> decl_commande
         | commande* -> sequence
         | "pass"                                                     -> pass
         | "print" "(" expression ")" ";"                             -> print
         | "if" "(" expression ")" "{" commande "}"                   -> if
         | "while" "(" expression ")" "{" commande "}"                -> while
         | "for" "(" TYPE IDENTIFIER "=" expression ";" expression ";" IDENTIFIER "=" IDENTIFIER OPBIN expression ")""{" commande "}" -> for
 
fonction : type IDENTIFIER "(" vars ")" "{" commande "return" "(" expression ")" ";" "}" -> fonction

main : "main" "(" vars ")" "{" commande "return" "(" expression ")" ";" "}" -> main

programme : (struct_def | fonction | (decl ";"))* main -> programme

%import common.WS
%import common.SIGNED_NUMBER
%ignore WS
""", start="programme", ambiguity="resolve")

compteur = iter(range(1000000000))
MAX_TAILLE = 1024
tableaux = set()

tmp_counter = 0

def generer_nom_temp():
    global tmp_counter
    tmp_counter += 1
    return f"__tmp_{tmp_counter}"


def pp_type(ast):
    if ast.data == "type_int":
        return "int"
    if ast.data == "type_struct":
        return ast.children[0].value

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
    if ast.data == "index2d":
        return f"{pp_expression(ast.children[0])}[{pp_expression(ast.children[1])}][{pp_expression(ast.children[2])}]"
    if ast.data == "row":
        elements = ", ".join(pp_expression(c) for c in ast.children)
        return "{" + elements + "}"
    if ast.data == "array2d_literal":
        lignes = ", ".join(pp_expression(r) for r in ast.children)
        return "{" + lignes + "}"
    if ast.data == "array_literal":
        elements = ", ".join(pp_expression(c) for c in ast.children)
        return "{" + elements + "}"
    if ast.data == "len":
        return f"len({pp_expression(ast.children[0])})"
    if ast.data == "field_access":
        base  = pp_expression(ast.children[0])
        champ = ast.children[1].value
        return f"{base}.{champ}"
    if ast.data == "appel":
        nom  = ast.children[0].value
        args = ", ".join(pp_expression(a) for a in ast.children[1:])
        return f"{nom}({args})"
    raise ValueError(f"pp_expression : cas non géré -> {ast.data}")

def pp_lvalue(ast):
    if ast.data == "lvalue":
        return ast.children[0].value
    if ast.data == "index_lvalue":
        return f"{pp_lvalue(ast.children[0])}[{pp_expression(ast.children[1])}]"
    if ast.data == "index2d_lvalue":
        return f"{pp_lvalue(ast.children[0])}[{pp_expression(ast.children[1])}][{pp_expression(ast.children[2])}]"
    if ast.data == "field_lvalue":
        base  = pp_lvalue(ast.children[0])
        champ = ast.children[1].value
        return f"{base}.{champ}"
    raise ValueError(f"pp_lvalue : cas non géré -> {ast.data}")

def pp_decl(ast):
    if ast.data == "decl_scalar":
        typ = pp_type(ast.children[0])
        nom = ast.children[1].value
        return f"{typ} {nom}"
    if ast.data == "decl_array":
        typ    = pp_type(ast.children[0])
        nom    = ast.children[1].value
        taille = pp_expression(ast.children[2])
        return f"{typ} {nom}[{taille}]"
    raise ValueError(f"pp_decl : cas non géré -> {ast.data}")

def pp_vars(ast):
    return ", ".join(pp_decl(d) for d in ast.children)

def pp_field_decl(ast):
    typ = pp_type(ast.children[0])
    nom = ast.children[1].value
    return f"    {typ} {nom}"

def pp_struct_def(ast):
    champs = [pp_field_decl(c) for c in ast.children[:-1]]
    nom    = ast.children[-1].value
    corps  = ";\n".join(champs) + ";\n" if champs else ""
    return f"typedef struct {{\n{corps}}} {nom};\n"

def pp_commande(ast):
    if ast.data == "assignation":
        lhs = pp_lvalue(ast.children[0])
        rhs = pp_expression(ast.children[1])
        return f"{lhs} = {rhs};\n"
    if ast.data == "decl_init":
        typ = pp_type(ast.children[0])
        nom = ast.children[1].value
        val = pp_expression(ast.children[2])
        return f"{typ} {nom} = {val};\n"
    if ast.data == "decl_commande":
        return pp_decl(ast.children[0]) + ";\n"
    if ast.data == "pass":
        return "pass\n"
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
        return (f"for ({typ} {var} = {init}; {cond}; "
                f"{lhs_inc} = {src_inc} {op_inc} {val_inc}) {{\n{corps}}}\n")
    raise ValueError(f"pp_commande : cas non géré -> {ast.data}")

def pp_fonction(ast):
    typ    = pp_type(ast.children[0])
    nom    = ast.children[1].value
    params = pp_vars(ast.children[2])
    corps  = pp_commande(ast.children[3])
    retour = pp_expression(ast.children[4])
    return f"{typ} {nom}({params}) {{\n{corps}return ({retour});\n}}\n"

def pp_main(ast):
    params = pp_vars(ast.children[0])
    corps  = pp_commande(ast.children[1])
    retour = pp_expression(ast.children[2])
    return f"main({params}) {{\n{corps}return ({retour});\n}}\n"

def pp_programme(ast):
    morceaux = []
    for enfant in ast.children:
        if enfant.data == "struct_def":
            morceaux.append(pp_struct_def(enfant))
        elif enfant.data == "fonction":
            morceaux.append(pp_fonction(enfant))
        elif enfant.data == "main":
            morceaux.append(pp_main(enfant))
        elif enfant.data in ("decl_array", "decl_scalar"):
            morceaux.append(pp_decl(enfant) + ";")
        else:
            if hasattr(enfant, "data") and len(enfant.children) > 0:
                morceaux.append(pp_decl(enfant.children[0]) + ";")
    return "\n".join(morceaux)


def est_entier_litteral(expr_ast):
    if expr_ast.data == "entier":
        return expr_ast.children[0].value
    return None

def nom_racine(noeud):
    if noeud.data in ("lvalue", "variable"):
        return noeud.children[0].value
    if noeud.data in ("index_lvalue", "index", "index2d_lvalue", "index2d"):
        return nom_racine(noeud.children[0])

def asm_expression(ast, contexte=None):
    if contexte is None:
        contexte = {}

    if ast.data == "variable":
        nom = ast.children[0].value
        if nom in contexte:
            return f"    mov rax, [rbp{contexte[nom]}]\n"
        if nom in tableaux:
            return f"    lea rax, [rel {nom}_data]\n"
        return f"    mov rax, [rel {nom}]\n"

    if ast.data == "entier":
        return f"    mov rax, {ast.children[0].value}\n"

    if ast.data == "appel":
        nom = ast.children[0].value
        args = ast.children[1:] if len(ast.children) > 1 else []
        regs = ["rdi", "rsi", "rdx", "rcx", "r8", "r9"]
        code = ""
        
        arg_tmps = []
        for arg in args:
            code += asm_expression(arg, contexte)
            if not hasattr(arg, 'temp_var'):
                arg.temp_var = generer_nom_temp()
                if arg.temp_var not in contexte:
                    contexte[arg.temp_var] = -(len(contexte) + 1) * 8
            
            offset = contexte[arg.temp_var]
            code += f"    mov [rbp{offset}], rax\n"
            arg_tmps.append(arg.temp_var)
            
        for i, tmp_name in enumerate(arg_tmps):
            offset = contexte[tmp_name]
            code += f"    mov {regs[i]}, [rbp{offset}]\n"
            
        code += f"    call {nom}\n"
        return code

    if ast.data == "binaire":
        op = ast.children[1].value
        
        if not hasattr(ast.children[0], 'temp_var'):
            ast.children[0].temp_var = generer_nom_temp()
            if ast.children[0].temp_var not in contexte:
                contexte[ast.children[0].temp_var] = -(len(contexte) + 1) * 8
                
        code = asm_expression(ast.children[0], contexte)
        offset_gauche = contexte[ast.children[0].temp_var]
        code += f"    mov [rbp{offset_gauche}], rax\n"
        
        code += asm_expression(ast.children[2], contexte)
        
        code += f"    mov rbx, rax\n"
        code += f"    mov rax, [rbp{offset_gauche}]\n"
        
        if op == "+":  code += "    add rax, rbx\n"
        if op == "-":  code += "    sub rax, rbx\n"
        if op == "*":  code += "    imul rax, rbx\n"
        if op == "/":  code += "    cqo\n    idiv rbx\n"
        if op == "<":  code += "    cmp rax, rbx\n    setl al\n    movzx rax, al\n"
        if op == ">":  code += "    cmp rax, rbx\n    setg al\n    movzx rax, al\n"
        return code

    if ast.data == "len":
        inner = ast.children[0]
        if inner.data == "variable":
            nom = inner.children[0].value
            return f"    mov rax, [rel {nom}_len]\n"
        if inner.data == "index":
            nom   = nom_racine(inner.children[0])
            idx_i = asm_expression(inner.children[1], contexte)
            code  = idx_i
            code += "    imul rax, 8\n"
            code += f"    lea rbx, [rel {nom}_data]\n"
            code += "    add rax, rbx\n"
            code += "    mov rax, [rax]\n"       
            code += "    mov rax, [rax - 8]\n"   
            return code

    if ast.data in ("index", "index2d"):
        nom = nom_racine(ast)
        if ast.data == "index2d" or (ast.children[0].data in ("index", "index_lvalue")):
            idx_i = asm_expression(ast.children[0].children[1], contexte)
            idx_j = asm_expression(ast.children[2] if ast.data == "index2d" else ast.children[1], contexte)
            code  = idx_i
            code += "    imul rax, 8\n"
            code += f"    lea rbx, [rel {nom}_data]\n"
            code += "    add rax, rbx\n"
            code += "    mov rax, [rax]\n"       
            code += "    push rax\n"             
            code += idx_j
            code += "    imul rax, 8\n"
            code += "    pop rbx\n"              
            code += "    add rax, rbx\n"
            code += "    mov rax, [rax]\n"       
            return code
        else:
            idx  = asm_expression(ast.children[1], contexte)
            code  = idx
            code += "    imul rax, 8\n"
            code += f"    lea rbx, [rel {nom}_data]\n"
            code += "    add rax, rbx\n"
            code += "    mov rax, [rax]\n"
            return code

    raise ValueError(f"asm_expression : cas non géré -> {ast.data}")

def asm_lvalue(ast, contexte=None):
    if contexte is None:
        contexte = {}
    if ast.data == "lvalue":
        return ast.children[0].value

    if ast.data in ("index_lvalue", "index2d_lvalue"):
        nom = nom_racine(ast)
        if ast.data == "index2d_lvalue" or ast.children[0].data == "index_lvalue":
            idx_i = asm_expression(ast.children[0].children[1], contexte)
            idx_j = asm_expression(ast.children[2] if ast.data == "index2d_lvalue" else ast.children[1], contexte)
            code  = idx_i
            code += "    imul rax, 8\n"
            code += f"    lea rbx, [rel {nom}_data]\n"
            code += "    add rax, rbx\n"
            code += "    mov rax, [rax]\n"       
            code += "    push rax\n"
            code += idx_j
            code += "    imul rax, 8\n"
            code += "    pop rbx\n"
            code += "    add rax, rbx\n"
            code += "    mov rcx, rax\n"         
            return code
        else:
            idx  = asm_expression(ast.children[1], contexte)
            code  = idx
            code += "    imul rax, 8\n"
            code += f"    lea rcx, [rel {nom}_data]\n"
            code += "    add rcx, rax\n"
            return code

def asm_commande(ast, contexte=None):
    if contexte is None:
        contexte = {}

    if ast.data == "assignation":
        lv  = ast.children[0]
        rhs = ast.children[1]
        nom = nom_racine(lv)

        if rhs.data == "array2d_literal":
            code = ""
            for i, row in enumerate(rhs.children):
                nb_elems = len(row.children)
                code += f"    mov qword [rel {nom}_{i}_len], {nb_elems}\n"
                for j, elem in enumerate(row.children):
                    code += asm_expression(elem, contexte)
                    code += f"    mov [rel {nom}_{i}_data + {j*8}], rax\n"
                code += f"    lea rax, [rel {nom}_{i}_data]\n"
                code += f"    mov [rel {nom}_data + {i*8}], rax\n"
            return code

        if rhs.data == "array_literal":
            if (len(rhs.children) > 0 and hasattr(rhs.children[0], "data") and rhs.children[0].data == "array_literal"):
                code = ""
                for i, ligne in enumerate(rhs.children):
                    nb_elems = len(ligne.children)
                    code += f"    mov qword [rel {nom}_{i}_len], {nb_elems}\n"
                    for j, elem in enumerate(ligne.children):
                        code += asm_expression(elem, contexte)
                        code += f"    mov [rel {nom}_{i}_data + {j*8}], rax\n"
                    code += f"    lea rax, [rel {nom}_{i}_data]\n"
                    code += f"    mov [rel {nom}_data + {i*8}], rax\n"
                return code
            else:
                code = ""
                for i, elem in enumerate(rhs.children):
                    code += asm_expression(elem, contexte)
                    code += f"    mov [rel {nom}_data + {i*8}], rax\n"
                return code

        rhs_code = asm_expression(rhs, contexte)
        if lv.data == "lvalue":
            v_nom = lv.children[0].value
            if v_nom in contexte:
                return rhs_code + f"    mov [rbp{contexte[v_nom]}], rax\n"
            return rhs_code + f"    mov [rel {v_nom}], rax\n"
        else:
            lhs_code = asm_lvalue(lv, contexte)
            code  = rhs_code
            code += "    mov r12, rax\n"   
            code += lhs_code               
            code += "    mov [rcx], r12\n"
            return code

    if ast.data == "decl_init":
        v_nom = ast.children[1].value
        rhs_code = asm_expression(ast.children[2], contexte)
        if v_nom in contexte:
            return rhs_code + f"    mov [rbp{contexte[v_nom]}], rax\n"
        return rhs_code + f"    mov [rel {v_nom}], rax\n"

    if ast.data == "pass":
        return "    nop\n"

    if ast.data == "decl_commande":
        d   = ast.children[0]
        v_nom = d.children[1].value
        code = ""
        if d.data == "decl_array":
            if not est_entier_litteral(d.children[2]):
                code += asm_expression(d.children[2], contexte)
                code += f"    mov [rel {v_nom}_len], rax\n"
        return code if code else "    ; declaration locale\n"

    if ast.data == "print":
        return (asm_expression(ast.children[0], contexte) +
                "    mov rsi, rax\n"
                "    mov rdi, format\n"
                "    xor rax, rax\n"
                "    call printf\n")

    if ast.data == "sequence":
        return "".join(asm_commande(c, contexte) for c in ast.children)

    if ast.data == "if":
        test = asm_expression(ast.children[0], contexte)
        cmd  = asm_commande(ast.children[1], contexte)
        cpt  = next(compteur)
        return test + f"    cmp rax, 0\n    jz fin_{cpt}\n" + cmd + f"fin_{cpt}:\n"

    if ast.data == "while":
        test = asm_expression(ast.children[0], contexte)
        cmd  = asm_commande(ast.children[1], contexte)
        cpt  = next(compteur)
        return f"debut_{cpt}:\n" + test + f"    cmp rax, 0\n    jz fin_{cpt}\n" + cmd + f"    jmp debut_{cpt}\n" + f"fin_{cpt}:\n"

    if ast.data == "for":
        var   = ast.children[1].value
        init  = asm_expression(ast.children[2], contexte)
        cond  = asm_expression(ast.children[3], contexte)
        op    = ast.children[6].value
        val   = asm_expression(ast.children[7], contexte)
        corps = asm_commande(ast.children[8], contexte)
        cpt   = next(compteur)

        get_var = f"    mov rax, [rbp{contexte[var]}]\n" if var in contexte else f"    mov rax, [rel {var}]\n"
        set_var = f"    mov [rbp{contexte[var]}], rax\n" if var in contexte else f"    mov [rel {var}], rax\n"

        increment  = get_var + "    push rax\n" + val + "    mov rbx, rax\n    pop rax\n"
        if op == "+": increment += "    add rax, rbx\n"
        if op == "-": increment += "    sub rax, rbx\n"
        increment += set_var

        return init + set_var + f"for_debut_{cpt}:\n" + cond + f"    cmp rax, 0\n    jz for_fin_{cpt}\n" + corps + increment + f"    jmp for_debut_{cpt}\n" + f"for_fin_{cpt}:\n"

    return "    ; to be implemented\n"

def scan_variables(noeud, contexte):
    if not hasattr(noeud, "data"):
        return

    if noeud.data in ("assignation", "decl_init"):
        v = nom_racine(noeud.children[0]) if noeud.data == "assignation" else noeud.children[1].value
        if v not in contexte:
            contexte[v] = -(len(contexte) + 1) * 8
            
    elif noeud.data == "for":
        v = noeud.children[1].value
        if v not in contexte:
            contexte[v] = -(len(contexte) + 1) * 8
            
    elif noeud.data in ("binaire", "appel"):
        noeud.temp_var = generer_nom_temp()
        if noeud.temp_var not in contexte:
            contexte[noeud.temp_var] = -(len(contexte) + 1) * 8

    for child in noeud.children:
        if isinstance(child, lark.Tree):
            scan_variables(child, contexte)

def asm_main(ast):
    contexte = {}
    for c in ast.children[1:-1]:
        scan_variables(c, contexte)
    if len(ast.children) > 0:
        scan_variables(ast.children[-1], contexte)
        
    taille_locales = len(contexte) * 8
    taille = ((taille_locales + 15) // 16) * 16

    init = ""
    if len(ast.children) > 0 and hasattr(ast.children[0], "children"):
        for i, d in enumerate(ast.children[0].children):
            if hasattr(d, "children") and len(d.children) > 1:
                name = d.children[1].value
                if name not in contexte:
                    contexte[name] = -(len(contexte) + 1) * 8
                offset = contexte[name]
                init += f"    mov rdi, [argv]\n    mov rdi, [rdi + {(i+1)*8}]\n    call atoi\n    mov [rbp{offset}], rax\n"

    body = ""
    for c in ast.children[1:-1]:
        body += asm_commande(c, contexte)
    ret = asm_expression(ast.children[-1], contexte)

    return f"""
main:
    push rbp
    mov rbp, rsp
    sub rsp, {taille + 16}
    mov [argv], rsi
{init}
{body}
{ret}
    add rsp, {taille + 16}
    pop rbp
    ret
"""

def asm_fonction(ast):
    nom    = ast.children[1].value
    params = ast.children[2].children
    regs = ["rdi", "rsi", "rdx", "rcx", "r8", "r9"]
    contexte = {}

    for i, p in enumerate(params):
        contexte[p.children[1].value] = -(i + 1) * 8

    for c in ast.children[3:-1]:
        scan_variables(c, contexte)
    if len(ast.children) > 0:
        scan_variables(ast.children[-1], contexte)
        
    taille_locales = len(contexte) * 8
    taille = ((taille_locales + 15) // 16) * 16

    save_params = ""
    for i, p in enumerate(params):
        name = p.children[1].value
        save_params += f"    mov [rbp{contexte[name]}], {regs[i]}\n"

    body = ""
    for c in ast.children[3:-1]:
        body += asm_commande(c, contexte)
    ret = asm_expression(ast.children[-1], contexte)

    return f"""
{nom}:
    push rbp
    mov rbp, rsp
    sub rsp, {taille + 16}
{save_params}
{body}
{ret}
    mov rsp, rbp
    pop rbp
    ret
"""

def asm_decls_globales(ast):
    lignes = ["section .data", '    format: db "%d", 10, 0', "    argv: dq 0"]
    
    for noeud in ast.children:
        if hasattr(noeud, "data") and noeud.data in ("decl_scalar", "decl_array"):
            nom = noeud.children[1].value
            if noeud.data == "decl_scalar":
                lignes.append(f"    {nom}: dq 0")
            elif noeud.data == "decl_array":
                tableaux.add(nom)
                t_val = est_entier_litteral(noeud.children[2])
                taille_v = int(t_val) if t_val else MAX_TAILLE
                lignes.append(f"    {nom}_len: dq {taille_v if t_val else 0}")
                lignes.append(f"    {nom}_data: times {taille_v} dq 0")
                for k in range(taille_v):
                    lignes.append(f"    {nom}_{k}_len: dq 0")
                    lignes.append(f"    {nom}_{k}_data: times {MAX_TAILLE} dq 0")

    lignes.append("\nsection .text")
    lignes.append("    global main")
    lignes.append("    extern printf")
    lignes.append("    extern atoi")
    return "\n".join(lignes)

def asm_programme(ast):
    globales = asm_decls_globales(ast)
    fonctions_code = []
    main_code = ""

    for f in ast.children:
        if hasattr(f, "data") and f.data == "fonction":
            fonctions_code.append(asm_fonction(f))
        elif hasattr(f, "data") and f.data == "main":
            main_code = asm_main(f)

    code = globales + "\n" + "\n".join(fonctions_code) + "\n" + main_code
    
   
    code += "\n\nsection .note.GNU-stack noalloc noexec nowrite progbits\n"
    
    return code



if __name__ == "__main__":
    src = open("test.c").read()
    t = grammaire.parse(src)

    print("****** Pretty-print *********")
    print(pp_programme(t))
    
    print("\n****** Code ASM Géré *********")
    with open("result.asm", "w") as f:
       f.write(asm_programme(t))