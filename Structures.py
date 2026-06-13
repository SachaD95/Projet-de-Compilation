import lark
import sys
import os

# ==========================================
# GRAMMAIRE LARK
# ==========================================
grammaire = lark.Lark(r"""
IDENTIFIER: /[a-zA-Z_][a-zA-Z_0-9]*/
TYPE: "int"
OPBIN: /[+\/*<>-]/

field_decl : (TYPE | IDENTIFIER) IDENTIFIER
struct_def : "typedef" "struct" "{" (field_decl ";")+ "}" IDENTIFIER ";"

decl : (TYPE | IDENTIFIER) IDENTIFIER
vars : decl ("," decl)* -> liste_vars
     |                  -> vide

expression : IDENTIFIER -> variable
        | SIGNED_NUMBER -> entier
        | expression OPBIN expression -> binaire
        | IDENTIFIER "(" args ")" -> appel
        | expression "." IDENTIFIER -> field_access

args : expression ("," expression)* -> liste_args
     |                              -> vide

commande : lvalue "=" expression ";" -> assignation
        | "print" "(" expression ")" ";" -> print_cmd
        | IDENTIFIER "(" args ")" ";" -> appel_cmd
        | decl ";" -> decl_commande
        | decl "=" expression ";" -> decl_init
        | "pass" ";" -> pass_cmd
        | "if" "(" expression ")" "{" commande* "}" -> if_cmd
        | "while" "(" expression ")" "{" commande* "}" -> while_cmd

lvalue : IDENTIFIER -> var_lvalue
        | lvalue "." IDENTIFIER -> field_lvalue

retour : "return" "(" expression ")" ";"
       | "return" expression ";"

fonction : TYPE IDENTIFIER "(" vars ")" "{" commande* retour "}"
main : ["int"] "main" "(" vars ")" "{" commande* retour "}"

programme : struct_def* fonction* main

%import common.WS
%import common.SIGNED_NUMBER
COMMENT: "//" /[^\n]*/ "\n"
%ignore COMMENT
%ignore WS
""", start="programme")

compteur = iter(range(1000000000)) 

structures = {}
structures_tailles = {}

def analyser_structures(ast):
    global structures, structures_tailles
    structures.clear()
    structures_tailles.clear()
    for child in ast.children:
        if child.data == "struct_def":
            nom_struct = child.children[-1].value
            champs = {}
            offset_courant = 0
            for field in child.children[:-1]:
                type_champ = field.children[0].value
                nom_champ = field.children[1].value
                champs[nom_champ] = {"offset": offset_courant, "type": type_champ}
                offset_courant += structures_tailles.get(type_champ, 8) if type_champ != "int" else 8
            structures[nom_struct] = champs
            structures_tailles[nom_struct] = offset_courant

def get_components(ast):
    typ, nom, vs_node, cmds, ret_node = None, None, None, [], None
    for c in ast.children:
        if isinstance(c, lark.Token):
            if c.type == "TYPE": typ = c.value
            elif c.type == "IDENTIFIER": nom = c.value
        elif isinstance(c, lark.Tree):
            if c.data in ("liste_vars", "vide"): vs_node = c
            elif c.data == "retour": ret_node = c
            else: cmds.append(c)
    return typ, nom, vs_node, cmds, ret_node

def fmt_offset(offset):
    if offset < 0:
        return f"[rbp{offset}]"
    elif offset > 0:
        return f"[rbp+{offset}]"
    else:
        return "[rbp]"

# ==========================================
# PRETTY PRINTER (pp)
# ==========================================
def pp_expression(ast):
    if ast.data in ("variable", "entier"): return ast.children[0].value
    if ast.data == "appel": return f"{ast.children[0].value}({pp_args(ast.children[1])})"
    if ast.data == "field_access": return f"{pp_expression(ast.children[0])}.{ast.children[1].value}"
    return f"{pp_expression(ast.children[0])} {ast.children[1].value} {pp_expression(ast.children[2])}"

def pp_args(ast):
    if not ast.children: return ""
    return ", ".join(pp_expression(arg) for arg in ast.children)

def pp_lvalue(ast):
    if ast.data == "var_lvalue": return ast.children[0].value
    if ast.data == "field_lvalue": return f"{pp_lvalue(ast.children[0])}.{ast.children[1].value}"

def pp_commande(ast, indent_lvl=1):
    ind = "    " * indent_lvl
    if ast.data == "assignation": return f"{ind}{pp_lvalue(ast.children[0])} = {pp_expression(ast.children[1])};\n"
    if ast.data == "appel_cmd": return f"{ind}{ast.children[0].value}({pp_args(ast.children[1])});\n"
    if ast.data == "decl_commande": return f"{ind}{ast.children[0].children[0].value} {ast.children[0].children[1].value};\n"
    if ast.data == "decl_init": return f"{ind}{ast.children[0].children[0].value} {ast.children[0].children[1].value} = {pp_expression(ast.children[1])};\n"
    if ast.data == "pass_cmd": return f"{ind}pass;\n"
    if ast.data == "print_cmd": return f"{ind}print({pp_expression(ast.children[0])});\n"
    if ast.data == "if_cmd": return f"{ind}if ({pp_expression(ast.children[0])}) {{\n{''.join(pp_commande(c, indent_lvl+1) for c in ast.children[1:])}{ind}}}\n"
    if ast.data == "while_cmd": return f"{ind}while ({pp_expression(ast.children[0])}) {{\n{''.join(pp_commande(c, indent_lvl+1) for c in ast.children[1:])}{ind}}}\n"
    return ""

def pp_vars(ast):
    if not ast or not ast.children: return ""
    return ", ".join(f"{v.children[0].value} {v.children[1].value}" for v in ast.children)

def pp_programme(ast):
    out = ""
    for c in ast.children:
        if c.data == "struct_def":
            champs = "\n".join(f"    {f.children[0].value} {f.children[1].value};" for f in c.children[:-1])
            out += f"typedef struct {{\n{champs}\n}} {c.children[-1].value};\n\n"
        elif c.data in ("fonction", "main"):
            typ, nom, vs, cmds, ret = get_components(c)
            sig = f"{typ + ' ' if typ else ''}{nom if nom else 'main'}({pp_vars(vs)})"
            corps = "".join(pp_commande(cmd, 1) for cmd in cmds)
            out += f"{sig} {{\n{corps}    return ({pp_expression(ret.children[0])});\n}}\n\n"
    return out

# ==========================================
# GENERATEUR ASSEMBLEUR
# ==========================================
def asm_expression(ast, contexte={}):
    if ast.data == "variable":
        if ast.children[0].value not in contexte: raise NameError(f"Variable '{ast.children[0].value}' non declaree.")
        info = contexte[ast.children[0].value]
        return f"    mov rax, {fmt_offset(info['offset'])}\n", info["type"]
    if ast.data == "entier": return f"    mov rax, {ast.children[0].value}\n", "int"
    
    if ast.data == "appel":
        nom = ast.children[0].value
        
        if nom in structures:
            champs_attendus = list(structures[nom].values())
            args_fournis = ast.children[1].children
            
            if len(args_fournis) != len(champs_attendus):
                raise TypeError(f"La structure '{nom}' attend {len(champs_attendus)} arguments, mais {len(args_fournis)} ont ete fournis.")
            
            code = ""
            for i, arg in enumerate(args_fournis):
                c_arg, t_arg = asm_expression(arg, contexte)
                type_attendu = champs_attendus[i]["type"]
                
                if t_arg != type_attendu:
                    raise TypeError(f"Init de '{nom}' (argument {i+1}) : type '{t_arg}' recu, mais '{type_attendu}' était attendu.")
                
                code += c_arg + "    push rax\n"
            return code, nom
        
        else:
            code = ""
            args = ast.children[1].children
            for arg in args:
                c_arg, _ = asm_expression(arg, contexte)
                code += c_arg + "    push rax\n"
            for i in range(len(args)-1, -1, -1): code += f"    pop {['rdi','rsi','rdx','rcx','r8','r9'][i]}\n"
            return code + f"    call {nom}\n", "int"
            
    if ast.data == "field_access":
        champs = []; noeud = ast
        while noeud.data == "field_access": champs.insert(0, noeud.children[1].value); noeud = noeud.children[0]
        nom_var = noeud.children[0].value
        if nom_var not in contexte: raise NameError(f"Variable '{nom_var}' inconnue.")
        info, off = contexte[nom_var]["type"], contexte[nom_var]["offset"]
        for ch in champs:
            if info not in structures: raise TypeError(f"'{info}' n'est pas une structure.")
            if ch not in structures[info]: raise AttributeError(f"Champ '{ch}' introuvable.")
            off += structures[info][ch]["offset"]; info = structures[info][ch]["type"]
        return f"    mov rax, {fmt_offset(off)}\n", info

    cg, tg = asm_expression(ast.children[0], contexte)
    op = ast.children[1].value
    cd, td = asm_expression(ast.children[2], contexte)
    if tg != "int" or td != "int": raise TypeError("Opérations arithmétiques interdites sur les structures.")
    if op == "+": return cg + "    push rax\n" + cd + "    pop rbx\n    add rax, rbx\n", "int"
    if op == "-": return cg + "    push rax\n" + cd + "    push rax\n    pop rbx\n    pop rax\n    sub rax, rbx\n", "int"
    if op == "*": return cg + "    push rax\n" + cd + "    pop rbx\n    imul rax, rbx\n", "int"
    return "", "int"

def asm_commande(ast, contexte={}):
    if ast.data == "assignation":
        lhs, rhs = ast.children[0], ast.children[1]
        crhs, trhs = asm_expression(rhs, contexte)
        nom_v = lhs.children[0].value if lhs.data == "var_lvalue" else lhs.children[0].children[0].value
        if nom_v not in contexte: raise NameError(f"'{nom_v}' introuvable.")
        info, off = contexte[nom_v]["type"], contexte[nom_v]["offset"]
        if lhs.data == "field_lvalue":
            champs = []; noeud = lhs
            while noeud.data == "field_lvalue": champs.insert(0, noeud.children[1].value); noeud = noeud.children[0]
            for ch in champs:
                off += structures[info][ch]["offset"]; info = structures[info][ch]["type"]
        if info != trhs: raise TypeError(f"Affectation impossible de '{trhs}' dans '{info}'.")
        return f"{crhs}    mov {fmt_offset(off)}, rax\n\n"

    if ast.data == "appel_cmd":
        noeud_appel = lark.Tree("appel", ast.children)
        return asm_expression(noeud_appel, contexte)[0]
        
    if ast.data == "decl_commande":
        return ""

    if ast.data == "decl_init":
        nom_v, typ_v = ast.children[0].children[1].value, ast.children[0].children[0].value
        crhs, trhs = asm_expression(ast.children[1], contexte)
        if typ_v != trhs: raise TypeError(f"Init de '{nom_v}' : type '{trhs}' reçu, '{typ_v}' attendu.")
        off = contexte[nom_v]["offset"]
        
        # CAS 1 : Copie sans commentaires
        if typ_v in structures and ast.children[1].data == "variable":
            nom_source = ast.children[1].children[0].value
            off_source = contexte[nom_source]["offset"]
            code = ""
            for _, c_inf in sorted(structures[typ_v].items(), key=lambda i: i[1]["offset"]):
                code += f"    mov rax, {fmt_offset(off_source + c_inf['offset'])}\n"
                code += f"    mov {fmt_offset(off + c_inf['offset'])}, rax\n"
            return code + "\n"
            
        # CAS 2 : Constructeur sans commentaires
        code = crhs
        if typ_v in structures:
            for _, c_inf in sorted(structures[typ_v].items(), key=lambda i: i[1]["offset"], reverse=True):
                code += f"    pop rax\n    mov {fmt_offset(off + c_inf['offset'])}, rax\n"
        else: code += f"    mov {fmt_offset(off)}, rax\n"
        return code + "\n"

    if ast.data == "pass_cmd":
        return "    nop\n\n"

    if ast.data == "print_cmd":
        c_ex, t_ex = asm_expression(ast.children[0], contexte)
        if t_ex != "int": raise TypeError("print() n'affiche que des entiers.")
        return c_ex + "    mov rdi, format\n    mov rsi, rax\n    xor rax, rax\n    call printf\n\n"

    if ast.data == "if_cmd":
        code_test, _ = asm_expression(ast.children[0], contexte)
        cmd_str = "".join(asm_commande(c, contexte) for c in ast.children[1:])
        cpt = next(compteur)
        return f"{code_test}    cmp rax, 0\n    jz fin_{cpt}\n{cmd_str}fin_{cpt}:\n\n"

    if ast.data == "while_cmd":
        code_test, _ = asm_expression(ast.children[0], contexte)
        cmd_str = "".join(asm_commande(c, contexte) for c in ast.children[1:])
        cpt = next(compteur)
        return f"debut_{cpt}:\n{code_test}    cmp rax, 0\n    jz fin_{cpt}\n{cmd_str}    jmp debut_{cpt}\nfin_{cpt}:\n\n"
        
    return ""

def asm_vars(vs_node):
    if not vs_node or not vs_node.children: 
        return ""
    code = "    push rsi\n"
    for i in range(len(vs_node.children)):
        nom_var = vs_node.children[i].children[1].value
        offset = (i + 1) * 8
        code += f"    mov rdi, [rsp]\n"
        code += f"    mov rdi, [rdi + {offset}]\n"
        code += f"    call atoi\n"
        code += f"    mov [{nom_var}], rax\n"
    code += "    pop rsi\n"
    return code

def asm_decls_vars(vs_node):
    if not vs_node or not vs_node.children: return ""
    return "\n".join(f"{vs_node.children[i].children[1].value}: dq 0" for i in range(len(vs_node.children)))

def asm_fonction(ast):
    typ, nom, vs_node, cmds, ret_node = get_components(ast)
    params = vs_node.children if vs_node else []
    regs = ["rdi", "rsi", "rdx", "rcx", "r8", "r9"]
    contexte = {}
    
    offset_courant = -8
    for i, p in enumerate(params):
        contexte[p.children[1].value] = {"type": p.children[0].value, "offset": offset_courant}
        offset_courant -= 8
        
    def trouver_locales(cmd):
        nonlocal offset_courant
        if cmd.data in ("decl_init", "decl_commande"):
            d = cmd.children[0]
            typ_v, nom_v = d.children[0].value, d.children[1].value
            taille = structures_tailles.get(typ_v, 8)
            offset_courant -= taille
            contexte[nom_v] = {"type": typ_v, "offset": offset_courant}
        elif cmd.data in ("if_cmd", "while_cmd"):
            for c in cmd.children[1:]: trouver_locales(c)

    for c in cmds: trouver_locales(c)

    taille_totale = abs(offset_courant)
    save_params = "\n".join(f"    mov {fmt_offset(contexte[p.children[1].value]['offset'])}, {regs[i]}" for i, p in enumerate(params))
    body = "".join(asm_commande(c, contexte) for c in cmds)
    code_ret, _ = asm_expression(ret_node.children[0], contexte)
    
    return f"""
{nom}:
    push rbp
    mov rbp, rsp
    sub rsp, {taille_totale}
{save_params}
{body}
{code_ret}
    mov rsp, rbp
    pop rbp
    ret
"""

def asm_main(ast, fonctions_code):
    typ, nom, vs_node, cmds, ret_node = get_components(ast)
    decls = asm_decls_vars(vs_node)
    vs = asm_vars(vs_node)
    contexte = {}
    
    offset_courant = -8
    if vs_node:
        for p in vs_node.children:
            nom_p = p.children[1].value
            contexte[nom_p] = {"type": "int", "offset": offset_courant}
            offset_courant -= 8

    def trouver_locales(cmd):
        nonlocal offset_courant
        if cmd.data in ("decl_init", "decl_commande"):
            d = cmd.children[0]
            typ_v, nom_v = d.children[0].value, d.children[1].value
            taille = structures_tailles.get(typ_v, 8)
            offset_courant -= taille
            contexte[nom_v] = {"type": typ_v, "offset": offset_courant}
        elif cmd.data in ("if_cmd", "while_cmd"):
            for c in cmd.children[1:]: trouver_locales(c)

    for c in cmds: trouver_locales(c)

    taille_totale_stack = abs(offset_courant)
    cmd_str = "".join(asm_commande(c, contexte) for c in cmds)
    code_ret, _ = asm_expression(ret_node.children[0], contexte)
    
    try:
        with open("squelette.asm", "r") as sf:
            template = sf.read()
    except FileNotFoundError:
        print("Erreur : Fichier 'squelette.asm' introuvable.")
        sys.exit(1)
        
    template = template.replace("DECL_VARS", decls)
    template = template.replace("FONCTIONS", fonctions_code)
    template = template.replace("STACK_SIZE", str(taille_totale_stack))
    template = template.replace("INIT_VARS", vs)
    template = template.replace("COMMAND", cmd_str)
    template = template.replace("RETURN", code_ret)
    return template

def asm_programme(ast):
    analyser_structures(ast)
    fonctions_code = "\n".join(asm_fonction(c) for c in ast.children if c.data == "fonction")
    for c in ast.children:
        if c.data == "main": return asm_main(c, fonctions_code)

if __name__ == "__main__":
    try:
        with open("source.c", "r") as f: code_source = f.read()
    except FileNotFoundError:
        print("Erreur : Fichier 'source.c' introuvable.")
        sys.exit(1)

    try:
        arbre = grammaire.parse(code_source)
    except Exception as e:
        print(f"Erreur syntaxe : {e}")
        sys.exit(1)

    print("==========================================")
    print("        PRETTY PRINTER DU CODE SOURCE     ")
    print("==========================================")
    print(pp_programme(arbre))
    
    try:
        code_final_asm = asm_programme(arbre)
        with open("result.asm", "w") as f: f.write(code_final_asm)
        print("==========================================")
        print(" ✅ COMPILATION REUSSIE -> result.asm genere")
        print("==========================================")
    except (TypeError, AttributeError, NameError) as e:
        print(f"Erreur compilation : {e}")
        sys.exit(1)