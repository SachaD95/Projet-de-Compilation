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
        #Token('IDENTIFIER', 'x')
        return ast.children[0].value

    if ast.data == "entier":
        # 1 2 
        return ast.children[0].value

    if ast.data == "binaire":
        gauche = pp_expression(ast.children[0])   
        op     = ast.children[1].value            
        droite = pp_expression(ast.children[2])  
        return f"{gauche} {op} {droite}"

    if ast.data == "index":
        # t[i] donc children[0] = t,  children[1] = i
        return f"{pp_expression(ast.children[0])}[{pp_expression(ast.children[1])}]"

    if ast.data == "row":
        # une ligne du tableau 2D : {1, 2, 3}
        elements = ", ".join(pp_expression(c) for c in ast.children)
        return "{" + elements + "}"

    if ast.data == "array2d_literal":
        # {{1,2},{3,4}} → chaque child est un nœud "row"
        lignes = ", ".join(pp_expression(r) for r in ast.children)
        return "{" + lignes + "}"

    if ast.data == "len":
        return f"len({pp_expression(ast.children[0])})"

    if ast.data == "array_literal":
        # {1, 2, 3} avec tous les children sont des expressions
        elements = ", ".join(pp_expression(c) for c in ast.children)
        return "{" + elements + "}"
    
    if ast.data == "struct_constructor":
        nom  = ast.children[0].value
        args = ", ".join(pp_expression(c) for c in ast.children[1:])
        return f"{nom}({args})"
    if ast.data == "field_access":
        # children[0] = expression gauche  ex: p  ou  l.A
        # children[1] = Token nom du champ ex: "x"
        # récursif : l.A.x → pp_expression(l.A) + ".x"
        return f"{pp_expression(ast.children[0])}.{ast.children[1].value}"


def asm_expression(ast) -> str:

    if ast.data == "variable":
        # En assembleur, on va chercher la valeur stockée à l'adresse de cette variable.
        nom_var = ast.children[0].value
        return f"    mov rax, [{nom_var}]\n"

    if ast.data == "entier":
        # En assembleur, on charge la valeur brute (immédiate) SANS crochets.
        valeur = ast.children[0].value
        return f"    mov rax, {valeur}\n"

    if ast.data == "binaire":
       
        code_gauche = asm_expression(ast.children[0])   
        op          = ast.children[1].value            
        code_droite = asm_expression(ast.children[2])  

    
        ops_assembleur = {'+': 'add', '-': 'sub', '*': 'imul'}
        inst_asm = ops_assembleur[op]

        # On assemble en utilisant la pile (Stack) pour ne pas perdre les calculs
        return f"""{code_gauche}\
    push rax
{code_droite}\
    mov rbx, rax
    pop rax
    {inst_asm} rax, rbx
"""
    if ast.data == "struct_constructor":
        code_assembleur = ""

        
        for c in ast.children[1:]:
            
            code_argument = asm_expression(c) #le code va déjà dans rax 
            
            
            code_assembleur += f"""{code_argument}    push rax
            """
     
        return code_assembleur

    if ast.data == "field_access" : 
        if ast.children[1].value=="x":
            return "    mov rax, [rsp + 0]\n"
        if ast.children[1].value=="y":
            return "    mov rax, [rsp + 8]\n"














def pp_lvalue(ast):

    if ast.data == "lvalue":
        return ast.children[0].value

    if ast.data == "index_lvalue":
        # t[i]
        return f"{pp_lvalue(ast.children[0])}[{pp_expression(ast.children[1])}]"

    if ast.data == "index2d_lvalue":
        # t[i][j]
        return f"{pp_lvalue(ast.children[0])}[{pp_expression(ast.children[1])}][{pp_expression(ast.children[2])}]"

    if ast.data == "field_lvalue":
        #A.x
        return f"{pp_lvalue(ast.children[0])}.{ast.children[1].value}"




    
def pp_commande(ast):

    if ast.data == "assignation":
        lhs_code = asm_lvalue(ast.children[0])   # adresse dans rdi
        rhs_code = asm_expression(ast.children[1])  # valeur dans rax
        return f"""{lhs_code}\
        push rdi
    {rhs_code}\
        pop rdi
        mov [rdi], rax
    """

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
        # children[0] = condition,  children[1] = commande du corps
        test = pp_expression(ast.children[0])
        corps = pp_commande(ast.children[1])
        return f"if ({test}) {{\n{corps}}}\n"

    if ast.data == "while":
        test = pp_expression(ast.children[0])
        corps = pp_commande(ast.children[1])
        return f"while ({test}) {{\n{corps}}}\n"

    if ast.data == "for":
        # for(int k = 0; k < len(t); k = k + 1)
        # children[0]=TYPE  children[1]=IDENTIFIER(var)
        # children[2]=init  children[3]=condition
        # children[4]=IDENTIFIER(lhs)  children[5]=IDENTIFIER(src)
        # children[6]=OPBIN  children[7]=expression(pas)
        # children[8]=commande(corps)
        typ      = ast.children[0].value   # "int"
        var      = ast.children[1].value   # "k"
        init     = pp_expression(ast.children[2])   # "0"
        cond     = pp_expression(ast.children[3])   # "k < len(t)"
        lhs_inc  = ast.children[4].value   # "k"
        src_inc  = ast.children[5].value   # "k"
        op_inc   = ast.children[6].value   # "+"
        val_inc  = pp_expression(ast.children[7])   # "1"
        corps    = pp_commande(ast.children[8])
        return f"for ({typ} {var} = {init}; {cond}; {lhs_inc} = {src_inc} {op_inc} {val_inc}) {{\n{corps}}}\n"


# Un compteur global simple pour générer des étiquettes uniques (ex: fin_0, fin_1...)
compteur_label = 0

def asm_commande(ast) -> str:
    global compteur_label

    if ast.data == "assignation":
        # Au lieu de fouiller dans les children à tâtons, on utilise ton pp_lvalue !
        # Si c'est juste "x", pp_lvalue(ast.children[0]) va renvoyer "x".
        lhs = pp_lvalue(ast.children[0])
        
        rhs = asm_expression(ast.children[1])
        return f"{rhs}    mov [{lhs}], rax\n"

    if ast.data == "pass":
        # 'nop' (No Operation) est la vraie instruction assembleur pour ne rien faire
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
        # Giga bug ici : tu appelais pp_commande au lieu de asm_commande !
        # De plus, la règle 'sequence' dans Lark contient une LISTE d'enfants (commande*), pas juste deux.
        # On boucle donc sur tous les enfants avec une compréhension de liste.
        return "".join(asm_commande(c) for c in ast.children)

    if ast.data == "while":
        # Même bug : tu appelais pp_expression et recrachais du faux texte C.
        # En assembleur, un while a besoin d'une étiquette de début et d'une étiquette de fin.
        label_debut = f"debut_while_{compteur_label}"
        label_fin = f"fin_while_{compteur_label}"
        compteur_label += 1
        
        cond = asm_expression(ast.children[0])
        cmd = asm_commande(ast.children[1])
        
        return f"""{label_debut}:
{cond}\
    cmp rax, 0
    jz {label_fin}
{cmd}\
    jmp {label_debut}
{label_fin}:
"""

    if ast.data == "if":
        # On génère un numéro d'étiquette unique
        cpt = compteur_label
        compteur_label += 1
        
        test = asm_expression(ast.children[0])
        cmd = asm_commande(ast.children[1])
        
        # Attention à la cohérence du nom : tu as écrit fin{cpt} puis fin_{cpt}
        return f"""{test}\
    cmp rax, 0
    jz fin_{cpt}
{cmd}fin_{cpt}:
"""

    return ""

def pp_vars(ast):
    # ast.children est la liste des decl
    # on reconstruit chaque decl et on les sépare par des virgules
    return ", ".join(pp_decl(d) for d in ast.children)

def pp_decl(ast):
    if ast.data == "decl_scalar":
        typ  = ast.children[0].value   # "int"
        nom  = ast.children[1].value   # "n"
        return f"{typ} {nom}"

    if ast.data == "decl_array":
        typ   = ast.children[0].value
        nom   = ast.children[1].value
        taille = pp_expression(ast.children[2])
        return f"{typ} {nom}[{taille}]"

    if ast.data == "decl_array2d":
        typ    = ast.children[0].value
        nom    = ast.children[1].value
        lignes = pp_expression(ast.children[2])
        cols   = pp_expression(ast.children[3])
        return f"{typ} {nom}[{lignes}][{cols}]"

    if ast.data == "decl_struct":
        typ  = ast.children[0].value   # "Point ou Livne "
        nom  = ast.children[1].value 
        return f"{typ} {nom}"


def pp_field_decl(ast):
    # field_decl_int   : int x
    # field_decl_struct : Point A
    typ = ast.children[0].value
    nom = ast.children[1].value
    return f"    {typ} {nom}"


def pp_struct_def(ast):
    champs = [pp_field_decl(c) for c in ast.children[:-1]]
    nom    = ast.children[-1].value
    corps  = ";\n".join(champs) + ";"
    return f"typedef struct {{\n{corps}\n}} {nom};\n"



# pour que le programme lance d'abord les définition de structures 

def pp_main(ast):
    #   children[0] = (les paramètres)
    #   children[1] = (le corps)
    #   children[2] = (la valeur de return)
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
    
    
    noeud_main = arbre.children[-1]
    
   
    noeud_commande = noeud_main.children[1]
    
    print("; --- CODE ASSEMBLEUR GÉNÉRÉ ---")
    print(asm_commande(noeud_commande))